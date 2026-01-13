from __future__ import annotations

import hashlib
import json
import re
import secrets
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from ..services.dispatch import CodexDispatch, CodexDispatchConfig
from ..services.memory_store import JsonMemoryStore, MemoryConfig as MemoryStoreConfig
from ..utils.fs import atomic_write_json, find_ancestor_with_child_dir, global_codex_path, project_codex_path
from ..utils.text import compact_text, truncate_tail_text


_PROJECT_LOCK = threading.RLock()
_MEMORY_LOCK = threading.Lock()

DEFAULT_PARALLEL = 3
DEFAULT_SUMMARY_LINES = 2
PATCH_PREVIEW_MAX_LINES = 40


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _parse_utc_iso(ts: str | None) -> datetime | None:
    if not ts or not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _job_stdout_mtime(dispatch: CodexDispatch, job_id: str) -> float | None:
    try:
        path = dispatch.jobs_dir / job_id / "stdout.jsonl"
        if not path.exists():
            return None
        return float(path.stat().st_mtime)
    except Exception:
        return None


def _projects_index_path() -> Path:
    return global_codex_path("projects-index.json")


def _load_projects_index() -> dict[str, str]:
    data = _read_json(_projects_index_path()) or {}
    out: dict[str, str] = {}
    for pid, path in data.items():
        if not pid or path is None:
            continue
        try:
            candidate = Path(str(path)).expanduser().resolve()
        except Exception:
            continue
        out[str(pid)] = str(candidate)
    return out


def _write_projects_index(index: dict[str, str]) -> None:
    atomic_write_json(_projects_index_path(), {k: str(v) for k, v in index.items()})


def _projects_root() -> Path:
    return project_codex_path("projects")


def _project_dir(project_id: str) -> Path:
    with _PROJECT_LOCK:
        indexed = _load_projects_index().get(str(project_id))
    if indexed:
        try:
            candidate = Path(str(indexed)).expanduser().resolve()
            if candidate.is_dir():
                return candidate
        except Exception:
            pass
    return _projects_root() / str(project_id)


def _project_file(project_id: str, name: str) -> Path:
    return _project_dir(project_id) / name


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        return data
    return None


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _new_project_id() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(3)
    return f"p_{ts}_{suffix}"


_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")


def _is_valid_task_id(task_id: str) -> bool:
    return bool(task_id) and bool(_TASK_ID_RE.match(str(task_id)))


def _normalize_lock_key(lock: str) -> str:
    raw = str(lock or "").strip()
    if not raw:
        return ""
    for ch in ("*", "?", "["):
        idx = raw.find(ch)
        if idx >= 0:
            raw = raw[:idx]
    return raw.rstrip("/").strip()


def _extract_lock_keys(locks: Any) -> list[str]:
    if not isinstance(locks, list):
        return []
    out: list[str] = []
    for v in locks:
        if v is None:
            continue
        key = _normalize_lock_key(str(v))
        if key and key not in out:
            out.append(key)
    return out


def _locks_conflict(a: list[str], b: list[str]) -> bool:
    if not a or not b:
        return False
    for x in a:
        for y in b:
            if not x or not y:
                continue
            if x == y or x.startswith(y + "/") or y.startswith(x + "/"):
                return True
    return False


def _dispatch_bucket_for_cwd(cwd: str | None) -> str:
    if not cwd:
        return "unknown"
    try:
        start = Path(cwd).expanduser().resolve()
    except Exception:
        return "unknown"
    root = find_ancestor_with_child_dir(start, ".codex") or find_ancestor_with_child_dir(start, ".git") or start
    base = re.sub(r"[^a-z0-9]+", "_", root.name.lower()).strip("_") or "project"
    suffix = hashlib.sha256(root.as_posix().encode("utf-8")).hexdigest()[:10]
    return f"{base}_{suffix}"


def _split_bucketed_job_id(job_id: str) -> tuple[str | None, str]:
    if not job_id:
        return (None, "")
    if "--" not in job_id:
        return (None, job_id)
    bucket, rest = job_id.split("--", 1)
    if not bucket or not rest:
        return (None, job_id)
    return (bucket, rest)


def _dispatch_for_job(job_id: str, *, dispatch_base_dir: Path) -> CodexDispatch:
    bucket, _ = _split_bucketed_job_id(job_id)
    if bucket:
        return CodexDispatch(CodexDispatchConfig(jobs_dir=dispatch_base_dir / bucket))
    try:
        for child in dispatch_base_dir.iterdir():
            if not child.is_dir():
                continue
            if (child / job_id / "meta.json").exists():
                return CodexDispatch(CodexDispatchConfig(jobs_dir=child))
    except FileNotFoundError:
        pass
    return CodexDispatch(CodexDispatchConfig(jobs_dir=dispatch_base_dir))


def _git_root_for_cwd(cwd: str | None) -> Path | None:
    if not cwd:
        return None
    try:
        start = Path(cwd).expanduser().resolve()
    except Exception:
        return None
    return find_ancestor_with_child_dir(start, ".git")


def _run_git(repo_dir: Path, args: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_dir), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return int(proc.returncode), str(proc.stdout or ""), str(proc.stderr or "")
    except FileNotFoundError:
        return 127, "", "git not found"
    except Exception as e:
        return 1, "", repr(e)


def _resolve_cwd_path(cwd: str | Path | None) -> Path:
    try:
        return Path(cwd).expanduser().resolve() if cwd else Path.cwd().resolve()
    except Exception:
        return Path.cwd().resolve()


def _repo_root_for_cwd(cwd: str | Path | None) -> Path:
    base = _resolve_cwd_path(cwd)
    return find_ancestor_with_child_dir(base, ".codex") or find_ancestor_with_child_dir(base, ".git") or base



def _project_paths(project_id: str) -> dict[str, Path]:
    base = _project_dir(project_id)
    return {
        "base": base,
        "plan": base / "plan.json",
        "state": base / "state.json",
        "project": base / "project.json",
        "prompts": base / "prompts",
        "reports": base / "reports",
        "worktrees": base / "worktrees",
        "patches": base / "patches",
        "input": base / "input.md",
    }


def _task_latest_patch_entry(tasks_state: dict[str, Any], task_id: str) -> tuple[str | None, str | None]:
    ts = tasks_state.get(task_id)
    if not isinstance(ts, dict):
        return None, None
    patch_path = ts.get("patch_path")
    worktree_dir = ts.get("worktree_dir")
    return (str(patch_path) if patch_path else None, str(worktree_dir) if worktree_dir else None)


def _patch_stat(repo_root: Path, patch_path: Path) -> str | None:
    code, out, _ = _run_git(repo_root, ["apply", "--stat", str(patch_path)])
    if code != 0:
        return None
    text = compact_text(out, max_len=1200)
    return text if text else None


def _patch_check(repo_root: Path, patch_path: Path) -> tuple[bool, str]:
    code, _, err = _run_git(repo_root, ["apply", "--check", str(patch_path)])
    if code == 0:
        return True, "ok"
    msg = compact_text(err or "patch check failed", max_len=240)
    return False, msg


def _patch_is_applied(repo_root: Path, patch_path: Path) -> bool:
    code, _, _ = _run_git(repo_root, ["apply", "--reverse", "--check", str(patch_path)])
    return code == 0


def _extract_candidate_pref_lines(text: str) -> list[str]:
    triggers = (
        "必须",
        "不要",
        "禁止",
        "永远",
        "默认",
        "优先",
        "尽量",
        "建议",
        "偏好",
        "日志",
        "summary",
        "context",
        "上下文",
        "job_id",
        "job_ref",
        "patch",
        "worktree",
        "并行",
        "锁",
        "冲突",
        "审查",
        "review",
        "选项",
        "options",
    )
    out: list[str] = []
    seen: set[str] = set()
    for raw in (text or "").splitlines():
        s = " ".join(str(raw).strip().split())
        if not s:
            continue
        if any(t in s for t in triggers):
            line = truncate_tail_text(compact_text(s, max_len=220), max_chars=160) or ""
            if line and line not in seen:
                seen.add(line)
                out.append(line)
    return out


def _classify_pref_line(line: str) -> str:
    lower = str(line).lower()
    if any(k in line for k in ("不要", "禁止", "never")) or "do not" in lower or "don't" in lower:
        return "constraints"
    if any(k in line for k in ("默认", "优先", "尽量", "建议", "偏好")) or "prefer" in lower or "default" in lower:
        return "preferences"
    return "notes"

def _looks_project_specific(line: str) -> bool:
    s = str(line)
    lower = s.lower()
    if "/" in s or "\\" in s:
        return True
    if any(ext in lower for ext in (".py", ".ts", ".tsx", ".js", ".yaml", ".yml", ".json", ".md")):
        return True
    if any(seg in lower for seg in ("apps/", "mcp-tools/", "charts/", ".codex/", ".git/")):
        return True
    return False


def _maybe_write_short_memory(
    *,
    memory_store: JsonMemoryStore | None,
    project_id: str,
    project: dict[str, Any],
    report_path: Path | None,
) -> None:
    if memory_store is None:
        return
    input_text = ""
    input_path = project.get("input_path")
    if input_path:
        try:
            input_text = Path(str(input_path)).read_text(encoding="utf-8")
        except Exception:
            input_text = ""
    report_text = ""
    if report_path:
        try:
            report_text = report_path.read_text(encoding="utf-8")
        except Exception:
            report_text = ""

    candidates = _extract_candidate_pref_lines(input_text + "\n" + report_text)
    if not candidates:
        return

    buckets: dict[str, list[str]] = {"constraints": [], "preferences": [], "notes": []}
    for line in candidates:
        if _looks_project_specific(line):
            continue
        buckets[_classify_pref_line(line)].append(line)
    summary_lines: list[str] = []
    for k in ("constraints", "preferences", "notes"):
        for line in buckets[k]:
            if line in summary_lines:
                continue
            summary_lines.append(line)
            if len(summary_lines) >= 5:
                break
        if len(summary_lines) >= 5:
            break
    if len(summary_lines) < 2:
        return

    content = "\n".join(f"- {ln}" for ln in summary_lines)
    content = truncate_tail_text(content, max_chars=240) or content

    key = "prefs/core"
    with _MEMORY_LOCK:
        last = None
        for it in reversed(memory_store.load_items()):
            if isinstance(it, dict) and it.get("key") == key:
                last = it
                break
        if last and _sha256(str(last.get("content") or "")) == _sha256(content):
            return
        tags = sorted({_classify_pref_line(ln) for ln in summary_lines} | {"auto"})
        memory_store.upsert_singleton(key=key, content=content, tags=tags, source=f"project_collect:{project_id}")


def _job_summary_path(meta: dict[str, Any]) -> Path | None:
    artifacts = meta.get("artifacts") if isinstance(meta.get("artifacts"), dict) else {}
    job_dir = artifacts.get("job_dir") if artifacts else None
    if not job_dir:
        return None
    try:
        return Path(str(job_dir)) / "summary.json"
    except Exception:
        return None


def _normalize_summary_lines(lines: list[Any] | None, *, max_items: int) -> list[str]:
    out: list[str] = []
    if max_items <= 0:
        return out
    seen: set[str] = set()
    for raw in lines or []:
        if raw is None:
            continue
        text = raw if isinstance(raw, str) else str(raw)
        text = truncate_tail_text(compact_text(text, max_len=200), max_chars=160) or ""
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    if len(out) > max_items:
        out = out[-max_items:]
    return out


def _extract_paths(ev: dict[str, Any]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    def _add(val: Any) -> None:
        if val is None:
            return
        candidate: str | None = None
        if isinstance(val, str):
            candidate = val
        elif isinstance(val, dict):
            for key in ("path", "file", "name"):
                if val.get(key):
                    candidate = str(val.get(key))
                    break
        if candidate:
            c = candidate.strip()
            if c and c not in seen:
                seen.add(c)
                ordered.append(c)

    def _walk(val: Any) -> None:
        if val is None:
            return
        if isinstance(val, list):
            for it in val:
                _walk(it)
            return
        _add(val)

    for key in ("paths", "files", "file_changes", "items"):
        if key in ev:
            _walk(ev.get(key))
    for key in ("path", "file"):
        if key in ev:
            _add(ev.get(key))
    return ordered


_VERIFY_HINTS = ("compileall", "py_compile", "pytest", "ruff", "mypy", "tsc", "go test", "cargo test")


def _summarize_event(ev: Any) -> list[str]:
    if not isinstance(ev, dict):
        return []
    etype = ev.get("type")
    if etype == "file_change":
        paths = _extract_paths(ev)
        if not paths:
            return []
        preview = paths[:3]
        extra = max(0, len(paths) - len(preview))
        joined = ", ".join(preview)
        if extra:
            joined = f"{joined} +{extra}"
        return [f"Updated: {joined}"]

    if etype == "command_execution":
        cmd = ev.get("command") or ev.get("cmd") or ev.get("command_line") or ev.get("argv") or ev.get("args")
        cmd_text: str | None = None
        if isinstance(cmd, list):
            cmd_text = " ".join(str(p) for p in cmd)
        elif isinstance(cmd, dict):
            argv = cmd.get("argv") or cmd.get("args")
            if isinstance(argv, list):
                cmd_text = " ".join(str(p) for p in argv)
            else:
                cmd_text = str(cmd.get("raw") or cmd.get("cmd") or "")
        elif cmd is not None:
            cmd_text = str(cmd)
        if not cmd_text:
            return []
        lowered = cmd_text.lower()
        if not any(h in lowered for h in _VERIFY_HINTS):
            return []
        exit_code = ev.get("exit_code", ev.get("code"))
        exit_str = str(exit_code) if exit_code is not None else "unknown"
        line = f"Verify: {cmd_text} (exit={exit_str})"
        if exit_code not in (0, "0", None):
            snippet = ev.get("aggregated_output") or ev.get("stderr") or ev.get("output") or ""
            snippet_text = truncate_tail_text(compact_text(str(snippet), max_len=200), max_chars=200)
            if snippet_text:
                line = f"{line} | {snippet_text}"
        return [line]

    return []


def _refresh_job_summary(
    dispatch: CodexDispatch,
    job_id: str,
    *,
    current_cursor: int,
    current_lines: list[str],
    max_items: int,
) -> tuple[int, list[str]]:
    cursor = max(0, int(current_cursor or 0))
    summary = list(current_lines or [])
    res = dispatch.events(job_id=job_id, cursor=cursor, max_bytes=12000, max_items=120)
    if not res.get("found"):
        return cursor, summary
    events = res.get("events") if isinstance(res.get("events"), list) else []
    for ev in events:
        for line in _summarize_event(ev):
            if not line:
                continue
            compacted = truncate_tail_text(compact_text(str(line), max_len=200), max_chars=160)
            if compacted and compacted not in summary:
                summary.append(compacted)
    cursor = int(res.get("cursor", cursor))
    if len(summary) > max_items:
        summary = summary[-max_items:]
    return cursor, summary


def _load_or_update_summary(
    dispatch: CodexDispatch,
    *,
    job_id: str,
    meta: dict[str, Any],
    state_cursor: int,
    state_lines: list[str],
    max_items: int,
) -> tuple[int, list[str]]:
    cursor = int(state_cursor or 0)
    lines = list(state_lines or [])

    spath = _job_summary_path(meta)
    if spath:
        snapshot = _read_json(spath)
        if snapshot:
            try:
                disk_cursor = int(snapshot.get("cursor", 0) or 0)
            except Exception:
                disk_cursor = 0
            disk_lines = snapshot.get("summary") if isinstance(snapshot.get("summary"), list) else []
            merged = _normalize_summary_lines(disk_lines, max_items=max_items)
            if disk_cursor > cursor:
                cursor = disk_cursor
            for line in merged:
                if line not in lines:
                    lines.append(line)
            if len(lines) > max_items:
                lines = lines[-max_items:]

    new_cursor, new_lines = _refresh_job_summary(
        dispatch,
        job_id,
        current_cursor=cursor,
        current_lines=lines,
        max_items=max_items,
    )

    if spath:
        try:
            atomic_write_json(spath, {"cursor": int(new_cursor), "summary": _normalize_summary_lines(new_lines, max_items=max_items)})
        except Exception:
            pass
    return new_cursor, new_lines


def register_project_tools(
    mcp: FastMCP,
    *,
    dispatch_base_dir: Path,
    dispatch_enabled_default: bool,
    memory_enabled_default: bool,
    memory_global_scope: bool,
    resolved_memory_path: Path,
    memory_max_items: int,
    memory_max_bytes: int,
    get_verbosity: Callable[[dict[str, Any] | None], str],
    effective_enabled: Callable[..., bool],
) -> None:
    def _memory_store_for_project(project: dict[str, Any]) -> JsonMemoryStore | None:
        if not memory_enabled_default:
            return None
        try:
            if memory_global_scope:
                path = Path(resolved_memory_path)
            else:
                cwd = project.get("cwd")
                root = find_ancestor_with_child_dir(Path(str(cwd)).resolve(), ".codex") if cwd else None
                if not root and cwd:
                    root = find_ancestor_with_child_dir(Path(str(cwd)).resolve(), ".git")
                if not root and cwd:
                    root = Path(str(cwd)).resolve()
                base = (root / ".codex") if root else Path.cwd().resolve() / ".codex"
                path = base / "memory.json"
            return JsonMemoryStore(
                MemoryStoreConfig(
                    path=path if path else global_codex_path("memory.json"),
                    max_items=int(memory_max_items or 0),
                    max_bytes=int(memory_max_bytes or 0),
                )
            )
        except Exception:
            return None

    def _load_bundle(project_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
        p = _read_json(_project_file(project_id, "project.json"))
        plan = _read_json(_project_file(project_id, "plan.json"))
        state = _read_json(_project_file(project_id, "state.json"))
        return p, plan, state

    def _ensure_state(project_id: str, plan: dict[str, Any] | None) -> dict[str, Any]:
        state_path = _project_file(project_id, "state.json")
        state = _read_json(state_path) or {"version": 1, "tasks": {}, "rounds": []}
        tasks_state = state.get("tasks")
        if not isinstance(tasks_state, dict):
            tasks_state = {}
            state["tasks"] = tasks_state
        for t in (plan.get("tasks") if isinstance(plan, dict) else []) or []:
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            if not _is_valid_task_id(tid):
                continue
            if tid not in tasks_state:
                tasks_state[tid] = {"state": "pending", "attempts": 0, "summary": [], "summary_cursor": 0}
        return state

    def _save_state(project_id: str, state: dict[str, Any]) -> None:
        atomic_write_json(_project_file(project_id, "state.json"), state)

    def _update_task_timing(task_state: dict[str, Any], dispatch: CodexDispatch, *, job_id: str) -> None:
        started = _parse_utc_iso(str(task_state.get("started_at") or "")) or _parse_utc_iso(str(task_state.get("created_at") or ""))
        now = datetime.now(timezone.utc)
        if started:
            task_state["running_for_sec"] = int(max(0.0, (now - started).total_seconds()))

        mtime = _job_stdout_mtime(dispatch, job_id)
        if mtime is None:
            return
        last_output = datetime.fromtimestamp(mtime, tz=timezone.utc)
        task_state["last_output_at"] = last_output.isoformat()
        task_state["last_output_sec_ago"] = int(max(0.0, (now - last_output).total_seconds()))
        st = str(task_state.get("state") or "")
        if st == "running":
            task_state["stalled_suspected"] = bool(task_state.get("last_output_sec_ago", 0) > 120)
        else:
            task_state.pop("stalled_suspected", None)

    def _refresh_task_from_dispatch(task_state: dict[str, Any], *, job_id: str) -> None:
        dispatch = _dispatch_for_job(job_id, dispatch_base_dir=dispatch_base_dir)
        res = dispatch.status(job_id=job_id, stdout_tail_bytes=0, stderr_tail_bytes=0, include_last_message=False, compact=True, include_artifacts=True)
        meta = res.get("meta") if isinstance(res, dict) else None
        if not isinstance(meta, dict):
            task_state["state"] = "unknown"
            return
        status = meta.get("status") or "unknown"
        task_state["state"] = str(status)
        if meta.get("finished_at"):
            task_state["finished_at"] = meta.get("finished_at")
        if meta.get("exit_code") is not None:
            task_state["exit_code"] = meta.get("exit_code")
        _update_task_timing(task_state, dispatch, job_id=job_id)
        cursor, lines = _load_or_update_summary(
            dispatch,
            job_id=job_id,
            meta=meta,
            state_cursor=int(task_state.get("summary_cursor") or 0),
            state_lines=task_state.get("summary") if isinstance(task_state.get("summary"), list) else [],
            max_items=30,
        )
        task_state["summary_cursor"] = int(cursor)
        task_state["summary"] = lines

    def _ensure_patch_generated(task_state: dict[str, Any]) -> None:
        state_val = str(task_state.get("state") or "")
        if state_val not in {"completed", "failed", "canceled"}:
            return
        patch_path = task_state.get("patch_path")
        if not patch_path:
            return
        if Path(str(patch_path)).exists():
            return
        worktree_dir = task_state.get("worktree_dir")
        if not worktree_dir:
            return
        wt = Path(str(worktree_dir))
        if not wt.exists():
            return
        code, out, err = _run_git(wt, ["diff"])
        if code != 0:
            task_state["patch_error"] = compact_text(err or "patch generation failed", max_len=160)
            return
        Path(str(patch_path)).parent.mkdir(parents=True, exist_ok=True)
        Path(str(patch_path)).write_text(out, encoding="utf-8")
        task_state["patch_generated_at"] = _utc_now_iso()
        code2, out2, _ = _run_git(wt, ["status", "--porcelain"])
        if code2 == 0:
            files = [ln[3:] for ln in out2.splitlines() if len(ln) > 3]
            task_state["changed_files"] = files[:50]

    @mcp.tool(
        name="project_create",
        description="Create a lightweight project record for multi-task orchestration (compact output, persisted under .codex/projects/<project_id>/).",
    )
    def project_create(
        *,
        title: str | None = None,
        cwd: str | None = None,
        input: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project_id = _new_project_id()
        resolved_cwd = _resolve_cwd_path(cwd)
        repo_root = _repo_root_for_cwd(resolved_cwd).resolve()
        codex_root = repo_root / ".codex"
        project_root = codex_root / "projects"
        project_path = project_root / project_id
        input_path: Path | None = None
        input_text: str | None = None
        payload: dict[str, Any] = {
            "id": project_id,
            "created_at": _utc_now_iso(),
            "title": (title or "").strip() or "Untitled",
            "cwd": str(resolved_cwd),
        }
        if input:
            input_path = project_path / "input.md"
            input_text = str(input).rstrip() + "\n"
            if len(input_text) > 8000:
                input_text = input_text[:8000] + "\n"
            payload["input_sha256"] = _sha256(str(input))
            payload["input_path"] = str(input_path)
        with _PROJECT_LOCK:
            codex_root.mkdir(parents=True, exist_ok=True)
            project_path.mkdir(parents=True, exist_ok=True)
            if input_path and input_text is not None:
                input_path.write_text(input_text, encoding="utf-8")
            atomic_write_json(project_path / "project.json", payload)
            atomic_write_json(project_path / "plan.json", {"version": 1, "tasks": []})
            atomic_write_json(project_path / "state.json", {"version": 1, "tasks": {}, "rounds": []})
            index = _load_projects_index()
            index[project_id] = str(project_path.resolve())
            _write_projects_index(index)
        return {"project_id": project_id, "message": "created"}

    @mcp.tool(
        name="project_plan_set",
        description="Persist a task plan for a project (tasks with prompt/prompt_path, deps, acceptance).",
    )
    def project_plan_set(
        *,
        project_id: str,
        plan: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not project_id:
            return {"state": "error", "code": "E_PROJECT_ID_REQUIRED", "message": "project_id required"}
        project = _read_json(_project_file(project_id, "project.json"))
        if not project:
            return {"state": "not_found", "message": "project not found"}
        version = int(plan.get("version") or 0) if isinstance(plan, dict) else 0
        if version != 1:
            return {"state": "error", "code": "E_UNSUPPORTED_PLAN_VERSION", "message": "plan.version must be 1"}

        tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else None
        if tasks is None:
            return {"state": "error", "code": "E_TASKS_REQUIRED", "message": "plan.tasks must be a list"}

        project_cwd = str(project.get("cwd") or "")
        prompts_dir = _project_dir(project_id) / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        normalized_tasks: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for raw in tasks:
            if not isinstance(raw, dict):
                continue
            tid = str(raw.get("id") or "").strip()
            if not _is_valid_task_id(tid):
                return {"state": "error", "code": "E_TASK_ID_INVALID", "message": "invalid task id"}
            if tid in seen_ids:
                return {"state": "error", "code": "E_TASK_ID_DUP", "message": "duplicate task id"}
            seen_ids.add(tid)

            title = str(raw.get("title") or "").strip() or tid
            prompt = raw.get("prompt")
            prompt_path = raw.get("prompt_path")
            if prompt and not prompt_path:
                ppath = prompts_dir / f"{tid}.md"
                ppath.write_text(str(prompt).rstrip() + "\n", encoding="utf-8")
                prompt_path = str(ppath)
            if not prompt_path:
                return {"state": "error", "code": "E_PROMPT_REQUIRED", "message": "task prompt or prompt_path required"}

            deps = raw.get("depends_on")
            depends_on = [str(x) for x in deps] if isinstance(deps, list) else []
            acceptance_val = raw.get("acceptance")
            acceptance = [str(x) for x in acceptance_val] if isinstance(acceptance_val, list) else []
            locks_val = raw.get("locks")
            locks = [str(x) for x in locks_val] if isinstance(locks_val, list) else []
            locks = [s.strip() for s in locks if s and str(s).strip()]
            if len(locks) > 20:
                return {"state": "error", "code": "E_LOCKS_TOO_MANY", "message": "locks too many"}

            normalized: dict[str, Any] = {
                "id": tid,
                "title": title,
                "prompt_path": str(prompt_path),
            }
            normalized["cwd"] = str(raw.get("cwd") or project_cwd).strip() or project_cwd
            for key in ("model", "sandbox", "approval_policy"):
                if raw.get(key) is not None:
                    normalized[key] = raw.get(key)
            if raw.get("extra_config") is not None:
                normalized["extra_config"] = raw.get("extra_config")
            if raw.get("env") is not None:
                normalized["env"] = raw.get("env")
            if depends_on:
                normalized["depends_on"] = depends_on
            if acceptance:
                normalized["acceptance"] = acceptance
            if locks:
                normalized["locks"] = locks
            normalized_tasks.append(normalized)

        # Validate dependency ids exist
        all_ids = {t["id"] for t in normalized_tasks}
        for t in normalized_tasks:
            for dep in t.get("depends_on", []) or []:
                if dep not in all_ids:
                    return {"state": "error", "code": "E_DEP_NOT_FOUND", "message": "depends_on contains unknown task id"}

        normalized_plan = {"version": 1, "tasks": normalized_tasks}
        with _PROJECT_LOCK:
            atomic_write_json(_project_file(project_id, "plan.json"), normalized_plan)
            state = _ensure_state(project_id, normalized_plan)
            _save_state(project_id, state)
        return {"ok": True, "task_count": len(normalized_tasks)}

    @mcp.tool(
        name="project_run",
        description="Start eligible tasks in parallel using codex dispatch (compact output by default).",
    )
    def project_run(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_dispatch", default=dispatch_enabled_default)
        if not enabled:
            return {"state": "disabled"}

        include_handles = bool(options.get("include_handles")) if options else False
        parallel = DEFAULT_PARALLEL

        project, plan, state = _load_bundle(project_id)
        if not project or not plan:
            return {"state": "not_found", "message": "project not found"}
        state = state or {"version": 1, "tasks": {}, "rounds": []}
        state = _ensure_state(project_id, plan)
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}

        plan_tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else []
        plan_by_id: dict[str, dict[str, Any]] = {}
        for t in plan_tasks:
            if isinstance(t, dict) and t.get("id"):
                plan_by_id[str(t.get("id"))] = t

        # Refresh running tasks before scheduling new ones
        running = 0
        active_lock_keys: list[str] = []
        for tid, ts in list(tasks_state.items()):
            if not isinstance(ts, dict):
                continue
            if str(ts.get("state")) == "running" and ts.get("job_id"):
                _refresh_task_from_dispatch(ts, job_id=str(ts.get("job_id")))
            if str(ts.get("state")) == "running":
                running += 1
                pt = plan_by_id.get(str(tid)) or {}
                active_lock_keys.extend(_extract_lock_keys(pt.get("locks")))
        # De-dupe
        active_lock_keys = [k for i, k in enumerate(active_lock_keys) if k and k not in active_lock_keys[:i]]

        available = max(0, parallel - running)
        started: list[dict[str, Any]] = []
        skipped: list[str] = []

        for t in plan_tasks:
            if available <= 0:
                break
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            ts = tasks_state.get(tid) if isinstance(tasks_state.get(tid), dict) else None
            if not ts:
                continue
            if str(ts.get("state")) in {"running", "completed"}:
                skipped.append(tid)
                continue
            deps = t.get("depends_on") if isinstance(t.get("depends_on"), list) else []
            blocked = False
            for dep in deps:
                dep_state = tasks_state.get(str(dep))
                if not isinstance(dep_state, dict) or str(dep_state.get("state")) != "completed":
                    blocked = True
                    break
            if blocked:
                skipped.append(tid)
                continue

            task_lock_keys = _extract_lock_keys(t.get("locks"))
            if _locks_conflict(task_lock_keys, active_lock_keys):
                skipped.append(tid)
                continue

            prompt_path = str(t.get("prompt_path") or "")
            try:
                prompt_text = Path(prompt_path).expanduser().read_text(encoding="utf-8")
            except FileNotFoundError:
                ts["state"] = "failed"
                ts["last_error"] = "prompt_path not found"
                skipped.append(tid)
                continue

            task_cwd = str(t.get("cwd") or project.get("cwd") or "").strip() or str(Path.cwd().resolve())
            repo_root = _git_root_for_cwd(task_cwd)
            if not repo_root:
                ts["state"] = "failed"
                ts["last_error"] = "git repo not found (required for patch-only)"
                skipped.append(tid)
                continue

            attempt_num = int(ts.get("attempts") or 0) + 1
            worktrees_dir = _project_dir(project_id) / "worktrees"
            wt_path = worktrees_dir / f"{tid}_a{attempt_num}"
            patches_dir = _project_dir(project_id) / "patches"
            patch_path = patches_dir / f"{tid}_a{attempt_num}.patch"

            worktrees_dir.mkdir(parents=True, exist_ok=True)
            patches_dir.mkdir(parents=True, exist_ok=True)
            if wt_path.exists():
                ts["state"] = "failed"
                ts["last_error"] = "worktree path already exists"
                skipped.append(tid)
                continue

            code, _, err = _run_git(repo_root, ["worktree", "add", "--detach", str(wt_path), "HEAD"])
            if code != 0:
                ts["state"] = "failed"
                ts["last_error"] = compact_text(err or "git worktree add failed", max_len=180)
                skipped.append(tid)
                continue

            bucket = _dispatch_bucket_for_cwd(str(repo_root))
            dispatch = CodexDispatch(CodexDispatchConfig(jobs_dir=dispatch_base_dir / bucket))

            res = dispatch.start(
                prompt=prompt_text,
                model=str(t.get("model")) if t.get("model") is not None else None,
                cwd=str(wt_path),
                sandbox=str(t.get("sandbox")) if t.get("sandbox") is not None else "workspace-write",
                approval_policy=str(t.get("approval_policy")) if t.get("approval_policy") is not None else "never",
                extra_config=list(t.get("extra_config")) if isinstance(t.get("extra_config"), list) else None,
                env=dict(t.get("env")) if isinstance(t.get("env"), dict) else None,
                job_id_prefix=bucket,
            )
            job_id = str(res.get("job_id") or "")
            ts["state"] = "running"
            ts["job_id"] = job_id
            ts["attempts"] = attempt_num
            ts["repo_root"] = str(repo_root)
            ts["worktree_dir"] = str(wt_path)
            ts["patch_path"] = str(patch_path)
            ts["started_at"] = _utc_now_iso()
            ts.pop("finished_at", None)
            ts.pop("exit_code", None)
            ts.pop("last_error", None)
            started_entry: dict[str, Any] = {"id": tid}
            if include_handles:
                started_entry["job_id"] = job_id
            started.append(started_entry)
            active_lock_keys.extend(task_lock_keys)
            active_lock_keys = [k for i, k in enumerate(active_lock_keys) if k and k not in active_lock_keys[:i]]
            available -= 1

        rounds = state.get("rounds")
        if not isinstance(rounds, list):
            rounds = []
            state["rounds"] = rounds
        rounds.append(
            {
                "started_at": _utc_now_iso(),
                "started": [e.get("id") for e in started],
                "parallel": parallel,
            }
        )
        all_job_ids = state.get("job_ids")
        if not isinstance(all_job_ids, list):
            all_job_ids = []
            state["job_ids"] = all_job_ids
        for e in started:
            if not isinstance(e, dict):
                continue
            tid = e.get("id")
            ts = tasks_state.get(str(tid)) if isinstance(tasks_state.get(str(tid)), dict) else None
            jid = ts.get("job_id") if isinstance(ts, dict) else None
            if jid and jid not in all_job_ids:
                all_job_ids.append(jid)
        with _PROJECT_LOCK:
            _save_state(project_id, state)

        counts = {
            "started": len(started),
            "skipped": len(skipped),
            "running": running + len(started),
        }
        payload: dict[str, Any] = {"state": "ok", "counts": counts, "started": started, "skipped": skipped}
        if include_handles is not True:
            # Ensure no accidental job ids leak
            for entry in payload.get("started", []):
                if isinstance(entry, dict):
                    entry.pop("job_id", None)
        return payload

    @mcp.tool(
        name="project_status",
        description="Get compact status for a project and its tasks (summary-first, minimal output).",
    )
    def project_status(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        include_handles = bool(options.get("include_handles")) if options else False
        summary_lines = DEFAULT_SUMMARY_LINES
        include_timing = True if options is None else bool(options.get("include_timing", True))

        project, plan, state = _load_bundle(project_id)
        if not project or not plan:
            return {"state": "not_found", "message": "project not found"}
        state = state or {"version": 1, "tasks": {}, "rounds": []}
        state = _ensure_state(project_id, plan)
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}

        completed = failed = running = pending = unknown = 0
        tasks_out: list[dict[str, Any]] = []
        for t in (plan.get("tasks") if isinstance(plan, dict) else []) or []:
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            ts = tasks_state.get(tid)
            if not isinstance(ts, dict):
                ts = {"state": "pending", "attempts": 0, "summary": [], "summary_cursor": 0}
                tasks_state[tid] = ts

            job_id = ts.get("job_id")
            needs_patch = False
            if ts.get("patch_path") and not Path(str(ts.get("patch_path"))).exists():
                needs_patch = True
            if job_id and (str(ts.get("state")) in {"running"} or needs_patch):
                try:
                    _refresh_task_from_dispatch(ts, job_id=str(job_id))
                except Exception:
                    ts["state"] = "unknown"

            st = str(ts.get("state") or "unknown")
            if st == "completed":
                completed += 1
            elif st == "failed":
                failed += 1
            elif st == "running":
                running += 1
            elif st in {"pending"}:
                pending += 1
            else:
                unknown += 1

            entry: dict[str, Any] = {"id": tid, "state": st}
            summary_list = ts.get("summary") if isinstance(ts.get("summary"), list) else []
            trimmed = summary_list[-summary_lines:] if summary_lines > 0 else []
            if trimmed:
                entry["summary"] = trimmed
            if include_handles and job_id:
                entry["job_id"] = str(job_id)
            if include_timing:
                for key in ("running_for_sec", "last_output_at", "last_output_sec_ago", "stalled_suspected"):
                    if ts.get(key) is not None:
                        entry[key] = ts.get(key)
            tasks_out.append(entry)

        with _PROJECT_LOCK:
            _save_state(project_id, state)

        counts = {
            "total": len(tasks_out),
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "unknown": unknown,
        }
        payload: dict[str, Any] = {"state": "ok", "counts": counts, "tasks": tasks_out}
        if not include_handles:
            for entry in payload.get("tasks", []):
                if isinstance(entry, dict):
                    entry.pop("job_id", None)
        return payload

    @mcp.tool(
        name="project_collect",
        description="Generate a compact per-round report for a project from current task states and summaries.",
    )
    def project_collect(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        summary_lines = DEFAULT_SUMMARY_LINES

        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}

        # Refresh before reporting
        _ = project_status(project_id=project_id, options={"include_handles": False})
        state = _read_json(_project_file(project_id, "state.json")) or state

        reports_dir = _project_dir(project_id) / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        existing = sorted(reports_dir.glob("round_*.md"))
        n = 1
        if existing:
            last = existing[-1].stem
            try:
                n = int(last.split("_", 1)[1]) + 1
            except Exception:
                n = len(existing) + 1

        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        lines: list[str] = []
        lines.append(f"# Project Report: {project.get('title')}")
        lines.append(f"- project_id: {project_id}")
        lines.append(f"- generated_at: {_utc_now_iso()}")
        lines.append("")
        lines.append("## Tasks")

        short_summary: list[str] = []
        for t in (plan.get("tasks") if isinstance(plan, dict) else []) or []:
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            ts = tasks_state.get(tid) if isinstance(tasks_state.get(tid), dict) else {}
            st = str(ts.get("state") or "unknown")
            title = str(t.get("title") or tid)
            lines.append(f"- [{st}] {tid}: {title}")
            summary_list = ts.get("summary") if isinstance(ts.get("summary"), list) else []
            trimmed = summary_list[-summary_lines:] if summary_lines > 0 else []
            for s in trimmed:
                lines.append(f"  - {s}")
            if st in {"failed", "unknown"} and ts.get("last_error"):
                lines.append(f"  - error: {truncate_tail_text(compact_text(str(ts.get('last_error')), max_len=240), max_chars=240)}")
            if ts.get("patch_path"):
                lines.append(f"  - patch: {ts.get('patch_path')}")
            changed_files = ts.get("changed_files") if isinstance(ts.get("changed_files"), list) else []
            if changed_files:
                preview = changed_files[:6]
                extra = max(0, len(changed_files) - len(preview))
                joined = ", ".join(str(p) for p in preview)
                if extra:
                    joined = f"{joined} +{extra}"
                lines.append(f"  - files: {joined}")

            # For tool return summary (<= ~10 lines)
            if len(short_summary) < 9:
                if trimmed:
                    short_summary.append(f"{tid}: {trimmed[-1]}")
                else:
                    short_summary.append(f"{tid}: {st}")

        report_path = reports_dir / f"round_{n}.md"
        report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        try:
            _maybe_write_short_memory(
                memory_store=_memory_store_for_project(project),
                project_id=project_id,
                project=project,
                report_path=report_path,
            )
        except Exception:
            pass
        return {"report_path": str(report_path), "summary": short_summary}

    @mcp.tool(
        name="project_patch_list",
        description="List latest patch artifacts for tasks (patch-only mode). Compact output; no job handles.",
    )
    def project_patch_list(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        repo_root = _git_root_for_cwd(str(project.get("cwd") or "")) or Path(str(project.get("cwd") or "")).resolve()
        patches: list[dict[str, Any]] = []
        for t in (plan.get("tasks") if isinstance(plan, dict) else []) or []:
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            ts = tasks_state.get(tid) if isinstance(tasks_state.get(tid), dict) else None
            if isinstance(ts, dict):
                _ensure_patch_generated(ts)
            patch_path, _ = _task_latest_patch_entry(tasks_state, tid)
            if not patch_path:
                continue
            p = Path(patch_path)
            if not p.exists():
                continue
            entry: dict[str, Any] = {"id": tid, "patch_path": patch_path}
            if _patch_is_applied(repo_root, p):
                entry["state"] = "applied"
            else:
                ok, msg = _patch_check(repo_root, p)
                entry["state"] = "ready" if ok else "blocked"
                if not ok:
                    entry["message"] = msg
            patches.append(entry)
        return {"state": "ok", "patches": patches}

    @mcp.tool(
        name="project_patch_view",
        description="Show a compact patch preview (stat + first lines) for a task patch.",
    )
    def project_patch_view(
        *,
        project_id: str,
        task_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        ts = tasks_state.get(str(task_id)) if isinstance(tasks_state.get(str(task_id)), dict) else None
        if isinstance(ts, dict):
            _ensure_patch_generated(ts)
        patch_path, _ = _task_latest_patch_entry(tasks_state, str(task_id))
        if not patch_path:
            return {"state": "not_found", "message": "patch not found"}
        p = Path(patch_path)
        if not p.exists():
            return {"state": "not_found", "message": "patch file missing"}
        repo_root = _git_root_for_cwd(str(project.get("cwd") or "")) or Path(str(project.get("cwd") or "")).resolve()
        stat = _patch_stat(repo_root, p)
        try:
            preview = p.read_text(encoding="utf-8")
        except Exception:
            preview = ""
        preview_lines = preview.splitlines()
        head = "\n".join(preview_lines[:PATCH_PREVIEW_MAX_LINES])
        head = truncate_tail_text(head, max_chars=2000) or head
        out: dict[str, Any] = {"state": "ok", "patch_path": patch_path}
        if stat:
            out["stat"] = stat
        if head:
            out["preview"] = head
        if _patch_is_applied(repo_root, p):
            out["patch_state"] = "applied"
        else:
            ok, msg = _patch_check(repo_root, p)
            out["patch_state"] = "ready" if ok else "blocked"
            if not ok:
                out["message"] = msg
        return out

    @mcp.tool(
        name="project_patch_apply",
        description="Apply a task patch to the main repo (runs git apply --check first).",
    )
    def project_patch_apply(
        *,
        project_id: str,
        task_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        ts = tasks_state.get(str(task_id)) if isinstance(tasks_state.get(str(task_id)), dict) else None
        if isinstance(ts, dict):
            _ensure_patch_generated(ts)
        patch_path, _ = _task_latest_patch_entry(tasks_state, str(task_id))
        if not patch_path:
            return {"state": "not_found", "message": "patch not found"}
        p = Path(patch_path)
        if not p.exists():
            return {"state": "not_found", "message": "patch file missing"}
        repo_root = _git_root_for_cwd(str(project.get("cwd") or "")) or Path(str(project.get("cwd") or "")).resolve()
        if _patch_is_applied(repo_root, p):
            return {"state": "ok", "message": "already applied"}
        ok, msg = _patch_check(repo_root, p)
        if not ok:
            return {"state": "error", "code": "E_PATCH_CHECK_FAILED", "message": msg}
        code, _, err = _run_git(repo_root, ["apply", str(p)])
        if code != 0:
            return {"state": "error", "code": "E_PATCH_APPLY_FAILED", "message": compact_text(err or "patch apply failed", max_len=240)}

        # Mark state as applied (best-effort)
        ts = tasks_state.get(str(task_id))
        if isinstance(ts, dict):
            ts["patch_applied_at"] = _utc_now_iso()
        with _PROJECT_LOCK:
            _save_state(project_id, state)
        return {"state": "ok", "message": "applied"}

    @mcp.tool(
        name="project_patch_apply_all",
        description="Apply all available task patches to the main repo (stop on first failure).",
    )
    def project_patch_apply_all(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        repo_root = _git_root_for_cwd(str(project.get("cwd") or ""))
        if not repo_root:
            return {"state": "error", "code": "E_GIT_REPO_NOT_FOUND", "message": "git repo not found"}

        applied: list[str] = []
        skipped: list[str] = []
        for t in (plan.get("tasks") if isinstance(plan, dict) else []) or []:
            if not isinstance(t, dict):
                continue
            tid = str(t.get("id") or "")
            ts = tasks_state.get(tid) if isinstance(tasks_state.get(tid), dict) else None
            if isinstance(ts, dict):
                _ensure_patch_generated(ts)
            patch_path, _ = _task_latest_patch_entry(tasks_state, tid)
            if not patch_path:
                continue
            p = Path(patch_path)
            if not p.exists():
                continue
            if _patch_is_applied(repo_root, p):
                skipped.append(tid)
                continue
            ok, msg = _patch_check(repo_root, p)
            if not ok:
                return {"state": "error", "code": "E_PATCH_CHECK_FAILED", "task_id": tid, "message": msg, "applied": applied}
            code, _, err = _run_git(repo_root, ["apply", str(p)])
            if code != 0:
                return {
                    "state": "error",
                    "code": "E_PATCH_APPLY_FAILED",
                    "task_id": tid,
                    "message": compact_text(err or "patch apply failed", max_len=240),
                    "applied": applied,
                }
            ts = tasks_state.get(tid)
            if isinstance(ts, dict):
                ts["patch_applied_at"] = _utc_now_iso()
            applied.append(tid)

        with _PROJECT_LOCK:
            _save_state(project_id, state)
        payload: dict[str, Any] = {"state": "ok", "applied": applied}
        if skipped:
            payload["skipped"] = skipped
        return payload

    @mcp.tool(
        name="project_tick",
        description="Single entrypoint: refresh status, start eligible tasks, and summarize progress (compact).",
    )
    def project_tick(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        status_res = project_status(project_id=project_id, options={"include_handles": False, "include_timing": True})
        if status_res.get("state") != "ok":
            return status_res

        run_res = project_run(project_id=project_id, options={"include_handles": False})
        if run_res.get("state") not in {"ok", "disabled"}:
            return run_res

        status_res = project_status(project_id=project_id, options={"include_handles": False, "include_timing": True})
        counts = status_res.get("counts") if isinstance(status_res.get("counts"), dict) else {}
        tasks = status_res.get("tasks") if isinstance(status_res.get("tasks"), list) else []
        running_ids: list[str] = []
        stalled_ids: list[str] = []
        for t in tasks:
            if not isinstance(t, dict):
                continue
            if t.get("state") == "running" and t.get("id"):
                running_ids.append(str(t.get("id")))
                if t.get("stalled_suspected"):
                    stalled_ids.append(str(t.get("id")))

        summary: list[str] = []
        summary.append(
            f"Tasks: running={counts.get('running', 0)} completed={counts.get('completed', 0)} failed={counts.get('failed', 0)} pending={counts.get('pending', 0)}"
        )
        if isinstance(run_res, dict):
            started = run_res.get("started") if isinstance(run_res.get("started"), list) else []
            started_ids = [str(x.get('id')) for x in started if isinstance(x, dict) and x.get("id")]
            if started_ids:
                summary.append(f"Started: {', '.join(started_ids[:8])}{'…' if len(started_ids) > 8 else ''}")
        if running_ids:
            summary.append(f"Running: {', '.join(running_ids[:8])}{'…' if len(running_ids) > 8 else ''}")
        if stalled_ids:
            summary.append(f"Stalled suspected: {', '.join(stalled_ids[:8])}{'…' if len(stalled_ids) > 8 else ''}")

        return {"state": "ok", "counts": counts, "summary": summary}

    @mcp.tool(
        name="project_worktree_list",
        description="List per-task git worktrees under .codex/projects/<project_id>/worktrees (patch-only mode).",
    )
    def project_worktree_list(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}
        paths = _project_paths(project_id)
        worktrees_dir = paths["worktrees"]
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        entries: list[dict[str, Any]] = []
        for tid, ts in tasks_state.items():
            if not isinstance(ts, dict):
                continue
            wt = ts.get("worktree_dir")
            if not wt:
                continue
            p = Path(str(wt))
            if not p.exists():
                continue
            entry: dict[str, Any] = {"id": str(tid), "path": str(p)}
            st = str(ts.get("state") or "")
            if st:
                entry["state"] = st
            if ts.get("patch_path"):
                entry["patch_path"] = str(ts.get("patch_path"))
            entries.append(entry)
        # Also include stray dirs (best-effort)
        if worktrees_dir.exists():
            known = {e.get("path") for e in entries if isinstance(e, dict)}
            for child in sorted(worktrees_dir.iterdir()):
                if not child.is_dir():
                    continue
                if str(child) in known:
                    continue
                entries.append({"id": "unknown", "path": str(child), "state": "orphan"})
        return {"state": "ok", "worktrees": entries}

    @mcp.tool(
        name="project_worktree_cleanup",
        description="Cleanup per-task git worktrees for completed tasks. Default is safe (no force).",
    )
    def project_worktree_cleanup(
        *,
        project_id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}
        force = bool(options.get("force")) if options else False
        only_applied = True if options is None else bool(options.get("only_applied", True))
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
        removed: list[str] = []
        skipped: list[str] = []
        repo_root = _git_root_for_cwd(str(project.get("cwd") or ""))
        if not repo_root:
            return {"state": "error", "code": "E_GIT_REPO_NOT_FOUND", "message": "git repo not found"}

        for tid, ts in tasks_state.items():
            if not isinstance(ts, dict):
                continue
            st = str(ts.get("state") or "")
            if st not in {"completed", "failed", "canceled"}:
                continue
            wt = ts.get("worktree_dir")
            if not wt:
                continue
            if only_applied and not ts.get("patch_applied_at"):
                skipped.append(str(tid))
                continue
            wt_path = Path(str(wt))
            if not wt_path.exists():
                continue
            # Safe by default: skip dirty worktrees unless force=true
            code, out, _ = _run_git(wt_path, ["status", "--porcelain"])
            dirty = code == 0 and bool(out.strip())
            if dirty and not force:
                skipped.append(str(tid))
                continue
            args = ["worktree", "remove"]
            if force:
                args.append("--force")
            args.append(str(wt_path))
            code2, _, err2 = _run_git(repo_root, args)
            if code2 == 0:
                removed.append(str(tid))
                ts["worktree_removed_at"] = _utc_now_iso()
            else:
                ts["worktree_cleanup_error"] = compact_text(err2 or "cleanup failed", max_len=160)
                skipped.append(str(tid))

        with _PROJECT_LOCK:
            _save_state(project_id, state)
        payload: dict[str, Any] = {"state": "ok", "removed": removed}
        if skipped:
            payload["skipped"] = skipped
        return payload

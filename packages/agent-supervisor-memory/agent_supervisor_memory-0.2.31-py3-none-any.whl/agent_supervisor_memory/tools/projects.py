from __future__ import annotations

import hashlib
import json
import re
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from ..services.dispatch import CodexDispatch, CodexDispatchConfig
from ..utils.fs import atomic_write_json, find_ancestor_with_child_dir, project_codex_path
from ..utils.text import compact_text, truncate_tail_text


_PROJECT_LOCK = threading.Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _projects_root() -> Path:
    return project_codex_path("projects")


def _project_dir(project_id: str) -> Path:
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
    while True:
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
        has_more = bool(res.get("has_more"))
        if len(summary) > max_items:
            summary = summary[-max_items:]
        if not has_more:
            break
        if len(summary) >= max_items:
            break
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
    get_verbosity: Callable[[dict[str, Any] | None], str],
    effective_enabled: Callable[..., bool],
) -> None:
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
        project_path = _project_dir(project_id)
        project_path.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "id": project_id,
            "created_at": _utc_now_iso(),
            "title": (title or "").strip() or "Untitled",
            "cwd": (cwd or "").strip() or str(Path.cwd().resolve()),
        }
        if input:
            payload["input_sha256"] = _sha256(str(input))
        with _PROJECT_LOCK:
            atomic_write_json(_project_file(project_id, "project.json"), payload)
            atomic_write_json(_project_file(project_id, "plan.json"), {"version": 1, "tasks": []})
            atomic_write_json(_project_file(project_id, "state.json"), {"version": 1, "tasks": {}, "rounds": []})
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
        parallel = int(options.get("parallel", 3)) if options else 3
        parallel = max(1, min(parallel, 20))

        project, plan, state = _load_bundle(project_id)
        if not project or not plan:
            return {"state": "not_found", "message": "project not found"}
        state = state or {"version": 1, "tasks": {}, "rounds": []}
        state = _ensure_state(project_id, plan)
        tasks_state = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}

        # Refresh running tasks before scheduling new ones
        running = 0
        for tid, ts in list(tasks_state.items()):
            if not isinstance(ts, dict):
                continue
            if str(ts.get("state")) == "running" and ts.get("job_id"):
                _refresh_task_from_dispatch(ts, job_id=str(ts.get("job_id")))
            if str(ts.get("state")) == "running":
                running += 1

        available = max(0, parallel - running)
        started: list[dict[str, Any]] = []
        skipped: list[str] = []

        plan_tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else []
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

            prompt_path = str(t.get("prompt_path") or "")
            try:
                prompt_text = Path(prompt_path).expanduser().read_text(encoding="utf-8")
            except FileNotFoundError:
                ts["state"] = "failed"
                ts["last_error"] = "prompt_path not found"
                skipped.append(tid)
                continue

            task_cwd = str(t.get("cwd") or project.get("cwd") or "").strip() or str(Path.cwd().resolve())
            bucket = _dispatch_bucket_for_cwd(task_cwd)
            dispatch = CodexDispatch(CodexDispatchConfig(jobs_dir=dispatch_base_dir / bucket))

            res = dispatch.start(
                prompt=prompt_text,
                model=str(t.get("model")) if t.get("model") is not None else None,
                cwd=task_cwd,
                sandbox=str(t.get("sandbox")) if t.get("sandbox") is not None else "workspace-write",
                approval_policy=str(t.get("approval_policy")) if t.get("approval_policy") is not None else "never",
                extra_config=list(t.get("extra_config")) if isinstance(t.get("extra_config"), list) else None,
                env=dict(t.get("env")) if isinstance(t.get("env"), dict) else None,
                job_id_prefix=bucket,
            )
            job_id = str(res.get("job_id") or "")
            ts["state"] = "running"
            ts["job_id"] = job_id
            ts["attempts"] = int(ts.get("attempts") or 0) + 1
            ts["started_at"] = _utc_now_iso()
            ts.pop("finished_at", None)
            ts.pop("exit_code", None)
            ts.pop("last_error", None)
            started_entry: dict[str, Any] = {"id": tid}
            if include_handles:
                started_entry["job_id"] = job_id
            started.append(started_entry)
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
        summary_lines = int(options.get("summary_lines", 2)) if options else 2
        summary_lines = max(0, min(summary_lines, 5))

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
            if job_id and str(ts.get("state")) in {"running"}:
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
        summary_lines = int(options.get("summary_lines", 2)) if options else 2
        summary_lines = max(0, min(summary_lines, 5))

        project, plan, state = _load_bundle(project_id)
        if not project or not plan or not state:
            return {"state": "not_found", "message": "project not found"}

        # Refresh before reporting
        _ = project_status(project_id=project_id, options={"summary_lines": max(2, summary_lines), "include_handles": False})
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

            # For tool return summary (<= ~10 lines)
            if len(short_summary) < 9:
                if trimmed:
                    short_summary.append(f"{tid}: {trimmed[-1]}")
                else:
                    short_summary.append(f"{tid}: {st}")

        report_path = reports_dir / f"round_{n}.md"
        report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return {"report_path": str(report_path), "summary": short_summary}


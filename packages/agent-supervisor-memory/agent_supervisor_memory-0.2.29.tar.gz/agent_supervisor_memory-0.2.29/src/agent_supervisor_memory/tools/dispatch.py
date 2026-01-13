from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from pathlib import Path
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from ..services.dispatch import CodexDispatch, CodexDispatchConfig
from ..utils.fs import atomic_write_json, find_ancestor_with_child_dir, project_codex_path
from ..utils.text import compact_text, truncate_tail_text


NOISE_EVENT_TYPES = {
    "thread.started",
    "thread.created",
    "turn.started",
    "turn.created",
    "turn.delta",
    "turn.completed",
    "turn.finished",
    "run.started",
    "run.finished",
    "response.started",
    "response.completed",
    "response.finished",
    "thread_started",
    "thread_created",
    "turn_started",
    "turn_created",
    "turn_delta",
    "turn_completed",
    "turn_finished",
    "run_started",
    "run_finished",
    "response_started",
    "response_completed",
    "response_finished",
    "heartbeat",
    "ping",
    "pong",
    "item.started",
    "item.updated",
    "item.completed",
}

NOISY_ITEM_TYPES = {"command_execution", "mcp_tool_call", "todo_list"}
VERIFICATION_COMMAND_HINTS = ("compileall", "py_compile", "pytest", "ruff", "mypy", "tsc")


def _extract_readable_stdout(res: dict[str, Any], *, max_chars: int = 700) -> str | None:
    """
    Extract the last user-readable message from a dispatch status response.

    Priority:
      1) Last readable text
      2) Reasoning fallback
      3) Event type fallback (non-noise)
      4) Raw fallback (last non-empty line)
      5) Last message
    """
    max_chars = max(600, min(int(max_chars or 700), 800))
    noise_types = NOISE_EVENT_TYPES
    stdout_tail = res.get("stdout_tail")
    last_message = res.get("last_message")
    if not stdout_tail:
        return compact_text(str(last_message), max_len=max_chars) if last_message else None

    fallback_event_type: str | None = None
    raw_fallback: str | None = None

    def _flatten_content(content: Any) -> str | None:
        if content is None:
            return None
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                flattened = _flatten_content(item)
                if flattened:
                    parts.append(flattened)
            return " ".join(parts) if parts else None
        if isinstance(content, dict):
            ctype = content.get("type")
            if isinstance(ctype, str) and (ctype in NOISE_EVENT_TYPES or ctype in NOISY_ITEM_TYPES):
                return None
            if "text" in content:
                text_val = content.get("text")
                if isinstance(text_val, (str, int, float)):
                    return str(text_val)
                nested_text = _flatten_content(text_val)
                if nested_text:
                    return nested_text
            if "content" in content:
                return _flatten_content(content.get("content"))
            if "message" in content:
                return _flatten_content(content.get("message"))
            if "item" in content:
                return _flatten_content(content.get("item"))
            return None
        return " ".join(str(content).split())

    def _extract_from_obj(obj: Any) -> str | None:
        if obj is None:
            return None
        if isinstance(obj, list):
            for item in reversed(obj):
                text_val = _extract_from_obj(item)
                if text_val:
                    return text_val
            return None
        if not isinstance(obj, dict):
            return str(obj)

        event_type = obj.get("type") or ""
        if isinstance(event_type, str) and event_type in NOISE_EVENT_TYPES:
            return None

        for key in ("message", "content", "text"):
            if key in obj:
                msg_text = _flatten_content(obj.get(key))
                if msg_text:
                    return msg_text

        if "item" in obj and isinstance(obj.get("item"), dict):
            item = obj.get("item") or {}
            item_type = item.get("type") or ""
            if isinstance(item_type, str) and item_type in NOISE_EVENT_TYPES:
                return None
            if isinstance(item_type, str) and item_type in NOISY_ITEM_TYPES:
                return None
            msg_text = _flatten_content(item.get("message") or item.get("content") or item.get("text") or item)
            if msg_text:
                return msg_text

        return None

    reasoning_fallback: str | None = None
    lines = stdout_tail.splitlines()
    for line in reversed(lines):
        candidate = line.strip()
        if not candidate:
            continue
        if raw_fallback is None:
            raw_fallback = candidate
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        text_val = _extract_from_obj(obj)
        if text_val:
            if text_val not in noise_types:
                return compact_text(text_val, max_len=max_chars)
            continue

        if reasoning_fallback is None:
            if isinstance(obj, dict):
                reasoning_text = _flatten_content(obj.get("item") or obj.get("content") or obj.get("message"))
            else:
                reasoning_text = _flatten_content(obj)
            if reasoning_text:
                reasoning_fallback = compact_text(reasoning_text, max_len=max_chars)

        if not fallback_event_type and isinstance(obj, dict):
            event_type = obj.get("type")
            if isinstance(event_type, str) and event_type and event_type not in noise_types:
                fallback_event_type = str(event_type)

    if reasoning_fallback:
        return reasoning_fallback

    tail_fallback = raw_fallback
    if fallback_event_type and (not tail_fallback or tail_fallback.lstrip().startswith("{")):
        tail_fallback = fallback_event_type
    if tail_fallback:
        return compact_text(tail_fallback, max_len=max_chars)

    if last_message:
        return compact_text(str(last_message), max_len=max_chars)

    return None


def _compact_event(obj: dict[str, Any], *, max_text_chars: int, max_paths: int) -> dict[str, Any] | None:
    etype = obj.get("type")
    if isinstance(etype, str) and etype in NOISE_EVENT_TYPES:
        return None
    if isinstance(etype, str) and etype in NOISY_ITEM_TYPES:
        return None

    def _flatten(v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, (str, int, float)):
            return str(v)
        if isinstance(v, list):
            parts: list[str] = []
            for it in v:
                t = _flatten(it)
                if t:
                    parts.append(t)
            return " ".join(parts) if parts else None
        if isinstance(v, dict):
            vtype = v.get("type")
            if isinstance(vtype, str) and (vtype in NOISE_EVENT_TYPES or vtype in NOISY_ITEM_TYPES):
                return None
            for k in ("text", "message", "content"):
                if k in v:
                    t = _flatten(v.get(k))
                    if t:
                        return t
            if "item" in v:
                return _flatten(v.get("item"))
        return None

    out: dict[str, Any] = {}
    if isinstance(etype, str):
        out["type"] = etype
    if etype == "file_change":
        paths = _extract_paths_from_event(obj)
        if paths:
            limit = max(0, int(max_paths or 0))
            trimmed = paths[:limit] if limit > 0 else []
            total = len(paths)
            extra = max(0, total - len(trimmed))
            out["paths"] = trimmed
            out["paths_total"] = total
            out["paths_extra"] = extra
            preview = paths[:3]
            joined = ", ".join(preview)
            preview_extra = max(0, total - 3)
            if preview_extra > 0:
                joined = f"{joined} +{preview_extra}"
            out["text"] = f"Updated: {joined}"
        return out or None

    text = None
    for k in ("message", "content", "text"):
        if k in obj:
            text = _flatten(obj.get(k))
            if text:
                break
    if not text and "item" in obj:
        text = _flatten(obj.get("item"))

    if text:
        out["text"] = truncate_tail_text(compact_text(str(text), max_len=max_text_chars), max_chars=max_text_chars)
    return out or None


def _is_noise_json_text(text: str | None) -> bool:
    if not text:
        return False
    stripped = str(text).lstrip()
    if not stripped.startswith("{"):
        return False
    try:
        obj = json.loads(stripped)
    except json.JSONDecodeError:
        return False
    if not isinstance(obj, dict):
        return False
    etype = obj.get("type")
    return isinstance(etype, str) and (etype in NOISE_EVENT_TYPES or etype in NOISY_ITEM_TYPES)


def _extract_paths_from_event(ev: dict[str, Any]) -> list[str]:
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
                if key in val and val.get(key):
                    candidate = str(val.get(key))
                    break
        if candidate:
            normalized = candidate.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)

    def _extract_nested(val: Any) -> None:
        if val is None:
            return
        if isinstance(val, list):
            for item in val:
                _extract_nested(item)
            return
        _add(val)

    for key in ("paths", "files", "file_changes", "items"):
        if key in ev:
            _extract_nested(ev.get(key))
    for key in ("path", "file"):
        if key in ev:
            _add(ev.get(key))

    return ordered


def _normalize_summary_lines(lines: list[Any] | None, *, store_max_items: int) -> list[str]:
    cleaned: list[str] = []
    if store_max_items <= 0:
        return cleaned
    seen: set[str] = set()
    for raw in lines or []:
        if raw is None:
            continue
        text = raw if isinstance(raw, str) else str(raw)
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    if len(cleaned) > store_max_items:
        cleaned = cleaned[-store_max_items:]
    return cleaned


def _summary_file_path(dispatch: CodexDispatch, job_id: str) -> Path | None:
    if not job_id:
        return None
    try:
        return dispatch.jobs_dir / job_id / "summary.json"
    except Exception:
        return None


def _summarize_event(ev: Any) -> list[str]:
    if not isinstance(ev, dict):
        return []

    etype = ev.get("type")
    if etype == "file_change":
        paths = _extract_paths_from_event(ev)
        if not paths:
            return []
        max_paths = 3
        truncated = paths[:max_paths]
        extra = len(paths) - len(truncated)
        joined = ", ".join(truncated)
        if extra > 0:
            joined = f"{joined} +{extra}"
        return [f"Updated: {joined}"]

    if etype == "command_execution":
        command_val = (
            ev.get("command")
            or ev.get("cmd")
            or ev.get("argv")
            or ev.get("args")
            or ev.get("command_line")
        )
        command_text: str | None = None
        if isinstance(command_val, list):
            command_text = " ".join(str(part) for part in command_val)
        elif isinstance(command_val, dict):
            nested = command_val.get("argv") or command_val.get("args")
            if isinstance(nested, list):
                command_text = " ".join(str(part) for part in nested)
            else:
                command_text = str(command_val.get("raw") or command_val.get("cmd") or "")
        elif command_val is not None:
            command_text = str(command_val)
        if not command_text:
            return []
        lowered = command_text.lower()
        if not any(hint in lowered for hint in VERIFICATION_COMMAND_HINTS):
            return []

        exit_code = ev.get("exit_code", ev.get("code"))
        exit_str = str(exit_code) if exit_code is not None else "unknown"
        line = f"Verify: {command_text} (exit={exit_str})"
        if str(exit_code) not in {"0", "None"}:
            snippet = (
                ev.get("aggregated_output")
                or ev.get("stderr")
                or ev.get("stderr_delta")
                or ev.get("stdout_delta")
                or ev.get("output")
            )
            if snippet:
                snippet_text = truncate_tail_text(compact_text(str(snippet), max_len=200), max_chars=200)
                if snippet_text:
                    line = f"{line} | {snippet_text}"
        return [line]

    return []


def _load_summary_snapshot(
    dispatch: CodexDispatch,
    job_id: str,
    *,
    store_max_items: int,
) -> tuple[list[str], int] | None:
    path = _summary_file_path(dispatch, job_id)
    if not path:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    except Exception:
        return None
    summary_data = data.get("summary")
    summary_lines = _normalize_summary_lines(summary_data if isinstance(summary_data, list) else [], store_max_items=store_max_items)
    try:
        cursor = int(data.get("cursor", 0) or 0)
    except Exception:
        cursor = 0
    return summary_lines, cursor


def _persist_summary_snapshot(
    dispatch: CodexDispatch,
    job_id: str,
    summary: list[str],
    cursor: int,
    *,
    store_max_items: int,
) -> None:
    path = _summary_file_path(dispatch, job_id)
    if not path:
        return
    payload = {
        "cursor": int(cursor or 0),
        "summary": _normalize_summary_lines(summary, store_max_items=store_max_items),
    }
    try:
        atomic_write_json(path, payload)
    except Exception:
        return


def _update_job_summary(
    job_id: str,
    dispatch: CodexDispatch,
    *,
    job_summary: dict[str, list[str]],
    job_summary_cursor: dict[str, int],
    job_summary_lock: threading.Lock,
    store_max_items: int = 30,
    item_max_chars: int = 160,
    max_bytes: int = 12000,
    max_items: int = 120,
) -> list[str]:
    cursor = 0
    with job_summary_lock:
        cursor = int(job_summary_cursor.get(job_id, 0))

    new_cursor = cursor
    collected: list[str] = []
    while True:
        res = dispatch.events(
            job_id=job_id,
            cursor=new_cursor,
            max_bytes=max_bytes,
            max_items=max_items,
        )
        if not res.get("found"):
            return job_summary.get(job_id, [])
        new_cursor = int(res.get("cursor", new_cursor))
        events = res.get("events") if isinstance(res.get("events"), list) else []
        for ev in events:
            for line in _summarize_event(ev):
                if not line:
                    continue
                compacted = truncate_tail_text(compact_text(str(line), max_len=item_max_chars), max_chars=item_max_chars)
                if compacted:
                    collected.append(compacted)
        has_more = bool(res.get("has_more"))
        if not has_more or new_cursor == cursor:
            break
        cursor = new_cursor
        if len(collected) >= store_max_items:
            break

    with job_summary_lock:
        summary = job_summary.get(job_id, [])
        for line in collected:
            if line not in summary:
                summary.append(line)
        if len(summary) > store_max_items:
            summary = summary[-store_max_items:]
        job_summary[job_id] = summary
        job_summary_cursor[job_id] = new_cursor
        persisted_summary = list(summary)
        persisted_cursor = new_cursor
    _persist_summary_snapshot(
        dispatch,
        job_id,
        persisted_summary,
        persisted_cursor,
        store_max_items=store_max_items,
    )
    return persisted_summary


def _collect_artifacts(res: dict[str, Any]) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    for source in (res.get("artifacts"), (res.get("meta") or {}).get("artifacts")):
        if isinstance(source, dict):
            for key, value in source.items():
                if value is None:
                    continue
                artifacts[str(key)] = str(value)
    return artifacts


def _format_dispatch_status_output(
    res: dict[str, Any],
    *,
    verbosity: str,
    summary: list[str] | None = None,
    summary_max_items: int = 5,
    summary_cursor: int | None = None,
    include_summary_cursor: bool = False,
) -> dict[str, Any]:
    summary_cursor_value = int(summary_cursor or 0)
    if verbosity == "full":
        payload = dict(res)
        if payload.get("enabled") is True:
            payload.pop("enabled")
        if include_summary_cursor:
            payload["summary_cursor"] = summary_cursor_value
        return payload

    if not res.get("found"):
        payload = {"state": "not_found", "message": "Job not found"}
        if include_summary_cursor:
            payload["summary_cursor"] = summary_cursor_value
        return payload

    meta = res.get("meta") or {}
    state = meta.get("status")
    exit_code = meta.get("exit_code")
    summary_items = (summary or [])[-max(1, int(summary_max_items or 0)) :] if summary else []
    cursor_mode = "stdout_cursor" in res or "stderr_cursor" in res
    if cursor_mode:
        include_deltas = False
        delta_max_chars = 0
        options = res.get("_options")
        if isinstance(options, dict):
            include_deltas = bool(options.get("include_deltas"))
            delta_max_chars = int(options.get("delta_max_chars") or 0)

        payload: dict[str, Any] = {"state": state or "unknown"}
        cursor: dict[str, Any] = {}
        if "stdout_cursor" in res:
            cursor["stdout"] = res.get("stdout_cursor")
            stdout_delta = res.get("stdout_delta")
            if stdout_delta:
                payload["has_stdout_delta"] = True
                payload["stdout_delta_len"] = len(str(stdout_delta))
                if include_deltas:
                    payload["stdout_delta"] = truncate_tail_text(str(stdout_delta), max_chars=delta_max_chars or 1200)
            else:
                payload["has_stdout_delta"] = False
        if "stderr_cursor" in res:
            cursor["stderr"] = res.get("stderr_cursor")
            stderr_delta = res.get("stderr_delta")
            if stderr_delta:
                payload["has_stderr_delta"] = True
                payload["stderr_delta_len"] = len(str(stderr_delta))
                if include_deltas:
                    payload["stderr_delta"] = truncate_tail_text(str(stderr_delta), max_chars=delta_max_chars or 1200)
            else:
                payload["has_stderr_delta"] = False
        if cursor:
            payload["cursor"] = cursor
        if exit_code is not None and (state == "failed" or state == "completed"):
            payload["exit_code"] = exit_code
        if summary_items:
            payload["summary"] = summary_items
        if include_summary_cursor:
            payload["summary_cursor"] = summary_cursor_value
        return payload

    max_tail_chars = 700
    readable_message = _extract_readable_stdout(res, max_chars=max_tail_chars)
    stderr_tail = compact_text(res.get("stderr_tail") or "", max_len=max_tail_chars) if res.get("stderr_tail") else None

    if state == "failed":
        payload: dict[str, Any] = {
            "state": "failed",
            "message": stderr_tail
            or readable_message
            or compact_text(res.get("last_message") or "Task failed", max_len=max_tail_chars),
        }
        if exit_code is not None:
            payload["exit_code"] = exit_code
        if summary_items:
            payload["summary"] = summary_items
        if include_summary_cursor:
            payload["summary_cursor"] = summary_cursor_value
        return payload

    resolved_state = state or "unknown"
    message = readable_message or compact_text(res.get("last_message") or "", max_len=max_tail_chars)
    if _is_noise_json_text(message):
        message = summary_items[-1] if summary_items else None
    if not message:
        message = "Running…" if resolved_state == "running" else "No output yet"

    payload: dict[str, Any] = {"state": resolved_state, "message": message}
    if summary_items:
        payload["summary"] = summary_items[-max(1, int(summary_max_items or 0)) :]
    if include_summary_cursor:
        payload["summary_cursor"] = summary_cursor_value
    return payload


def _format_wait_result(
    res: dict[str, Any],
    job_id: str | None,
    verbosity: str,
    state_override: str | None = None,
    summary: list[str] | None = None,
    summary_max_items: int = 5,
    summary_cursor: int | None = None,
    include_summary_cursor: bool = False,
) -> dict[str, Any]:
    found = res.get("found", True)
    meta = res.get("meta") or {}
    exit_code = meta.get("exit_code")
    state = state_override or meta.get("status") or res.get("state")
    if not state:
        state = "not_found" if not found else "unknown"
    artifacts = _collect_artifacts(res)
    summary_items = (summary or [])[-max(1, int(summary_max_items or 0)) :] if summary else []
    summary_cursor_value = int(summary_cursor or 0)

    if verbosity == "full":
        payload: dict[str, Any] = {**res, "job_id": job_id, "state": state}
        if exit_code is not None and "exit_code" not in payload:
            payload["exit_code"] = exit_code
        if artifacts and "artifacts" not in payload:
            payload["artifacts"] = artifacts
        if summary_items:
            payload["summary"] = summary_items
        if payload.get("enabled") is True:
            payload.pop("enabled")
        if include_summary_cursor:
            payload["summary_cursor"] = summary_cursor_value
        return payload

    if not found:
        payload = {"state": "not_found", "job_id": job_id, "message": "Job not found"}
        if include_summary_cursor:
            payload["summary_cursor"] = summary_cursor_value
        return payload

    max_tail_chars = 700
    stderr_tail_raw = res.get("stderr_tail") or ""
    stderr_tail = compact_text(stderr_tail_raw, max_len=max_tail_chars) if stderr_tail_raw else None
    readable_message = _extract_readable_stdout(res, max_chars=max_tail_chars)
    last_message = res.get("last_message")

    if state == "failed":
        message = stderr_tail or readable_message or compact_text(str(last_message or "Task failed"), max_len=max_tail_chars)
    elif state == "timeout":
        message = stderr_tail or readable_message or compact_text(str(last_message or "Timed out"), max_len=max_tail_chars)
    else:
        message = readable_message or compact_text(str(last_message or ""), max_len=max_tail_chars)
        if _is_noise_json_text(message):
            message = summary_items[-1] if summary_items else None
        if not message:
            message = "Running…" if state == "running" else "No output yet"

    payload: dict[str, Any] = {"state": state, "job_id": job_id, "message": message}
    if exit_code is not None:
        payload["exit_code"] = exit_code
    if artifacts:
        payload["artifacts"] = artifacts
    if summary_items:
        payload["summary"] = summary_items
    if include_summary_cursor:
        payload["summary_cursor"] = summary_cursor_value
    return payload


def _wait_for_job(
    dispatch: CodexDispatch,
    job_id: str,
    *,
    poll_interval_ms: int,
    timeout_seconds: int,
    max_wait_seconds: int,
    include_last_message_while_running: bool,
    stdout_tail_bytes: int,
    stderr_tail_bytes: int,
    verbosity: str,
    summary_max_items: int = 5,
    include_summary_cursor: bool = False,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds if timeout_seconds > 0 else None
    call_deadline = time.time() + max_wait_seconds if max_wait_seconds and max_wait_seconds > 0 else None
    while True:
        res = dispatch.status(
            job_id=job_id,
            stdout_tail_bytes=stdout_tail_bytes,
            stderr_tail_bytes=stderr_tail_bytes,
            include_last_message=include_last_message_while_running,
            compact=True,
            include_artifacts=True,
        )
        summary_lines = _refresh_summary(job_id, dispatch, store_max_items=30)
        summary_cursor_value = _get_summary_cursor(job_id)
        if not res.get("found"):
            return _format_wait_result(
                res,
                job_id,
                verbosity,
                state_override="not_found",
                summary=summary_lines,
                summary_max_items=summary_max_items,
                summary_cursor=summary_cursor_value,
                include_summary_cursor=include_summary_cursor,
            )

        state = (res.get("meta") or {}).get("status")
        now = time.time()
        if call_deadline and now >= call_deadline:
            return _format_wait_result(
                res,
                job_id,
                verbosity,
                state_override="running",
                summary=summary_lines,
                summary_max_items=summary_max_items,
                summary_cursor=summary_cursor_value,
                include_summary_cursor=include_summary_cursor,
            )
        if deadline and now >= deadline:
            return _format_wait_result(
                res,
                job_id,
                verbosity,
                state_override="timeout",
                summary=summary_lines,
                summary_max_items=summary_max_items,
                summary_cursor=summary_cursor_value,
                include_summary_cursor=include_summary_cursor,
            )

        if state and state != "running":
            if not include_last_message_while_running:
                res = dispatch.status(
                    job_id=job_id,
                    stdout_tail_bytes=stdout_tail_bytes,
                    stderr_tail_bytes=stderr_tail_bytes,
                    include_last_message=True,
                    compact=True,
                    include_artifacts=True,
                )
                summary_lines = _refresh_summary(job_id, dispatch, store_max_items=30)
            summary_cursor_value = _get_summary_cursor(job_id)
            return _format_wait_result(
                res,
                job_id,
                verbosity,
                summary=summary_lines,
                summary_max_items=summary_max_items,
                summary_cursor=summary_cursor_value,
                include_summary_cursor=include_summary_cursor,
            )

        time.sleep(max(0.01, poll_interval_ms / 1000.0))


def _sha256_short(text: str, *, n: int = 10) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[: max(1, int(n))]


def _sanitize_bucket_component(text: str) -> str:
    normalized = (text or "").strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "project"


def _dispatch_bucket_for_cwd(cwd: str | None) -> str:
    if not cwd:
        return "unknown"
    try:
        start = Path(cwd).expanduser().resolve()
    except Exception:
        return "unknown"
    root = (
        find_ancestor_with_child_dir(start, ".codex")
        or find_ancestor_with_child_dir(start, ".git")
        or start
    )
    base_name = _sanitize_bucket_component(root.name)
    suffix = _sha256_short(root.as_posix(), n=10)
    return f"{base_name}_{suffix}"


def _split_bucketed_job_id(job_id: str) -> tuple[str | None, str]:
    if not job_id:
        return (None, "")
    if "--" not in job_id:
        return (None, job_id)
    bucket, rest = job_id.split("--", 1)
    if not bucket or not rest:
        return (None, job_id)
    return (bucket, rest)


def register_dispatch_tools(
    mcp: FastMCP,
    *,
    dispatch_base_dir: Path,
    dispatch_enabled_default: bool,
    get_verbosity: Callable[[dict[str, Any] | None], str],
    effective_enabled: Callable[..., bool],
) -> None:
    last_job_lock = threading.Lock()
    started_jobs_lock = threading.Lock()
    started_job_ids: list[str] = []
    last_job_id: str | None = None
    job_ref_lock = threading.Lock()
    next_job_ref = 1
    job_id_by_ref: dict[int, str] = {}
    job_ref_by_id: dict[str, int] = {}
    job_summary_lock = threading.Lock()
    job_summary: dict[str, list[str]] = {}
    job_summary_cursor: dict[str, int] = {}

    def _get_summary_cursor(job_id: str | None) -> int:
        if not job_id:
            return 0
        with job_summary_lock:
            return int(job_summary_cursor.get(job_id, 0) or 0)

    def _dispatch_for_job(job_id: str) -> CodexDispatch:
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

    def _record_started_job(job_id: str | None) -> None:
        if not job_id:
            return
        with started_jobs_lock:
            if job_id not in started_job_ids:
                started_job_ids.append(job_id)

    def _job_ref_for_id(job_id: str | None) -> int | None:
        nonlocal next_job_ref
        if not job_id:
            return None
        with job_ref_lock:
            existing = job_ref_by_id.get(job_id)
            if existing is not None:
                return existing
            ref = next_job_ref
            next_job_ref += 1
            job_ref_by_id[job_id] = ref
            job_id_by_ref[ref] = job_id
            return ref

    def _job_id_for_ref(job_ref: int | None) -> str | None:
        if job_ref is None:
            return None
        with job_ref_lock:
            return job_id_by_ref.get(int(job_ref))

    def _refresh_summary(
        job_id: str,
        dispatch: CodexDispatch,
        *,
        store_max_items: int = 30,
        item_max_chars: int = 160,
    ) -> list[str]:
        needs_backfill = False
        with job_summary_lock:
            needs_backfill = job_id not in job_summary or int(job_summary_cursor.get(job_id, 0) or 0) == 0
        if needs_backfill:
            snapshot = _load_summary_snapshot(dispatch, job_id, store_max_items=store_max_items)
            if snapshot:
                summary_lines, disk_cursor = snapshot
                with job_summary_lock:
                    merged = list(job_summary.get(job_id, []))
                    for line in summary_lines:
                        if line not in merged:
                            merged.append(line)
                    if len(merged) > store_max_items:
                        merged = merged[-store_max_items:]
                    job_summary[job_id] = merged
                    existing_cursor = int(job_summary_cursor.get(job_id, 0) or 0)
                    job_summary_cursor[job_id] = max(existing_cursor, disk_cursor)
        try:
            return _update_job_summary(
                job_id,
                dispatch,
                job_summary=job_summary,
                job_summary_cursor=job_summary_cursor,
                job_summary_lock=job_summary_lock,
                store_max_items=store_max_items,
                item_max_chars=item_max_chars,
            )
        except Exception:
            return job_summary.get(job_id, [])

    @mcp.tool(
        name="codex_dispatch_start",
        description="Launch a 'codex exec' task. Defaults to async (returns immediately); set options.wait=true to wait (bounded) for completion. Supports prompt_path/options.prompt_path to avoid large prompts. Output saved to stdout.jsonl/stderr.log.",
    )
    def codex_dispatch_start(
        *,
        prompt: str = "",
        prompt_path: str | None = None,
        model: str | None = None,
        cwd: str | None = None,
        sandbox: str | None = "workspace-write",
        approval_policy: str | None = "never",
        extra_config: list[str] | None = None,
        env: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal last_job_id
        enabled = effective_enabled(options, field="enable_dispatch", default=dispatch_enabled_default)
        if not enabled:
            return {"state": "disabled"}

        verbosity = get_verbosity(options)
        wait = bool(options.get("wait")) if (options and "wait" in options) else False
        poll_interval_ms = int(options.get("poll_interval_ms", 250)) if options else 250
        timeout_seconds = int(options.get("timeout_seconds", 0)) if options else 0
        max_wait_seconds = int(options.get("max_wait_seconds", 45)) if options else 45
        include_last_message_while_running = bool(options.get("include_last_message_while_running", False)) if options else False
        stdout_tail_bytes = int(options.get("stdout_tail_bytes", 2000)) if options else 2000
        stderr_tail_bytes = int(options.get("stderr_tail_bytes", 2000)) if options else 2000
        summary_max_items = int(options.get("summary_max_items", 5)) if options else 5
        include_summary_cursor = bool(options.get("include_summary_cursor")) if options else False

        def _normalize_effort(value: Any) -> str | None:
            if not isinstance(value, str):
                return None
            effort = value.strip().lower()
            return effort if effort in ("low", "medium", "high") else None

        resolved_prompt = (prompt or "").strip()
        resolved_prompt_path = prompt_path or (str(options.get("prompt_path")) if (options and options.get("prompt_path")) else None)
        if not resolved_prompt and resolved_prompt_path:
            try:
                resolved_prompt = Path(resolved_prompt_path).expanduser().read_text(encoding="utf-8")
            except FileNotFoundError:
                return {"state": "error", "code": "E_PROMPT_PATH_NOT_FOUND", "message": "prompt_path not found"}
        if not resolved_prompt and options and options.get("use_project_prompt") is True:
            default_path = project_codex_path("structured-request.json")
            try:
                resolved_prompt = default_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                return {
                    "state": "error",
                    "code": "E_PROJECT_PROMPT_NOT_FOUND",
                    "message": "project prompt not found",
                }
        if not resolved_prompt:
            return {"state": "error", "code": "E_PROMPT_REQUIRED", "message": "prompt or prompt_path required"}

        effective_extra_config = extra_config
        if options:
            max_effort = _normalize_effort(options.get("max_model_reasoning_effort") or options.get("max_reasoning_effort"))
            if max_effort:
                requested_effort = _normalize_effort(
                    options.get("model_reasoning_effort")
                    if options.get("model_reasoning_effort") is not None
                    else options.get("reasoning_effort")
                )
                effort_rank = {"low": 0, "medium": 1, "high": 2}
                effective_effort = max_effort
                if requested_effort:
                    if effort_rank.get(requested_effort, 0) < effort_rank.get(max_effort, 0):
                        effective_effort = requested_effort
                effective_extra_config = list(extra_config) if extra_config else []
                effective_extra_config.append(f'model_reasoning_effort="{effective_effort}"')

        bucket = _dispatch_bucket_for_cwd(cwd)
        dispatch = CodexDispatch(CodexDispatchConfig(jobs_dir=dispatch_base_dir / bucket))
        res = dispatch.start(
            prompt=resolved_prompt,
            model=model,
            cwd=cwd,
            sandbox=sandbox,
            approval_policy=approval_policy,
            extra_config=effective_extra_config,
            env=env,
            job_id_prefix=bucket,
        )
        with last_job_lock:
            last_job_id = res.get("job_id")
        _record_started_job(res.get("job_id"))
        job_ref = _job_ref_for_id(res.get("job_id"))

        job_id = res.get("job_id")
        if not wait:
            if verbosity == "full":
                full_payload = {**res, "job_id": job_id, "job_ref": job_ref}
                if full_payload.get("enabled") is True:
                    full_payload.pop("enabled")
                return full_payload
            payload: dict[str, Any] = {"state": "running", "job_id": job_id, "job_ref": job_ref}
            if options and options.get("omit_job_id") is True:
                payload.pop("job_id", None)
            if options and options.get("include_artifacts") is True:
                artifacts = res.get("artifacts") or {}
                if artifacts:
                    payload["artifacts"] = artifacts
            return payload

        if not job_id:
            return {"state": "error", "code": "E_DISPATCH_START_FAILED", "message": "failed to start dispatch job"}

        result = _wait_for_job(
            dispatch,
            job_id,
            poll_interval_ms=poll_interval_ms,
            timeout_seconds=timeout_seconds,
            max_wait_seconds=max_wait_seconds,
            include_last_message_while_running=include_last_message_while_running,
            stdout_tail_bytes=stdout_tail_bytes,
            stderr_tail_bytes=stderr_tail_bytes,
            verbosity=verbosity,
            summary_max_items=summary_max_items,
            include_summary_cursor=include_summary_cursor,
        )
        if isinstance(result, dict) and "job_ref" not in result:
            result["job_ref"] = job_ref
            if options and options.get("omit_job_id") is True:
                result.pop("job_id", None)
        return result

    @mcp.tool(
        name="codex_dispatch_status",
        description="Poll the status of a background task. Supports compact output (default: status+tails only) or full metadata. Use include_last_message=false while running, true on completion for efficiency.",
    )
    def codex_dispatch_status(
        *,
        job_id: str | None = None,
        job_ref: int | None = None,
        include_last_message: bool = True,
        stdout_cursor: int | None = None,
        stderr_cursor: int | None = None,
        stdout_tail_bytes: int = 2000,
        stderr_tail_bytes: int = 2000,
        compact: bool = True,
        include_artifacts: bool = False,
        include_command: bool = False,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal last_job_id
        enabled = effective_enabled(options, field="enable_dispatch", default=dispatch_enabled_default)
        if not enabled:
            return {"state": "disabled", "message": "Dispatch disabled"}

        verbosity = get_verbosity(options)
        summary_max_items = int(options.get("summary_max_items", 5)) if options else 5
        include_summary_cursor = bool(options.get("include_summary_cursor")) if options else False
        with last_job_lock:
            effective_job_id = job_id or _job_id_for_ref(job_ref) or last_job_id
            if effective_job_id:
                last_job_id = effective_job_id
        if not effective_job_id:
            return {"state": "error", "code": "E_JOB_REQUIRED", "message": "job_id or job_ref required"}

        dispatch = _dispatch_for_job(effective_job_id)
        res = dispatch.status(
            job_id=effective_job_id,
            stdout_cursor=stdout_cursor,
            stderr_cursor=stderr_cursor,
            include_last_message=include_last_message,
            stdout_tail_bytes=stdout_tail_bytes,
            stderr_tail_bytes=stderr_tail_bytes,
            compact=compact,
            include_artifacts=include_artifacts,
            include_command=include_command,
        )
        summary_lines = _refresh_summary(effective_job_id, dispatch, store_max_items=30)
        summary_cursor_value = _get_summary_cursor(effective_job_id)
        if stdout_cursor is not None or stderr_cursor is not None:
            res["_options"] = options
        out = _format_dispatch_status_output(
            res,
            verbosity=verbosity,
            summary=summary_lines,
            summary_max_items=summary_max_items,
            summary_cursor=summary_cursor_value,
            include_summary_cursor=include_summary_cursor,
        )
        if isinstance(out, dict) and "job_ref" not in out:
            out["job_ref"] = _job_ref_for_id(effective_job_id)
            if options and options.get("omit_job_ref") is True:
                out.pop("job_ref", None)
        return out

    @mcp.tool(
        name="codex_dispatch_cancel",
        description="Request cancellation of a running codex dispatch job by job_id or job_ref.",
    )
    def codex_dispatch_cancel(
        *,
        job_id: str | None = None,
        job_ref: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal last_job_id
        enabled = effective_enabled(options, field="enable_dispatch", default=dispatch_enabled_default)
        if not enabled:
            return {"state": "disabled", "message": "Dispatch disabled"}

        with last_job_lock:
            effective_job_id = job_id or _job_id_for_ref(job_ref) or last_job_id
            if effective_job_id:
                last_job_id = effective_job_id
        if not effective_job_id:
            return {"state": "error", "code": "E_JOB_REQUIRED", "message": "job_id or job_ref required"}

        dispatch = _dispatch_for_job(effective_job_id)
        res = dispatch.cancel(job_id=effective_job_id)
        out: dict[str, Any] = dict(res) if isinstance(res, dict) else {"state": "error", "code": "E_UNKNOWN", "message": "cancel failed"}
        if "job_ref" not in out:
            out["job_ref"] = _job_ref_for_id(effective_job_id)
        if options and options.get("omit_job_id") is True:
            out.pop("job_id", None)
        return out

    @mcp.tool(
        name="codex_dispatch_events",
        description="Incrementally read parsed stdout.jsonl events for a dispatch job using a cursor. Defaults to compact, noise-filtered events to minimize context.",
    )
    def codex_dispatch_events(
        *,
        job_id: str | None = None,
        job_ref: int | None = None,
        cursor: int = 0,
        max_bytes: int = 8000,
        max_items: int = 50,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        nonlocal last_job_id
        enabled = effective_enabled(options, field="enable_dispatch", default=dispatch_enabled_default)
        if not enabled:
            return {"state": "disabled", "message": "Dispatch disabled"}

        with last_job_lock:
            effective_job_id = job_id or _job_id_for_ref(job_ref) or last_job_id
            if effective_job_id:
                last_job_id = effective_job_id
        if not effective_job_id:
            return {"state": "error", "code": "E_JOB_REQUIRED", "message": "job_id or job_ref required"}

        dispatch = _dispatch_for_job(effective_job_id)
        res = dispatch.events(
            job_id=effective_job_id,
            cursor=int(cursor or 0),
            max_bytes=int(max_bytes or 0),
            max_items=int(max_items or 0),
        )
        if not res.get("found"):
            return {"state": "not_found", "message": "Job not found"}

        meta = res.get("meta") or {}
        state = meta.get("status") or "unknown"
        max_text_chars = 400
        raw = bool(options.get("raw")) if options else False
        include_meta = bool(options.get("include_meta")) if options else False
        include_job_ref = not (options and options.get("omit_job_ref") is True)
        max_paths = 20
        if options and "max_paths" in options:
            try:
                max_paths = int(options.get("max_paths", max_paths))
            except (TypeError, ValueError):
                max_paths = 20
        max_paths = max(0, max_paths)

        events = res.get("events") if isinstance(res.get("events"), list) else []
        if raw:
            out_events = events
        else:
            compacted: list[dict[str, Any]] = []
            for ev in events:
                if not isinstance(ev, dict):
                    continue
                ce = _compact_event(ev, max_text_chars=max_text_chars, max_paths=max_paths)
                if ce:
                    compacted.append(ce)
            out_events = compacted

        payload: dict[str, Any] = {
            "state": state,
            "cursor": res.get("cursor", cursor),
            "has_more": bool(res.get("has_more")),
            "events": out_events,
        }
        if include_job_ref:
            payload["job_ref"] = _job_ref_for_id(effective_job_id)
        if include_meta:
            payload["meta"] = meta
        return payload

    @mcp.tool(
        name="codex_dispatch_wait_all",
        description="Wait for one or more codex dispatch jobs to finish. Defaults to summary-only (state/counts); set options.summary_only=false for detailed per-job results. If job_ids is omitted, uses all jobs started in this server process.",
    )
    def codex_dispatch_wait_all(
        *,
        job_ids: list[str] | None = None,
        poll_interval_ms: int = 250,
        timeout_seconds: int = 0,
        include_last_message_while_running: bool = False,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_dispatch", default=dispatch_enabled_default)
        if not enabled:
            return {"state": "disabled"}

        summary_only = True
        if options and "summary_only" in options:
            summary_only = bool(options.get("summary_only"))

        verbosity = "tail" if summary_only else get_verbosity(options)
        summary_max_items = int(options.get("summary_max_items", 3 if summary_only else 5)) if options else (3 if summary_only else 5)
        include_counts_requested = bool(options.get("include_counts")) if options else False
        if options and "stdout_tail_bytes" in options:
            stdout_tail_bytes = int(options.get("stdout_tail_bytes", 0))
        elif summary_only:
            stdout_tail_bytes = 0
        else:
            stdout_tail_bytes = 2000

        if options and "stderr_tail_bytes" in options:
            stderr_tail_bytes = int(options.get("stderr_tail_bytes", 0))
        elif summary_only:
            stderr_tail_bytes = 0
        else:
            stderr_tail_bytes = 2000

        effective_poll_interval_ms = int(options.get("poll_interval_ms", poll_interval_ms)) if options else poll_interval_ms
        effective_timeout_seconds = int(options.get("timeout_seconds", timeout_seconds)) if options else timeout_seconds
        max_wait_seconds = int(options.get("max_wait_seconds", 45)) if options else 45
        include_last = include_last_message_while_running
        if options and "include_last_message_while_running" in options:
            include_last = bool(options.get("include_last_message_while_running"))

        include_problem_job_ids = False
        if options and "include_problem_job_ids" in options:
            include_problem_job_ids = bool(options.get("include_problem_job_ids"))

        include_summary_cursor = bool(options.get("include_summary_cursor")) if options else False

        problem_only = bool(options.get("problem_only")) if options else False

        def _parse_problem_states(raw: Any) -> set[str]:
            default_states = {"failed", "timeout", "not_found", "canceled"}
            if raw is None:
                return set(default_states)
            values: list[str] = []
            if isinstance(raw, str):
                raw_str = raw.strip()
                if not raw_str:
                    return set(default_states)
                loaded: Any = None
                if raw_str.startswith("["):
                    try:
                        loaded = json.loads(raw_str)
                    except Exception:
                        loaded = None
                if isinstance(loaded, list):
                    values = [str(item).strip() for item in loaded if str(item).strip()]
                else:
                    values = [part.strip() for part in raw_str.split(",") if part.strip()]
            elif isinstance(raw, list):
                values = [str(item).strip() for item in raw if str(item).strip()]
            states = {v.lower() for v in values if v}
            if not states:
                return set(default_states)
            return states

        problem_states = _parse_problem_states(options.get("problem_states") if options else None)
        if problem_only:
            include_counts_requested = True

        with started_jobs_lock:
            effective_job_ids = list(job_ids if job_ids is not None else started_job_ids)

        results: list[dict[str, Any]] = []
        overall_state = "completed"
        failed_job_ids: list[str] = []
        timeout_job_ids: list[str] = []
        not_found_job_ids: list[str] = []
        canceled_job_ids: list[str] = []
        completed_count = 0
        failed_count = 0
        running_count = 0
        timeout_count = 0
        not_found_count = 0
        canceled_count = 0
        job_states: list[str] = []
        problem_job_ids: dict[str, list[str]] = {}

        if not effective_job_ids:
            if summary_only:
                payload: dict[str, Any] = {"state": overall_state, "jobs": []}
                if include_counts_requested:
                    payload["counts"] = {
                        "total": 0,
                        "completed": completed_count,
                        "failed": failed_count,
                        "running": running_count,
                        "timeout": timeout_count,
                        "not_found": not_found_count,
                    }
                return payload
            return {"state": overall_state, "jobs": results}

        for jid in effective_job_ids:
            dispatch = _dispatch_for_job(jid)
            result = _wait_for_job(
                dispatch,
                jid,
                poll_interval_ms=effective_poll_interval_ms,
                timeout_seconds=effective_timeout_seconds,
                max_wait_seconds=max_wait_seconds,
                include_last_message_while_running=include_last,
                stdout_tail_bytes=stdout_tail_bytes,
                stderr_tail_bytes=stderr_tail_bytes,
                verbosity=verbosity,
                summary_max_items=summary_max_items,
                include_summary_cursor=include_summary_cursor,
            )
            results.append(result)

            state = str(result.get("state") or "").lower()
            job_states.append(state)
            if state in problem_states:
                problem_job_ids.setdefault(state, []).append(jid)
            if state == "running":
                running_count += 1
                if overall_state == "completed":
                    overall_state = "running"
            elif state == "timeout":
                timeout_job_ids.append(jid)
                timeout_count += 1
                if overall_state == "completed":
                    overall_state = "timeout"
            elif state == "completed":
                completed_count += 1
            elif state == "not_found":
                not_found_job_ids.append(jid)
                not_found_count += 1
                if overall_state not in {"timeout"}:
                    overall_state = "failed"
            elif state == "canceled":
                canceled_job_ids.append(jid)
                canceled_count += 1
                if overall_state not in {"timeout"}:
                    overall_state = "failed"
            else:
                failed_job_ids.append(jid)
                failed_count += 1
                if overall_state not in {"timeout"}:
                    overall_state = "failed"

        counts = {
            "total": len(effective_job_ids),
            "completed": completed_count,
            "failed": failed_count,
            "running": running_count,
            "timeout": timeout_count,
            "not_found": not_found_count,
            "canceled": canceled_count,
        }
        has_problems = bool(problem_job_ids)

        if summary_only:
            jobs_payload: list[dict[str, Any]] = []
            for idx, jid in enumerate(effective_job_ids):
                result = results[idx] if idx < len(results) else {}
                summary_items = result.get("summary") if isinstance(result, dict) else None
                summary_list = summary_items if isinstance(summary_items, list) else job_summary.get(jid, [])
                entry: dict[str, Any] = {
                    "job_id": result.get("job_id") if isinstance(result, dict) else jid,
                    "state": result.get("state") if isinstance(result, dict) else None,
                }
                summary_cursor_val: int | None = None
                if isinstance(result, dict):
                    try:
                        summary_cursor_val = int(result.get("summary_cursor")) if result.get("summary_cursor") is not None else None
                    except (TypeError, ValueError):
                        summary_cursor_val = None
                if summary_cursor_val is None:
                    summary_cursor_val = _get_summary_cursor(jid)
                trimmed_summary = (summary_list or [])[-max(1, int(summary_max_items or 0)) :]
                if trimmed_summary:
                    entry["summary"] = trimmed_summary
                if include_summary_cursor:
                    entry["summary_cursor"] = int(summary_cursor_val or 0)
                jobs_payload.append(entry)

            if problem_only:
                filtered_jobs: list[dict[str, Any]] = []
                for idx, entry in enumerate(jobs_payload):
                    state_value = job_states[idx] if idx < len(job_states) else entry.get("state")
                    if str(state_value or "").lower() in problem_states:
                        filtered_jobs.append(entry)
                jobs_payload = filtered_jobs

            payload = {"state": overall_state, "jobs": jobs_payload}
            if include_counts_requested or has_problems:
                payload["counts"] = counts
            if include_problem_job_ids:
                if failed_job_ids:
                    payload["failed_job_ids"] = failed_job_ids
                if timeout_job_ids:
                    payload["timeout_job_ids"] = timeout_job_ids
                if not_found_job_ids:
                    payload["not_found_job_ids"] = not_found_job_ids
                if canceled_job_ids:
                    payload["canceled_job_ids"] = canceled_job_ids
                extra_problem_ids = {
                    state: ids for state, ids in problem_job_ids.items() if state not in {"failed", "timeout", "not_found", "canceled"}
                }
                if extra_problem_ids:
                    payload["problem_job_ids"] = extra_problem_ids
            return payload

        output_results = results if not problem_only else []
        if problem_only:
            for idx, result in enumerate(results):
                state_value = job_states[idx] if idx < len(job_states) else (result.get("state") if isinstance(result, dict) else None)
                if str(state_value or "").lower() in problem_states:
                    output_results.append(result)

        payload: dict[str, Any] = {"state": overall_state, "jobs": output_results}
        if include_counts_requested or has_problems:
            payload["counts"] = counts
        if include_problem_job_ids:
            if failed_job_ids:
                payload["failed_job_ids"] = failed_job_ids
            if timeout_job_ids:
                payload["timeout_job_ids"] = timeout_job_ids
            if not_found_job_ids:
                payload["not_found_job_ids"] = not_found_job_ids
            if canceled_job_ids:
                payload["canceled_job_ids"] = canceled_job_ids
            extra_problem_ids = {
                state: ids for state, ids in problem_job_ids.items() if state not in {"failed", "timeout", "not_found", "canceled"}
            }
            if extra_problem_ids:
                payload["problem_job_ids"] = extra_problem_ids
        return payload

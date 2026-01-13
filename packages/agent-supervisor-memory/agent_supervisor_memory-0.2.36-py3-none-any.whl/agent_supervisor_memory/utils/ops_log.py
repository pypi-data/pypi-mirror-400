from __future__ import annotations

import inspect
from functools import wraps
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from .fs import project_codex_path
from .metrics import record_call
from .text import compact_text


_OPS_LOCK = threading.Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_trace_id() -> str:
    return uuid.uuid4().hex[:16]


def _ops_path() -> str:
    return str(project_codex_path("operations-log.md"))


def append_ops_line(line: str) -> None:
    path = _ops_path()
    with _OPS_LOCK:
        p = project_codex_path("operations-log.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")


def log_tool_start(*, tool_name: str, trace_id: str, details: str | None = None) -> float:
    started_at = _utc_now_iso()
    msg = compact_text(details or "", max_len=180) if details else ""
    line = f"- {started_at} event=start tool={tool_name} trace={trace_id} state=started{(' ' + msg) if msg else ''}"
    append_ops_line(line)
    return time.monotonic()


def log_tool_end(
    *,
    tool_name: str,
    trace_id: str,
    start_monotonic: float,
    state: str,
    code: str | None = None,
    message: str | None = None,
    ) -> int:
    elapsed_ms = int(max(0.0, (time.monotonic() - float(start_monotonic or 0.0)) * 1000.0))
    ended_at = _utc_now_iso()
    parts: list[str] = [
        f"- {ended_at}",
        "event=end",
        f"tool={tool_name}",
        f"trace={trace_id}",
        f"state={state}",
        f"elapsed_ms={elapsed_ms}",
    ]
    if code:
        parts.append(f"code={compact_text(str(code), max_len=48)}")
    if message:
        parts.append(f"msg={compact_text(str(message), max_len=180)}")
    append_ops_line(" ".join(parts))
    return elapsed_ms


def instrument_tool(tool_name: str):
    def _decorator(fn):
        sig = inspect.signature(fn)

        @wraps(fn)
        def _wrapped(*args: Any, **kwargs: Any):
            trace_id = new_trace_id()
            start = log_tool_start(tool_name=tool_name, trace_id=trace_id)
            try:
                res = fn(*args, **kwargs)
                state = "ok"
                code = None
                message = None
                if isinstance(res, dict):
                    state = str(res.get("state") or "ok")
                    code = res.get("code")
                    message = res.get("message")
                    res.setdefault("trace_id", trace_id)
                elapsed_ms = log_tool_end(
                    tool_name=tool_name,
                    trace_id=trace_id,
                    start_monotonic=start,
                    state=state,
                    code=str(code) if code is not None else None,
                    message=str(message) if message is not None else None,
                )
                record_call(tool=tool_name, state=state, elapsed_ms=elapsed_ms)
                if isinstance(res, dict):
                    res.setdefault("elapsed_ms", elapsed_ms)
                return res
            except Exception as exc:
                elapsed_ms = log_tool_end(
                    tool_name=tool_name,
                    trace_id=trace_id,
                    start_monotonic=start,
                    state="error",
                    code=exc.__class__.__name__,
                    message=str(exc),
                )
                record_call(tool=tool_name, state="error", elapsed_ms=elapsed_ms)
                return {
                    "state": "error",
                    "trace_id": trace_id,
                    "code": exc.__class__.__name__,
                    "message": str(exc),
                    "elapsed_ms": elapsed_ms,
                }

        _wrapped.__signature__ = sig
        return _wrapped

    return _decorator

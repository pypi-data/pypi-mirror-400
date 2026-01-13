from __future__ import annotations

import statistics
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


_LOCK = threading.Lock()
_MAX_ITEMS = 200
_CALLS: list[dict[str, Any]] = []


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_call(*, tool: str, state: str, elapsed_ms: int) -> None:
    entry = {"ts": _utc_now_iso(), "tool": str(tool), "state": str(state), "elapsed_ms": int(elapsed_ms)}
    with _LOCK:
        _CALLS.append(entry)
        if len(_CALLS) > _MAX_ITEMS:
            del _CALLS[: len(_CALLS) - _MAX_ITEMS]


def _percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    if len(values) == 1:
        return int(values[0])
    p = max(0.0, min(float(p), 100.0))
    xs = sorted(int(v) for v in values)
    k = (len(xs) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    if f == c:
        return int(xs[f])
    d = k - f
    return int(round(xs[f] + (xs[c] - xs[f]) * d))


def snapshot(*, last_n: int = 50) -> dict[str, Any]:
    with _LOCK:
        calls = list(_CALLS[-max(0, int(last_n)) :])
        all_calls = list(_CALLS)

    by_tool: dict[str, list[int]] = {}
    for c in all_calls:
        tool = str(c.get("tool") or "")
        if not tool:
            continue
        by_tool.setdefault(tool, []).append(int(c.get("elapsed_ms") or 0))

    stats: dict[str, Any] = {}
    for tool, values in by_tool.items():
        stats[tool] = {
            "count": len(values),
            "p50_ms": _percentile(values, 50),
            "p95_ms": _percentile(values, 95),
            "max_ms": max(values) if values else 0,
        }

    return {"by_tool": stats, "last": calls}


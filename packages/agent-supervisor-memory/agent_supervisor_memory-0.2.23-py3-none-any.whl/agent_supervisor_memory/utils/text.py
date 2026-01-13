from __future__ import annotations

from typing import Any

from .env import env_bool, env_first


def compact_text(text: str, *, max_len: int) -> str:
    normalized = " ".join((text or "").strip().split())
    if max_len > 0 and len(normalized) > max_len:
        return normalized[: max_len - 1] + "…"
    return normalized


def truncate_tail_text(text: str | None, *, max_chars: int = 4000) -> str | None:
    if text is None:
        return None
    if max_chars > 0 and len(text) > max_chars:
        return text[: max_chars - 1] + "…"
    return text


def normalize_verbosity(raw: Any, *, default: str = "tail") -> str:
    if raw is None:
        return default
    norm = str(raw).strip().lower()
    if norm in {"full", "debug", "verbose"}:
        return "full"
    if norm in {"tail", "minimal", "quiet", "default"}:
        return "tail"
    return default


def get_verbosity(options: dict[str, Any] | None, *, default: str = "tail") -> str:
    if env_bool("AGENT_SUPERVISOR_MEMORY_VERBOSE", False) or env_bool("SUPERVISOR_MEMORY_VERBOSE", False):
        return "full"

    env_verbosity = env_first(
        ["AGENT_SUPERVISOR_MEMORY_VERBOSITY", "SUPERVISOR_MEMORY_VERBOSITY"],
        default=None,
    )
    if env_verbosity:
        return normalize_verbosity(env_verbosity, default=default)

    if options:
        if options.get("verbose") is True:
            return "full"
        if "verbosity" in options:
            return normalize_verbosity(options.get("verbosity"), default=default)

    return default

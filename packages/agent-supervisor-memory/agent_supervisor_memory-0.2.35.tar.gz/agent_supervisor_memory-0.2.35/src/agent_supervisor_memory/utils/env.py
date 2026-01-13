from __future__ import annotations

import os
from typing import Iterable


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(str(raw).strip())
    except ValueError:
        return default


def env_first(names: Iterable[str], default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    return default


def env_bool_first(names: Iterable[str], default: bool) -> bool:
    for name in names:
        if os.getenv(name) is not None:
            return env_bool(name, default)
    return default


def env_int_first(names: Iterable[str], default: int) -> int:
    for name in names:
        if os.getenv(name) is not None:
            return env_int(name, default)
    return default

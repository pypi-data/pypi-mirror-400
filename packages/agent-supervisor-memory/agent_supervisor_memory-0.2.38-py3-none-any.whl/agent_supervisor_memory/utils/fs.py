from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def find_ancestor_with_child_dir(start: Path, child_dir_name: str) -> Path | None:
    for p in [start, *start.parents]:
        if (p / child_dir_name).is_dir():
            return p
    return None


def project_codex_path(filename: str) -> Path:
    cwd = Path.cwd().resolve()
    root = find_ancestor_with_child_dir(cwd, ".codex") or cwd
    return root / ".codex" / filename


def codex_path_for(start: Path, filename: str) -> Path:
    """
    Resolve <root>/.codex/<filename> for an arbitrary start path.

    Root selection:
      1) nearest ancestor containing .codex/
      2) fallback to start (resolved)
    """
    try:
        start = Path(start).expanduser().resolve()
    except Exception:
        start = Path.cwd().resolve()
    root = find_ancestor_with_child_dir(start, ".codex") or start
    return root / ".codex" / filename


def global_codex_path(filename: str) -> Path:
    return Path.home() / ".codex" / filename


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

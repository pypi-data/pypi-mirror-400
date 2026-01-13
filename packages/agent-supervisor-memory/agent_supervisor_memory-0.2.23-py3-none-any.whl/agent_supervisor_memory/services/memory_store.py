"""
JSON-based keyword-searchable memory store.

JsonMemoryStore:
  - Stores entries as JSON in a single file (path configurable)
  - Each entry: id (uuid), key (namespace), content, tags, source, created_at
  - Auto-trimming: FIFO (oldest first) if max_items or max_bytes limits exceeded
  - Atomic writes: uses tmp file + rename to prevent corruption

Search API:
  - put(key, content, tags, source) -> item dict
  - search(query, key=None, tags_any=None, tags_all=None, top_k=10, mode="AND") -> scored results
  - delete_by_id(item_id) -> deleted count
  - load_items() -> full list of stored items

Query modes:
  - "AND": all tokens must match in content (strict matching)
  - "OR": any token must match (relaxed matching)

Storage format:
  - memory.json: {"version": 1, "items": [{id, key, tags, content, source, created_at}, ...]}
  - Limits enforced by config (max_items, max_bytes)

Usage:
  1. config = MemoryConfig(path=Path(...), max_items=500, max_bytes=2_000_000)
  2. store = JsonMemoryStore(config)
  3. item = store.put(key="project-x", content="Found bug in auth", tags=["bug", "critical"])
  4. results = store.search(query="auth bug", mode="AND", top_k=5)
  5. store.delete_by_id(item['id'])
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..utils.fs import atomic_write_json


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "items": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "items": [], "corrupt": True}


def _tokenize(query: str) -> list[str]:
    if not query:
        return []
    parts = re.split(r"[\s,.;:，。；：/\\|()\[\]{}<>\"'`~!@#$%^&*+=?-]+", query)
    tokens = [p.strip() for p in parts if p and p.strip()]
    filtered: list[str] = []
    for t in tokens:
        if len(t) <= 1 and t.isascii():
            continue
        filtered.append(t)
    return filtered


@dataclass(frozen=True)
class MemoryConfig:
    path: Path
    max_items: int
    max_bytes: int


class JsonMemoryStore:
    """
    JSON-based memory store with keyword search and tag filtering.

    Thread-unsafe on its own; memory tools wrap it with external locks to serialize access. Stores all entries in a
    single JSON file.
    Auto-trims entries (FIFO) if max_items or max_bytes limits exceeded.
    """

    def __init__(self, config: MemoryConfig):
        self._config = config

    @property
    def path(self) -> Path:
        return self._config.path

    def _load(self) -> dict[str, Any]:
        data = _read_json(self._config.path)
        if not isinstance(data, dict):
            data = {"version": 1, "items": []}
        items = data.get("items")
        if not isinstance(items, list):
            data["items"] = []
        data.setdefault("version", 1)
        return data

    def load_items(self) -> list[dict[str, Any]]:
        data = self._load()
        items = data.get("items")
        return items if isinstance(items, list) else []

    def _persist(self, data: dict[str, Any]) -> None:
        atomic_write_json(self._config.path, data)

    def _trim(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self._config.max_items > 0 and len(items) > self._config.max_items:
            items = items[-self._config.max_items :]

        if self._config.max_bytes > 0:
            while items:
                encoded = json.dumps({"version": 1, "items": items}, ensure_ascii=False).encode("utf-8")
                if len(encoded) <= self._config.max_bytes:
                    break
                items = items[1:]
        return items

    def put(
        self,
        *,
        key: str,
        content: str,
        tags: list[str] | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        """
        Store a memory entry.

        Args:
            key: Namespace key for grouping (e.g., "project-x", "task-1234")
            content: Memory text (auto-trimmed if storage limits exceeded)
            tags: Optional list of labels for categorization (e.g., ["bug", "critical", "auth"])
            source: Optional source identifier (e.g., "conversation-123", "meeting-notes")

        Returns:
            dict with item metadata (id, key, tags, content, source, created_at)
        """
        data = self._load()
        items: list[dict[str, Any]] = data["items"]

        item_id = uuid.uuid4().hex
        item = {
            "id": item_id,
            "key": key,
            "tags": sorted({t.strip() for t in (tags or []) if t and t.strip()}),
            "content": content,
            "source": source,
            "created_at": _utc_now_iso(),
        }
        items.append(item)
        data["items"] = self._trim(items)
        self._persist(data)
        return item

    def delete_by_id(self, item_id: str) -> dict[str, Any]:
        data = self._load()
        items: list[dict[str, Any]] = data["items"]
        before = len(items)
        items = [it for it in items if it.get("id") != item_id]
        data["items"] = items
        self._persist(data)
        return {"deleted": before - len(items)}

    def search(
        self,
        *,
        query: str,
        key: str | None = None,
        tags_any: list[str] | None = None,
        tags_all: list[str] | None = None,
        top_k: int = 10,
        mode: str = "AND",
    ) -> dict[str, Any]:
        """
        Search memory entries by keyword, key filter, and/or tag filters.

        Args:
            query: Search keywords (tokenized automatically; punctuation removed)
            key: Optional namespace filter (return only items with this key)
            tags_any: Optional "OR" tag filter (item must have at least one of these tags)
            tags_all: Optional "AND" tag filter (item must have all of these tags)
            top_k: Max results to return (sorted by score, then recency); 0 = unlimited
            mode: Search mode ("AND" = all tokens must match, "OR" = any token matches)

        Returns:
            dict with query, tokens, mode, items (scored results, sorted by relevance + recency)
        """
        data = self._load()
        items: list[dict[str, Any]] = data["items"]

        tokens = _tokenize(query)
        tags_any_set = {t.strip() for t in (tags_any or []) if t and t.strip()}
        tags_all_set = {t.strip() for t in (tags_all or []) if t and t.strip()}
        mode_norm = (mode or "AND").upper()
        if mode_norm not in {"AND", "OR"}:
            mode_norm = "AND"

        def match_item(it: dict[str, Any]) -> tuple[bool, int]:
            if key is not None and it.get("key") != key:
                return False, 0
            it_tags = set(it.get("tags") or [])
            if tags_any_set and not (it_tags & tags_any_set):
                return False, 0
            if tags_all_set and not tags_all_set.issubset(it_tags):
                return False, 0
            content = str(it.get("content") or "")
            if not tokens:
                return True, 0
            hits = [t for t in tokens if t in content]
            if mode_norm == "AND" and len(hits) != len(tokens):
                return False, 0
            if mode_norm == "OR" and not hits:
                return False, 0
            return True, len(hits)

        matched: list[dict[str, Any]] = []
        for it in items:
            ok, score = match_item(it)
            if not ok:
                continue
            matched.append({**it, "score": score})

        matched.sort(key=lambda x: (x.get("score", 0), x.get("created_at", "")), reverse=True)
        if top_k and top_k > 0:
            matched = matched[:top_k]
        return {"query": query, "tokens": tokens, "mode": mode_norm, "items": matched}

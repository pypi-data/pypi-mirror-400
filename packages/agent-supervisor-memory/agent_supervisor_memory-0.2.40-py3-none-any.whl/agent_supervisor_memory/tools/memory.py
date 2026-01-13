from __future__ import annotations

from datetime import datetime, timezone
import threading
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..services.memory_store import JsonMemoryStore
from ..utils.fs import atomic_write_json
from ..utils.ops_log import instrument_tool
from ..utils.text import compact_text


_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()


def _lock_key_for_mcp(mcp: FastMCP) -> str:
    for attr in ("app_id", "appId", "name", "id"):
        value = getattr(mcp, attr, None)
        if value:
            return str(value)
    return "default"


def _get_lock(key: str) -> threading.Lock:
    with _LOCKS_GUARD:
        if key not in _LOCKS:
            _LOCKS[key] = threading.Lock()
        return _LOCKS[key]


def _classify_memory_line(line: str) -> str:
    lower = line.lower()
    if any(k in lower for k in ["不要", "禁止", "avoid", "do not", "don't", "never"]):
        return "constraints"
    if any(k in lower for k in ["prefer", "推荐", "建议", "默认", "倾向", "喜欢", "best practice"]):
        return "preferences"
    if any(k in lower for k in ["error", "bug", "坑", "踩", "failed", "失败", "异常", "风险"]):
        return "pitfalls"
    if lower.startswith(("git ", "kubectl ", "helm ", "docker ", "npm ", "pnpm ", "yarn ", "python ", "poetry ", "uv ")):
        return "commands"
    return "notes"


def register_memory_tools(
    mcp: FastMCP,
    *,
    memory_store: JsonMemoryStore | None,
    memory_enabled_default: bool,
    effective_enabled,
) -> None:
    lock = _get_lock(_lock_key_for_mcp(mcp))

    @mcp.tool(
        name="memory_put",
        description="Store a memory entry with key, content, and optional tags. Entries are auto-trimmed (FIFO) when storage limits (max_items/max_bytes) are exceeded.",
    )
    @instrument_tool("memory_put")
    def memory_put(
        *,
        key: str,
        content: str,
        tags: list[str] | None = None,
        source: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_memory", default=memory_enabled_default)
        if not enabled or memory_store is None:
            return {"state": "disabled"}
        with lock:
            item = memory_store.put(key=key, content=content, tags=tags, source=source)
        return {"item": {k: item.get(k) for k in ("id", "key", "tags", "created_at") if k in item}}

    @mcp.tool(
        name="memory_search",
        description="Search memory entries by keyword (AND/OR mode), key filter, and/or tag filters. Returns scored results sorted by relevance and recency.",
    )
    @instrument_tool("memory_search")
    def memory_search(
        *,
        query: str,
        key: str | None = None,
        tags_any: list[str] | None = None,
        tags_all: list[str] | None = None,
        top_k: int = 10,
        mode: str = "AND",
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_memory", default=memory_enabled_default)
        if not enabled or memory_store is None:
            return {"state": "disabled", "items": []}
        with lock:
            result = memory_store.search(
                query=query, key=key, tags_any=tags_any, tags_all=tags_all, top_k=top_k, mode=mode
            )
        items = result.get("items") if isinstance(result, dict) else None
        if not isinstance(items, list):
            items = []
        simplified: list[dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            simplified.append(
                {
                    "id": it.get("id"),
                    "key": it.get("key"),
                    "tags": it.get("tags") or [],
                    "score": it.get("score"),
                    "content": compact_text(str(it.get("content") or ""), max_len=280),
                }
            )
        return {"items": simplified}

    @mcp.tool(
        name="memory_delete",
        description="Delete a memory entry by ID. Returns count of deleted items.",
    )
    @instrument_tool("memory_delete")
    def memory_delete(
        *,
        id: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_memory", default=memory_enabled_default)
        if not enabled or memory_store is None:
            return {"state": "disabled", "deleted": 0}
        with lock:
            return memory_store.delete_by_id(id)

    @mcp.tool(
        name="memory_compact",
        description="Generate profile.json from memory.json: deduplicate entries, classify by topic (constraints/preferences/pitfalls/commands/notes), and create a lightweight summary.",
    )
    @instrument_tool("memory_compact")
    def memory_compact(
        *,
        key: str | None = None,
        max_len: int = 240,
        max_items_per_key: int = 50,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_memory", default=memory_enabled_default)
        if not enabled or memory_store is None:
            return {"state": "disabled"}

        with lock:
            items = memory_store.load_items()
            source_path = memory_store.path
        if key:
            items = [it for it in items if it.get("key") == key]

        by_key: dict[str, list[dict[str, Any]]] = {}
        for it in items:
            k = str(it.get("key") or "")
            if not k:
                continue
            by_key.setdefault(k, []).append(it)

        profile: dict[str, Any] = {
            "version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": {"memory_path": str(source_path), "item_count": len(items)},
            "keys": {},
        }

        for k, group in by_key.items():
            buckets: dict[str, list[str]] = {"preferences": [], "constraints": [], "pitfalls": [], "commands": [], "notes": []}
            seen: set[str] = set()
            for it in reversed(group):
                content = str(it.get("content") or "").strip()
                if not content:
                    continue
                for raw_line in content.splitlines():
                    line = compact_text(raw_line, max_len=max_len)
                    if not line:
                        continue
                    if line in seen:
                        continue
                    seen.add(line)
                    bucket = _classify_memory_line(line)
                    buckets[bucket].append(line)

            for bucket_name in list(buckets.keys()):
                if max_items_per_key > 0:
                    buckets[bucket_name] = buckets[bucket_name][:max_items_per_key]

            profile["keys"][k] = buckets

        profile_path = source_path.with_name("profile.json")
        atomic_write_json(profile_path, profile)

        return {"profile_path": str(profile_path), "keys": sorted(profile["keys"].keys())}

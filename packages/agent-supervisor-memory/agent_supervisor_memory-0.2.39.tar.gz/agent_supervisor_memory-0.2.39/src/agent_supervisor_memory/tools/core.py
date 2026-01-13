from __future__ import annotations

from pathlib import Path
from typing import Any

import time

from ..services.policy import AgentPolicy
from ..utils.metrics import snapshot as metrics_snapshot
from ..utils.ops_log import instrument_tool


def register_core_tools(
    mcp,
    *,
    app_id: str,
    dispatch_enabled_default: bool,
    resolved_dispatch_base_dir: str | Path,
    memory_enabled_default: bool,
    resolved_memory_path: str | Path,
    memory_max_items: int,
    memory_max_bytes: int,
    subagents_enabled_default: bool,
    policy_enabled_default: bool,
    resolved_policy_path: str | Path | None,
    agent_policy: AgentPolicy,
    global_memory: bool,
    global_policy: bool,
) -> None:
    memory_mode = "disabled" if not memory_enabled_default else ("global" if global_memory else "project")
    policy_mode = "disabled" if not policy_enabled_default else ("global" if global_policy else "project")
    dispatch_base_dir = str(resolved_dispatch_base_dir)
    memory_path = str(resolved_memory_path)
    policy_path = str(resolved_policy_path) if resolved_policy_path else None

    @mcp.tool(
        name="capabilities_get",
        description="Introspect server capabilities, enabled modules, and storage paths. Returns configuration for memory, dispatch, policy, and workflow modules.",
    )
    @instrument_tool("capabilities_get")
    def capabilities_get() -> dict[str, Any]:
        return {
            "server": {"name": app_id, "transport": "stdio"},
            "dispatch": {"enabled": dispatch_enabled_default, "jobs_dir": dispatch_base_dir, "layout": "bucketed"},
            "memory": {
                "enabled": memory_enabled_default,
                "mode": memory_mode,
                "storage": "json",
                "path": memory_path,
                "global": global_memory,
                "max_items": memory_max_items,
                "max_bytes": memory_max_bytes,
            },
            "subagents": {"enabled": subagents_enabled_default},
            "workflow": {"enabled": True},
            "policy": {
                "enabled": policy_enabled_default,
                "mode": policy_mode,
                "path": policy_path,
                "global": global_policy,
                "version": agent_policy.version,
            },
            "options": {"enable_memory": True, "enable_subagents": True},
        }

    @mcp.tool(
        name="health_get",
        description="Fast health check for the MCP server (no disk I/O).",
    )
    @instrument_tool("health_get")
    def health_get() -> dict[str, Any]:
        return {"state": "ok", "server": app_id, "ts": int(time.time())}

    @mcp.tool(
        name="policy_get",
        description="Retrieve the agent routing policy (supervisor/coder model assignments, effort levels, auto-routing rules). Defaults to DEFAULT_POLICY if not explicitly configured.",
    )
    @instrument_tool("policy_get")
    def policy_get() -> dict[str, Any]:
        if not policy_enabled_default:
            return {"state": "disabled"}
        return {"policy": agent_policy.raw}

    @mcp.tool(
        name="metrics_get",
        description="Get recent per-tool latency metrics (p50/p95/max) and last N calls for timeout diagnosis.",
    )
    @instrument_tool("metrics_get")
    def metrics_get(*, last_n: int = 50) -> dict[str, Any]:
        return {"state": "ok", **metrics_snapshot(last_n=int(last_n or 50))}

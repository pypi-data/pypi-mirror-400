from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..services.policy import AgentPolicy, route_models
from ..services.workflow_spec import ensure_spec
from ..utils.ops_log import instrument_tool


def register_workflow_tools(
    mcp: FastMCP,
    *,
    agent_policy: AgentPolicy,
    subagents_enabled_default: bool,
    effective_enabled,
) -> None:
    @mcp.tool(
        name="workflow_route",
        description="Route a task to recommended supervisor/coder models and effort level based on task text and policy. Auto-detects task mode (lite/spike/heavy) and applies policy routing rules.",
    )
    @instrument_tool("workflow_route")
    def workflow_route(
        *,
        task_text: str,
        mode: str | None = None,
        effort: str | None = None,
        auto: bool = True,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        route = route_models(policy=agent_policy, task_text=task_text, mode=mode, effort=effort, auto=auto)
        return {
            "workflow_mode": route.get("workflow_mode"),
            "effort": route.get("effort"),
            "supervisor_model": route.get("supervisor_model"),
            "coder_model": route.get("coder_model"),
        }

    @mcp.tool(
        name="workflow_ensure_spec",
        description="Infer task specification (mode, goal, constraints, acceptance criteria) from task text. Returns minimal spec for lite/spike/heavy tasks to guide planning and implementation.",
    )
    @instrument_tool("workflow_ensure_spec")
    def workflow_ensure_spec(
        *,
        task_text: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        res = ensure_spec(task_text, policy=agent_policy)
        return res.spec

    @mcp.tool(
        name="subagents_echo",
        description="Placeholder tool for subagent validation. Simply echoes back the input text when subagents module is enabled.",
    )
    @instrument_tool("subagents_echo")
    def subagents_echo(
        *,
        text: str,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        enabled = effective_enabled(options, field="enable_subagents", default=subagents_enabled_default)
        if not enabled:
            return {"state": "disabled"}
        return {"text": text}

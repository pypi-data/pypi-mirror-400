from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import ServerConfig, effective_enabled, resolve_server_config
from .services.memory_store import JsonMemoryStore, MemoryConfig as MemoryStoreConfig
from .services.policy import DEFAULT_POLICY, AgentPolicy, load_policy
from .tools.core import register_core_tools
from .tools.dispatch import register_dispatch_tools
from .tools.memory import register_memory_tools
from .tools.projects import register_project_tools
from .tools.workflow import register_workflow_tools
from .utils.text import get_verbosity


def build_server(
    *,
    dispatch_dir: str | None = None,
    memory_path: str | None = None,
    policy_path: str | None = None,
    global_memory: bool = False,
    global_policy: bool = False,
    dispatch_enabled: bool | None = None,
    policy_enabled: bool | None = None,
    memory_enabled: bool | None = None,
    subagents_enabled: bool | None = None,
    config: ServerConfig | None = None,
) -> FastMCP:
    """Build and return a FastMCP server with workflow + memory + dispatch tools."""
    resolved_config = config or resolve_server_config(
        dispatch_dir=dispatch_dir,
        memory_path=memory_path,
        policy_path=policy_path,
        global_memory=global_memory,
        global_policy=global_policy,
        dispatch_enabled=dispatch_enabled,
        policy_enabled=policy_enabled,
        memory_enabled=memory_enabled,
        subagents_enabled=subagents_enabled,
    )

    app_id = "agent-supervisor-memory"
    mcp = FastMCP(app_id)

    memory_store: JsonMemoryStore | None = None
    if resolved_config.memory.enabled:
        memory_store = JsonMemoryStore(
            MemoryStoreConfig(
                path=resolved_config.memory.path,
                max_items=resolved_config.memory.max_items,
                max_bytes=resolved_config.memory.max_bytes,
            )
        )

    agent_policy: AgentPolicy
    if resolved_config.policy.enabled and resolved_config.policy.path:
        agent_policy = load_policy(resolved_config.policy.path)
    else:
        agent_policy = AgentPolicy(version=int(DEFAULT_POLICY.get("version") or 1), raw=DEFAULT_POLICY)

    register_core_tools(
        mcp,
        app_id=app_id,
        dispatch_enabled_default=resolved_config.dispatch.enabled,
        resolved_dispatch_base_dir=resolved_config.dispatch.base_dir,
        memory_enabled_default=resolved_config.memory.enabled,
        resolved_memory_path=resolved_config.memory.path,
        memory_max_items=resolved_config.memory.max_items,
        memory_max_bytes=resolved_config.memory.max_bytes,
        subagents_enabled_default=resolved_config.subagents_enabled,
        policy_enabled_default=resolved_config.policy.enabled,
        resolved_policy_path=resolved_config.policy.path,
        agent_policy=agent_policy,
        global_memory=resolved_config.memory.global_scope,
        global_policy=resolved_config.policy.global_scope,
    )

    register_dispatch_tools(
        mcp,
        dispatch_base_dir=resolved_config.dispatch.base_dir,
        dispatch_enabled_default=resolved_config.dispatch.enabled,
        get_verbosity=get_verbosity,
        effective_enabled=effective_enabled,
    )
    register_project_tools(
        mcp,
        dispatch_base_dir=resolved_config.dispatch.base_dir,
        dispatch_enabled_default=resolved_config.dispatch.enabled,
        get_verbosity=get_verbosity,
        effective_enabled=effective_enabled,
    )
    register_memory_tools(
        mcp,
        memory_store=memory_store,
        memory_enabled_default=resolved_config.memory.enabled,
        effective_enabled=effective_enabled,
    )
    register_workflow_tools(
        mcp,
        agent_policy=agent_policy,
        subagents_enabled_default=resolved_config.subagents_enabled,
        effective_enabled=effective_enabled,
    )

    return mcp

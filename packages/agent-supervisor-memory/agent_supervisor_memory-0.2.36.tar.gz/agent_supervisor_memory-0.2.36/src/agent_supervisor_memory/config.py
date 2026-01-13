from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils.env import env_bool_first, env_first, env_int_first
from .utils.fs import global_codex_path, project_codex_path

DEFAULT_MEMORY_MAX_ITEMS = 500
DEFAULT_MEMORY_MAX_BYTES = 2_000_000


@dataclass(frozen=True)
class DispatchSettings:
    enabled: bool
    base_dir: Path


@dataclass(frozen=True)
class MemorySettings:
    enabled: bool
    path: Path
    max_items: int
    max_bytes: int
    global_scope: bool


@dataclass(frozen=True)
class PolicySettings:
    enabled: bool
    path: Path | None
    global_scope: bool


@dataclass(frozen=True)
class ServerConfig:
    dispatch: DispatchSettings
    memory: MemorySettings
    policy: PolicySettings
    subagents_enabled: bool


def _resolve_enabled(cli_value: bool | None, env_names: list[str], default: bool) -> bool:
    if cli_value is not None:
        return bool(cli_value)
    return env_bool_first(env_names, default)


def resolve_server_config(
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
) -> ServerConfig:
    dispatch_dir_value = dispatch_dir or env_first(
        ["AGENT_SUPERVISOR_MEMORY_DISPATCH_DIR", "MCP_DISPATCH_DIR"],
        default=str(project_codex_path("codex-dispatch")),
    )
    if not dispatch_dir_value:
        dispatch_dir_value = str(project_codex_path("codex-dispatch"))

    dispatch_config = DispatchSettings(
        enabled=_resolve_enabled(
            dispatch_enabled,
            ["AGENT_SUPERVISOR_MEMORY_DISPATCH_ENABLED", "MCP_DISPATCH_ENABLED"],
            True,
        ),
        base_dir=Path(dispatch_dir_value).expanduser(),
    )

    memory_enabled_default = _resolve_enabled(
        memory_enabled,
        ["AGENT_SUPERVISOR_MEMORY_MEMORY_ENABLED", "MCP_MEMORY_ENABLED"],
        True,
    )
    default_memory_path = global_codex_path("memory.json") if global_memory else project_codex_path("memory.json")
    resolved_memory_path = Path(
        memory_path
        or env_first(
            ["AGENT_SUPERVISOR_MEMORY_MEMORY_PATH", "MCP_MEMORY_PATH"],
            default=str(default_memory_path),
        )
    ).expanduser()
    memory_config = MemorySettings(
        enabled=memory_enabled_default,
        path=resolved_memory_path,
        max_items=env_int_first(
            ["AGENT_SUPERVISOR_MEMORY_MEMORY_MAX_ITEMS", "MCP_MEMORY_MAX_ITEMS"],
            DEFAULT_MEMORY_MAX_ITEMS,
        ),
        max_bytes=env_int_first(
            ["AGENT_SUPERVISOR_MEMORY_MEMORY_MAX_BYTES", "MCP_MEMORY_MAX_BYTES"],
            DEFAULT_MEMORY_MAX_BYTES,
        ),
        global_scope=bool(global_memory),
    )

    policy_enabled_default = _resolve_enabled(
        policy_enabled,
        ["AGENT_SUPERVISOR_MEMORY_POLICY_ENABLED", "MCP_POLICY_ENABLED"],
        True,
    )
    default_policy_path = global_codex_path("agent-policy.json") if global_policy else project_codex_path("agent-policy.json")
    resolved_policy_path = Path(
        policy_path
        or env_first(
            [
                "AGENT_SUPERVISOR_MEMORY_POLICY_PATH",
                "MCP_POLICY_PATH",
                "MCP_AGENT_POLICY_PATH",
            ],
            default=str(default_policy_path),
        )
    ).expanduser()

    policy_config = PolicySettings(
        enabled=policy_enabled_default,
        path=resolved_policy_path if policy_enabled_default else None,
        global_scope=bool(global_policy),
    )

    subagents_enabled_default = _resolve_enabled(
        subagents_enabled,
        ["AGENT_SUPERVISOR_MEMORY_SUBAGENTS_ENABLED", "MCP_SUBAGENTS_ENABLED"],
        True,
    )

    return ServerConfig(
        dispatch=dispatch_config,
        memory=memory_config,
        policy=policy_config,
        subagents_enabled=subagents_enabled_default,
    )


def effective_enabled(options: dict[str, Any] | None, *, field: str, default: bool) -> bool:
    if not options:
        return default
    value = options.get(field)
    if value is None:
        return default
    return bool(value)

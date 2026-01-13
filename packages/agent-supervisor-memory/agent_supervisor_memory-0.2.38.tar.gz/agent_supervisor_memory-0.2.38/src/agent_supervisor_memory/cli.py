from __future__ import annotations

import argparse

from .config import resolve_server_config
from .server import build_server


def main() -> None:
    parser = argparse.ArgumentParser(prog="agent-supervisor-memory")
    parser.add_argument("--transport", default="stdio", choices=["stdio"], help="MCP transport")
    parser.add_argument(
        "--dispatch-dir",
        default=None,
        help="Base directory for codex dispatch jobs (default: <project>/.codex/codex-dispatch; or set AGENT_SUPERVISOR_MEMORY_DISPATCH_DIR / MCP_DISPATCH_DIR).",
    )
    parser.add_argument("--memory-path", default=None, help="Override memory.json path")
    parser.add_argument("--policy-path", default=None, help="Override agent-policy.json path")
    parser.add_argument("--global-memory", action="store_true", help="Use global ~/.codex/memory.json")
    parser.add_argument("--global-policy", action="store_true", help="Use global ~/.codex/agent-policy.json")
    parser.add_argument(
        "--dispatch",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_enabled",
        help="Enable/disable codex dispatch tools (default: enabled)",
    )
    parser.add_argument(
        "--policy",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="policy_enabled",
        help="Enable/disable policy tools & routing hints (default: enabled)",
    )
    parser.add_argument(
        "--memory",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="memory_enabled",
        help="Enable/disable memory tools (default: enabled)",
    )
    parser.add_argument(
        "--subagents",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="subagents_enabled",
        help="Enable/disable subagents tools (default: enabled)",
    )
    # Backward-compat aliases (not documented).
    parser.add_argument("--memory-global", dest="global_memory", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--policy-global", dest="global_policy", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        config = resolve_server_config(
            dispatch_dir=args.dispatch_dir,
            memory_path=args.memory_path,
            policy_path=args.policy_path,
            global_memory=bool(args.global_memory),
            global_policy=bool(args.global_policy),
            dispatch_enabled=args.dispatch_enabled,
            policy_enabled=args.policy_enabled,
            memory_enabled=args.memory_enabled,
            subagents_enabled=args.subagents_enabled,
        )
    except ValueError as exc:
        parser.error(str(exc))

    server = build_server(config=config)
    server.run(transport=args.transport)

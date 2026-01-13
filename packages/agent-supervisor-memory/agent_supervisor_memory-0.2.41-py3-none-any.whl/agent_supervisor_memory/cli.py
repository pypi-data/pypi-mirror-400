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
        "--dispatch-prune-enabled",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_prune_enabled",
        help="Enable/disable dispatch job pruning (default: disabled)",
    )
    parser.add_argument(
        "--dispatch-prune-on-job-finish",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_prune_on_job_finish",
        help="Prune dispatch jobs after completion (default: enabled)",
    )
    parser.add_argument(
        "--dispatch-prune-on-startup",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_prune_on_startup",
        help="Prune dispatch jobs on server startup (default: disabled)",
    )
    parser.add_argument(
        "--dispatch-retain-max-jobs-per-bucket",
        default=None,
        type=int,
        dest="dispatch_retain_max_jobs_per_bucket",
        help="Maximum jobs to retain per bucket (default: 100)",
    )
    parser.add_argument(
        "--dispatch-retain-max-age-days",
        default=None,
        type=int,
        dest="dispatch_retain_max_age_days",
        help="Maximum age (days) to retain jobs (default: 7)",
    )
    parser.add_argument(
        "--dispatch-retain-keep-failed",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_retain_keep_failed",
        help="Keep failed jobs when pruning (default: enabled)",
    )
    parser.add_argument(
        "--dispatch-prune-dry-run",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_prune_dry_run",
        help="Run pruning without deleting files (default: disabled)",
    )
    parser.add_argument(
        "--dispatch-prune-verbose",
        default=None,
        action=argparse.BooleanOptionalAction,
        dest="dispatch_prune_verbose",
        help="Verbose logging for pruning (default: disabled)",
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
            dispatch_prune_enabled=args.dispatch_prune_enabled,
            dispatch_prune_on_job_finish=args.dispatch_prune_on_job_finish,
            dispatch_prune_on_startup=args.dispatch_prune_on_startup,
            dispatch_retain_max_jobs_per_bucket=args.dispatch_retain_max_jobs_per_bucket,
            dispatch_retain_max_age_days=args.dispatch_retain_max_age_days,
            dispatch_retain_keep_failed=args.dispatch_retain_keep_failed,
            dispatch_prune_dry_run=args.dispatch_prune_dry_run,
            dispatch_prune_verbose=args.dispatch_prune_verbose,
            policy_enabled=args.policy_enabled,
            memory_enabled=args.memory_enabled,
            subagents_enabled=args.subagents_enabled,
        )
    except ValueError as exc:
        parser.error(str(exc))

    server = build_server(config=config)
    server.run(transport=args.transport)

"""
Task specification inference: auto-detect task complexity and generate minimal spec.

Task modes:
  - lite: simple one-off fixes/small features (default if text is empty or does not trigger other rules)
  - spike: exploration/POC/feasibility validation (keyword-based)
  - heavy: complex/high-impact changes based on policy auto_rules (length/keywords)

ensure_spec() returns a spec dict with:
  - mode: lite/spike/heavy
  - goal: normalized task text
  - constraints: default best practices (small steps, closeable designs)
  - acceptance: minimum deliverables (MCP tools, minimal docs, sanity checks for spike/heavy)
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .policy import AgentPolicy, classify_workflow_mode


@dataclass(frozen=True)
class EnsureSpecResult:
    mode: str
    spec: dict


def ensure_spec(task_text: str, *, policy: AgentPolicy | None = None) -> EnsureSpecResult:
    """
    Infer task specification (mode + minimal spec) from task text.

    Auto-detects complexity via policy routing rules (lite/spike/heavy).

    Args:
        task_text: User task description

    Returns:
        EnsureSpecResult with mode and spec dict (goal, constraints, acceptance criteria)
    """
    mode = classify_workflow_mode(task_text, policy=policy)
    normalized = re.sub(r"\s+", " ", (task_text or "").strip())
    spec = {
        "spec_version": "v1",
        "mode": mode,
        "goal": normalized or "未提供任务描述",
        "non_goals": [],
        "constraints": ["尽量小步提交（变更要可验证）", "优先可关闭/可降级的设计"],
        "acceptance": ["提供可调用的 MCP tools", "具备最小可用的说明文档"],
        "questions": [],
    }
    if mode in {"spike", "heavy"}:
        spec["acceptance"].append("包含最小验证步骤（sanity checks）")
    return EnsureSpecResult(mode=mode, spec=spec)

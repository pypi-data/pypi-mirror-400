"""
Agent routing policy: supervisor/coder model assignments and effort levels.

DEFAULT_POLICY structure:
  - defaults: supervisor_model, coder_model, effort, mode (used if not overridden)
  - modes: preset effort overrides for mode names (e.g., "quality" -> high effort)
  - routing.auto_rules: heavy_keywords (list) and heavy_length threshold (int) for task classification

route_models() function:
  - Takes task_text, mode, effort, auto flags and policy
  - Returns supervisor_model, coder_model, workflow_mode (lite/spike/heavy), effort (low/medium/high)
  - Supports auto-detection of workflow_mode based on task text + policy rules
  - Fallback: if not configured, returns sensible defaults

Usage:
  1. Load policy with load_policy(path) or use DEFAULT_POLICY
  2. Call route_models(policy=..., task_text="...", mode=None, effort=None, auto=True)
  3. Use returned supervisor_model/coder_model for agent dispatch
  4. Use workflow_mode for acceptance criteria selection
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_POLICY: dict[str, Any] = {
    "version": 1,
    "defaults": {
        "supervisor_model": "codex-5.2",
        "coder_model": "gpt-5.1-codex-max",
        "effort": "medium",
        "mode": "auto",
    },
    "modes": {
        "efficient": {"effort": "medium"},
        "saving": {"effort": "medium"},
        "quality": {"effort": "high"},
    },
    "routing": {
        "auto_rules": {
            "heavy_keywords": [
                "auth",
                "payment",
                "security",
                "k8s",
                "kubernetes",
                "helm",
                "ci",
                "cicd",
                "deploy",
                "database",
                "权限",
                "支付",
                "安全",
                "部署",
                "数据库",
            ],
            "heavy_length": 300,
        }
    },
}

SPIKE_KEYWORDS: tuple[str, ...] = (
    "spike",
    "poc",
    "proof of concept",
    "调研",
    "验证可行性",
)


def _resolve_auto_rules(policy: AgentPolicy | None) -> dict[str, Any]:
    default_auto_rules = (DEFAULT_POLICY.get("routing") or {}).get("auto_rules") or {}
    policy_auto_rules = (policy.routing.get("auto_rules") or {}) if policy else {}

    def _resolve_heavy_length(value: Any) -> int | None:
        try:
            length = int(value)
        except (TypeError, ValueError):
            return None
        return length if length > 0 else None

    heavy_length = _resolve_heavy_length(policy_auto_rules.get("heavy_length"))
    if heavy_length is None:
        heavy_length = _resolve_heavy_length(default_auto_rules.get("heavy_length")) or 300

    heavy_keywords_raw = policy_auto_rules.get("heavy_keywords")
    if not heavy_keywords_raw:
        heavy_keywords_raw = default_auto_rules.get("heavy_keywords") or []

    return {
        "heavy_length": heavy_length,
        "heavy_keywords": [str(k).lower() for k in (heavy_keywords_raw or [])],
    }


@dataclass(frozen=True)
class AgentPolicy:
    version: int
    raw: dict[str, Any]

    @property
    def defaults(self) -> dict[str, Any]:
        return dict(self.raw.get("defaults") or {})

    @property
    def modes(self) -> dict[str, Any]:
        return dict(self.raw.get("modes") or {})

    @property
    def routing(self) -> dict[str, Any]:
        return dict(self.raw.get("routing") or {})


def load_policy(path: Path) -> AgentPolicy:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = DEFAULT_POLICY
    except FileNotFoundError:
        data = DEFAULT_POLICY
    except json.JSONDecodeError:
        data = {**DEFAULT_POLICY, "corrupt": True}

    version = int(data.get("version") or 1)
    return AgentPolicy(version=version, raw=data)


def classify_workflow_mode(task_text: str, *, policy: AgentPolicy | None) -> str:
    """
    Classify a task into lite/spike/heavy based on text and policy routing rules.
    """
    text = (task_text or "").strip()
    if not text:
        return "lite"

    lower = text.lower()
    if any(k in lower for k in SPIKE_KEYWORDS):
        return "spike"

    auto_rules = _resolve_auto_rules(policy)
    heavy_length = auto_rules["heavy_length"]
    heavy_keywords = auto_rules["heavy_keywords"]

    if len(text) >= heavy_length or any(k and k in lower for k in heavy_keywords):
        return "heavy"
    return "lite"


def route_models(
    *,
    policy: AgentPolicy,
    task_text: str,
    mode: str | None,
    effort: str | None,
    auto: bool,
) -> dict[str, Any]:
    """
    Route a task to recommended supervisor/coder models based on policy and task text.

    Args:
        policy: AgentPolicy instance (loaded from file or DEFAULT_POLICY)
        task_text: Task description for auto-detection and keyword matching
        mode: Optional mode override (lite/spike/heavy); if None and auto=True, auto-detected
        effort: Optional effort override (low/medium/high); if None, inferred from mode or defaults
        auto: If True, auto-detect workflow_mode from task_text + policy rules; if False, use mode as-is

    Returns:
        dict with:
          - workflow_mode: auto-detected complexity (lite/spike/heavy)
          - supervisor_model: recommended supervisor model from policy
          - coder_model: recommended coder model from policy
          - effort: resolved effort level (low/medium/high)
          - reason: explanation of routing decision (for debugging)
    """
    defaults = policy.defaults
    resolved_mode = (mode or defaults.get("mode") or "auto").strip().lower()
    resolved_effort = (effort or "").strip().lower() or None

    text = (task_text or "").strip()

    if auto or resolved_mode == "auto":
        workflow_mode = classify_workflow_mode(text, policy=policy)
    else:
        workflow_mode = resolved_mode

    mode_preset = policy.modes.get(resolved_mode) if resolved_mode in policy.modes else None
    if resolved_effort is None and isinstance(mode_preset, dict):
        resolved_effort = str(mode_preset.get("effort") or "").strip().lower() or None
    if resolved_effort is None:
        resolved_effort = str(defaults.get("effort") or "medium").strip().lower()
    if resolved_effort not in {"low", "medium", "high"}:
        resolved_effort = "medium"

    supervisor_model = str(defaults.get("supervisor_model") or "codex-5.2").strip()
    coder_model = str(defaults.get("coder_model") or "gpt-5.1-codex-max").strip()

    reason = f"workflow_mode={workflow_mode}, effort={resolved_effort}, mode={resolved_mode}, auto={bool(auto)}"
    return {
        "policy_version": policy.version,
        "workflow_mode": workflow_mode,
        "mode": resolved_mode,
        "effort": resolved_effort,
        "supervisor_model": supervisor_model,
        "coder_model": coder_model,
        "reason": reason,
    }

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

import yaml

from .drafts import lint_draft
from .errors import ChappeError, ExitCode


def load_policy(path: Path) -> dict[str, Any]:
    text = Path(path).expanduser().read_text()
    suffix = Path(path).suffix.lower()
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    elif suffix == ".json":
        data = json.loads(text)
    elif suffix == ".toml":
        data = tomllib.loads(text)
    else:
        try:
            data = yaml.safe_load(text)
        except Exception:
            data = json.loads(text)
    if not isinstance(data, dict):
        raise ChappeError("Automation policy must be an object.", ExitCode.USAGE_ERROR)
    return data


def validate_policy(policy: dict[str, Any], *, channel: str | None = None) -> dict[str, Any]:
    target = policy.get("channel") or policy.get("allowed_channel")
    if not target:
        raise ChappeError("Automation policy must include `channel`.", ExitCode.USAGE_ERROR)
    if channel and target != channel:
        raise ChappeError(
            f"Policy channel {target!r} does not match requested channel {channel!r}.",
            ExitCode.PERMISSION_DENIED,
        )
    if policy.get("enabled") is False:
        raise ChappeError("Automation policy is disabled.", ExitCode.PERMISSION_DENIED)
    agents = policy.get("allowed_agents") or policy.get("agents") or ["*"]
    if not isinstance(agents, list):
        raise ChappeError("Automation policy `allowed_agents` must be a list.", ExitCode.USAGE_ERROR)
    rate = policy.get("rate_limits", {})
    if rate and not isinstance(rate, dict):
        raise ChappeError("Automation policy `rate_limits` must be an object.", ExitCode.USAGE_ERROR)
    lint = policy.get("draft_lint", {})
    if lint and not isinstance(lint, dict):
        raise ChappeError("Automation policy `draft_lint` must be an object.", ExitCode.USAGE_ERROR)
    return {
        **policy,
        "channel": target,
        "enabled": True,
        "allowed_agents": agents,
        "rate_limits": rate,
        "draft_lint": lint,
    }


def assert_publish_allowed(
    policy: dict[str, Any] | None,
    *,
    channel: str,
    text: str,
    actor: str,
) -> dict[str, Any]:
    if not policy:
        raise ChappeError(
            f"No automation policy enabled for {channel}.",
            ExitCode.PERMISSION_DENIED,
            next_command=f"chappe automate enable {channel} --policy chappe.yaml",
        )
    validated = validate_policy(policy, channel=channel)
    agents = validated["allowed_agents"]
    if "*" not in agents and actor not in agents:
        raise ChappeError(
            f"Actor {actor!r} is not allowed to publish for {channel}.",
            ExitCode.PERMISSION_DENIED,
        )
    lint_cfg = validated.get("draft_lint", {})
    lint = lint_draft(text, max_chars=int(lint_cfg.get("max_chars", 4096)))
    if lint_cfg.get("require_lint_ok", True) and not lint["ok"]:
        raise ChappeError("Draft failed publish lint.", ExitCode.UNSAFE_MUTATION, details=lint)
    return {"policy": validated, "lint": lint}


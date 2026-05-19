from __future__ import annotations

import shutil
from importlib import resources
from pathlib import Path

from .errors import ChappeError, ExitCode


HOST_TARGETS = {
    "codex": ".codex/skills/chappe",
    "claude-code": ".claude/commands/chappe",
    "opencode": ".config/opencode/commands/chappe",
    "openclaw": ".openclaw/skills/chappe",
    "hermes": ".hermes/skills/chappe",
}


def _copy_children(src, target: Path) -> None:
    for child in src.iterdir():
        child_target = target / child.name
        if child.is_dir():
            if child_target.exists():
                shutil.rmtree(child_target)
            shutil.copytree(child, child_target)
        else:
            shutil.copy2(child, child_target)


def available_hosts() -> list[str]:
    return sorted(HOST_TARGETS)


def agent_installation_status(*, home: Path | None = None) -> list[dict[str, object]]:
    root = Path(home).expanduser() if home else Path.home()
    statuses = []
    for host in available_hosts():
        target = root / HOST_TARGETS[host]
        statuses.append(
            {
                "host": host,
                "target": str(target),
                "installed": target.exists() and any(target.iterdir()),
            }
        )
    return statuses


def install_agent_assets(host: str, *, dest: Path | None = None, force: bool = False) -> Path:
    if host not in HOST_TARGETS:
        raise ChappeError(
            f"Unknown agent host: {host}",
            ExitCode.USAGE_ERROR,
            details={"available_hosts": available_hosts()},
        )
    target = Path(dest).expanduser() if dest else Path.home() / HOST_TARGETS[host]
    if target.exists() and any(target.iterdir()) and not force:
        raise ChappeError(
            f"Target already exists and is not empty: {target}",
            ExitCode.USAGE_ERROR,
            next_command=f"chappe agent install {host} --force",
        )
    target.mkdir(parents=True, exist_ok=True)
    src = resources.files("chappe").joinpath("agent_assets", host)
    if host == "codex":
        _copy_children(src.joinpath("chappe"), target)
        shutil.copy2(src.joinpath("AGENTS.snippet.md"), target / "AGENTS.snippet.md")
    else:
        _copy_children(src, target)
    return target

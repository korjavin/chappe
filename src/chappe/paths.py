from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "chappe"


def home() -> Path:
    override = os.getenv("CHAPPE_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home()


def config_dir() -> Path:
    override = os.getenv("CHAPPE_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    if os.getenv("CHAPPE_HOME"):
        return home() / ".config" / APP_NAME
    xdg = os.getenv("XDG_CONFIG_HOME")
    return (Path(xdg).expanduser() if xdg else home() / ".config") / APP_NAME


def data_dir() -> Path:
    override = os.getenv("CHAPPE_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if os.getenv("CHAPPE_HOME"):
        return home() / ".local" / "share" / APP_NAME
    xdg = os.getenv("XDG_DATA_HOME")
    return (Path(xdg).expanduser() if xdg else home() / ".local" / "share") / APP_NAME


def state_dir() -> Path:
    override = os.getenv("CHAPPE_STATE_DIR")
    if override:
        return Path(override).expanduser()
    if os.getenv("CHAPPE_HOME"):
        return home() / ".local" / "state" / APP_NAME
    xdg = os.getenv("XDG_STATE_HOME")
    return (Path(xdg).expanduser() if xdg else home() / ".local" / "state") / APP_NAME


def default_config_path() -> Path:
    return config_dir() / "config.toml"

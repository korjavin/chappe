from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]

from . import paths
from .errors import ChappeError, ExitCode


def expand_env(value: str | None) -> str | None:
    if value is None:
        return None
    if value.startswith("${") and value.endswith("}"):
        return os.getenv(value[2:-1])
    return os.path.expandvars(value)


@dataclass(frozen=True)
class TelegramConfig:
    api_id: str | None
    api_hash: str | None
    database_encryption_key_env: str = "CHAPPE_TDLIB_KEY"
    database_encryption_key: str | None = None


@dataclass(frozen=True)
class StorageConfig:
    config_path: Path
    data_dir: Path
    state_dir: Path
    tdlib_dir: Path
    sqlite_path: Path
    audit_log_path: Path


@dataclass(frozen=True)
class DefaultsConfig:
    json: bool = True
    max_messages: int = 100
    default_period: str = "30d"
    default_channel: str | None = None


@dataclass(frozen=True)
class ChappeConfig:
    telegram: TelegramConfig
    storage: StorageConfig
    defaults: DefaultsConfig
    raw: dict[str, Any]

    @classmethod
    def load(cls, config_path: Path | None = None) -> "ChappeConfig":
        path = Path(config_path).expanduser() if config_path else paths.default_config_path()
        raw: dict[str, Any] = {}
        if path.exists():
            raw = tomllib.loads(path.read_text())

        data_root = Path(raw.get("paths", {}).get("data_dir", paths.data_dir())).expanduser()
        state_root = Path(raw.get("paths", {}).get("state_dir", paths.state_dir())).expanduser()
        telegram = raw.get("telegram", {})
        defaults = raw.get("defaults", {})

        api_id = expand_env(telegram.get("api_id")) or os.getenv("TELEGRAM_API_ID")
        api_hash = expand_env(telegram.get("api_hash")) or os.getenv("TELEGRAM_API_HASH")
        tdlib_dir = Path(telegram.get("tdlib_dir", state_root / "tdlib")).expanduser()
        sqlite_path = Path(raw.get("paths", {}).get("sqlite_path", data_root / "chappe.db")).expanduser()
        audit_path = Path(raw.get("paths", {}).get("audit_log", state_root / "audit.jsonl")).expanduser()

        return cls(
            telegram=TelegramConfig(
                api_id=str(api_id) if api_id else None,
                api_hash=str(api_hash) if api_hash else None,
                database_encryption_key_env=str(
                    telegram.get("database_encryption_key_env", "CHAPPE_TDLIB_KEY")
                ),
                database_encryption_key=expand_env(telegram.get("database_encryption_key")),
            ),
            storage=StorageConfig(
                config_path=path,
                data_dir=data_root,
                state_dir=state_root,
                tdlib_dir=tdlib_dir,
                sqlite_path=sqlite_path,
                audit_log_path=audit_path,
            ),
            defaults=DefaultsConfig(
                json=bool(defaults.get("json", True)),
                max_messages=int(defaults.get("max_messages", 100)),
                default_period=str(defaults.get("default_period", "30d")),
                default_channel=defaults.get("default_channel"),
            ),
            raw=raw,
        )

    def ensure_dirs(self) -> None:
        for path in [
            self.storage.config_path.parent,
            self.storage.data_dir,
            self.storage.state_dir,
            self.storage.tdlib_dir,
            self.storage.sqlite_path.parent,
            self.storage.audit_log_path.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)


DEFAULT_CONFIG = """# Chappe configuration
# Chappe is an unofficial Telegram channel growth CLI.

[telegram]
api_id = "${TELEGRAM_API_ID}"
api_hash = "${TELEGRAM_API_HASH}"
tdlib_dir = "~/.local/state/chappe/tdlib"
database_encryption_key_env = "CHAPPE_TDLIB_KEY"
# Optional: store a local TDLib database key directly in config instead of env.
# database_encryption_key = "replace-with-a-long-local-random-string"

[paths]
data_dir = "~/.local/share/chappe"
state_dir = "~/.local/state/chappe"
sqlite_path = "~/.local/share/chappe/chappe.db"
audit_log = "~/.local/state/chappe/audit.jsonl"

[defaults]
json = true
max_messages = 100
default_period = "30d"
# default_channel = "@your_channel"
"""


def render_config(
    *,
    api_id: str | None = None,
    api_hash: str | None = None,
    database_encryption_key: str | None = None,
    default_channel: str | None = None,
) -> str:
    def toml_string(value: str) -> str:
        return json.dumps(value)

    api_id_value = api_id if api_id is not None else "${TELEGRAM_API_ID}"
    api_hash_value = api_hash if api_hash is not None else "${TELEGRAM_API_HASH}"
    key_value = database_encryption_key or secrets.token_urlsafe(32)
    channel_line = f"default_channel = {toml_string(default_channel)}\n" if default_channel else ""
    return f"""# Chappe configuration
# Chappe is an unofficial Telegram channel growth CLI.

[telegram]
api_id = {toml_string(api_id_value)}
api_hash = {toml_string(api_hash_value)}
tdlib_dir = "~/.local/state/chappe/tdlib"
database_encryption_key = {toml_string(key_value)}

[paths]
data_dir = "~/.local/share/chappe"
state_dir = "~/.local/state/chappe"
sqlite_path = "~/.local/share/chappe/chappe.db"
audit_log = "~/.local/state/chappe/audit.jsonl"

[defaults]
json = true
max_messages = 100
default_period = "30d"
{channel_line}"""


def init_config(path: Path | None = None, *, force: bool = False, contents: str | None = None) -> Path:
    config_path = Path(path).expanduser() if path else paths.default_config_path()
    if config_path.exists() and not force:
        raise ChappeError(
            f"Config already exists: {config_path}",
            ExitCode.USAGE_ERROR,
            next_command=f"chappe config init --force --path {config_path}",
        )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(contents or DEFAULT_CONFIG)
    return config_path

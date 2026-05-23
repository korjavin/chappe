from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .config import ChappeConfig
from .errors import ChappeError, ExitCode


class TelethonUnavailable(ChappeError):
    def __init__(self, detail: str = "Telethon is not installed."):
        super().__init__(
            detail,
            ExitCode.AUTH_ERROR,
            next_command="pipx install chappe or pip install telethon",
        )


def telethon_available() -> bool:
    try:
        import telethon  # noqa: F401

        return True
    except Exception:
        return False


AUTH_READY = "authorizationStateReady"
AUTH_WAIT_PHONE = "authorizationStateWaitPhoneNumber"
AUTH_WAIT_CODE = "authorizationStateWaitCode"
AUTH_WAIT_PASSWORD = "authorizationStateWaitPassword"


def _iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _media_type(message: Any) -> str:
    media = getattr(message, "media", None)
    if media is None:
        return "text"
    name = type(media).__name__
    if name == "MessageMediaPhoto":
        return "photo"
    if name == "MessageMediaDocument":
        doc = getattr(media, "document", None)
        mime = getattr(doc, "mime_type", "") or ""
        if mime.startswith("video/"):
            return "video"
        if mime.startswith("audio/"):
            return "audio"
        return "document"
    if name == "MessageMediaWebPage":
        return "webpage"
    if name == "MessageMediaPoll":
        return "poll"
    return name.replace("MessageMedia", "").lower() or "media"


def _reactions_total(message: Any) -> int:
    reactions = getattr(message, "reactions", None)
    if not reactions:
        return 0
    results = getattr(reactions, "results", None) or []
    total = 0
    for result in results:
        total += int(getattr(result, "count", 0) or 0)
    return total


def _replies_count(message: Any) -> int:
    replies = getattr(message, "replies", None)
    if not replies:
        return 0
    return int(getattr(replies, "replies", 0) or 0)


def normalize_chat(entity: Any, handle: str | None = None) -> dict[str, Any]:
    username = getattr(entity, "username", None)
    title = getattr(entity, "title", None) or getattr(entity, "first_name", None)
    chat_id = getattr(entity, "id", None)
    chat_type = type(entity).__name__
    return {
        "id": chat_id,
        "handle": handle or (f"@{username}" if username else str(chat_id)),
        "title": title,
        "username": username,
        "type": chat_type,
    }


def normalize_message(
    message: Any, *, channel: str, username: str | None = None
) -> dict[str, Any]:
    handle = username or (channel or "").lstrip("@")
    post_id = str(getattr(message, "id", ""))
    text = getattr(message, "message", None) or ""
    return {
        "id": post_id,
        "date": _iso(getattr(message, "date", None)),
        "text": text,
        "views": int(getattr(message, "views", 0) or 0),
        "forwards": int(getattr(message, "forwards", 0) or 0),
        "replies": _replies_count(message),
        "reactions": _reactions_total(message),
        "media_type": _media_type(message),
        "link": f"https://t.me/{handle}/{post_id}" if handle and post_id else None,
    }


def _auth_state(state_type: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"@type": state_type}
    payload.update(extra)
    return payload


class TelegramGateway:
    def __init__(self, config: ChappeConfig):
        self.config = config
        self._client: Any | None = None
        self._connected = False

    def _session_path(self) -> Path:
        return self.config.storage.tdlib_dir / "chappe"

    def _auth_state_path(self) -> Path:
        return self.config.storage.tdlib_dir / "auth_state.json"

    def _load_pending_phone_auth(self) -> dict[str, Any] | None:
        path = self._auth_state_path()
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def _save_pending_phone_auth(self, data: dict[str, Any]) -> None:
        path = self._auth_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def _clear_pending_phone_auth(self) -> None:
        path = self._auth_state_path()
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        if not self.config.telegram.api_id or not self.config.telegram.api_hash:
            raise ChappeError(
                "Telegram API credentials are missing.",
                ExitCode.AUTH_ERROR,
                next_command="chappe config init; export TELEGRAM_API_ID=... TELEGRAM_API_HASH=...",
            )
        try:
            from telethon.sync import TelegramClient
        except ImportError as exc:
            raise TelethonUnavailable(str(exc)) from exc
        self.config.ensure_dirs()
        self._client = TelegramClient(
            str(self._session_path()),
            int(self.config.telegram.api_id),
            self.config.telegram.api_hash,
            device_model="Chappe CLI",
            app_version=__version__,
            system_version="Chappe",
        )

    def connect(self) -> None:
        self._ensure_client()
        if not self._connected:
            assert self._client is not None
            self._client.connect()
            self._connected = True

    def close(self) -> None:
        if self._client is not None and self._connected:
            try:
                self._client.disconnect()
            except Exception:
                pass
        self._connected = False

    def configure(self) -> dict[str, Any]:
        self.connect()
        assert self._client is not None
        if self._client.is_user_authorized():
            self._clear_pending_phone_auth()
            return _auth_state(AUTH_READY)
        pending = self._load_pending_phone_auth() or {}
        stage = pending.get("stage")
        if stage == "wait_code":
            return _auth_state(AUTH_WAIT_CODE)
        if stage == "wait_password":
            return _auth_state(AUTH_WAIT_PASSWORD)
        return _auth_state(AUTH_WAIT_PHONE)

    def authorization_state(self) -> dict[str, Any]:
        return self.configure()

    def login_interactive(
        self,
        phone: str | None = None,
        *,
        code: str | None = None,
        password: str | None = None,
    ) -> dict[str, Any]:
        from telethon.errors import (
            PhoneCodeExpiredError,
            PhoneCodeInvalidError,
            SessionPasswordNeededError,
        )

        state = self.configure()
        stype = state["@type"]
        if stype == AUTH_READY:
            return {"authorized": True, "state": stype}

        assert self._client is not None
        pending = self._load_pending_phone_auth() or {}

        if stype == AUTH_WAIT_PHONE:
            if not phone:
                raise ChappeError(
                    "Phone number is required for Telethon login.",
                    ExitCode.USAGE_ERROR,
                    next_command=(
                        "chappe auth login-bot"
                        if self.config.telegram.bot_token
                        else "chappe auth login --phone +15551234567"
                    ),
                )
            sent = self._client.send_code_request(phone)
            self._save_pending_phone_auth(
                {
                    "phone": phone,
                    "phone_code_hash": getattr(sent, "phone_code_hash", None),
                    "stage": "wait_code",
                }
            )
            return {
                "authorized": False,
                "state": AUTH_WAIT_CODE,
                "next_command": "chappe auth login --code <telegram-code>",
            }

        if stype == AUTH_WAIT_CODE:
            if not code:
                return {
                    "authorized": False,
                    "state": stype,
                    "next_command": "chappe auth login --code <telegram-code>",
                }
            stored_phone = pending.get("phone")
            stored_hash = pending.get("phone_code_hash")
            if not stored_phone or not stored_hash:
                raise ChappeError(
                    "No pending phone login found. Restart with --phone.",
                    ExitCode.AUTH_ERROR,
                    next_command="chappe auth login --phone +15551234567",
                )
            try:
                self._client.sign_in(
                    phone=stored_phone, code=code, phone_code_hash=stored_hash
                )
            except SessionPasswordNeededError:
                self._save_pending_phone_auth(
                    {"phone": stored_phone, "stage": "wait_password"}
                )
                return {
                    "authorized": False,
                    "state": AUTH_WAIT_PASSWORD,
                    "next_command": 'chappe auth login --password "<2fa-password>"',
                }
            except (PhoneCodeInvalidError, PhoneCodeExpiredError) as exc:
                raise ChappeError(
                    f"Phone code rejected: {exc}",
                    ExitCode.AUTH_ERROR,
                    next_command="chappe auth login --phone +15551234567",
                ) from exc
            self._clear_pending_phone_auth()
            return {"authorized": True, "state": AUTH_READY}

        if stype == AUTH_WAIT_PASSWORD:
            if not password:
                return {
                    "authorized": False,
                    "state": stype,
                    "next_command": 'chappe auth login --password "<2fa-password>"',
                }
            self._client.sign_in(password=password)
            self._clear_pending_phone_auth()
            return {"authorized": True, "state": AUTH_READY}

        return {"authorized": False, "state": stype}

    def login_bot(self, token: str | None = None) -> dict[str, Any]:
        token_value = token or self.config.telegram.bot_token
        if not token_value:
            raise ChappeError(
                "Bot token is required. Pass --token or set telegram.bot_token / TELEGRAM_BOT_TOKEN.",
                ExitCode.USAGE_ERROR,
                next_command="chappe auth login-bot --token 123456:ABC-...",
            )
        state = self.configure()
        if state["@type"] == AUTH_READY:
            return {"authorized": True, "state": AUTH_READY}
        assert self._client is not None
        self._client.sign_in(bot_token=token_value)
        self._clear_pending_phone_auth()
        return {"authorized": True, "state": AUTH_READY}

    def _entity(self, handle: str | int) -> Any:
        self.connect()
        assert self._client is not None
        if isinstance(handle, str):
            if handle.startswith("@"):
                return self._client.get_entity(handle)
            try:
                return self._client.get_entity(int(handle))
            except (ValueError, TypeError):
                return self._client.get_entity(handle)
        return self._client.get_entity(handle)

    def resolve_chat(self, handle: str | int) -> dict[str, Any]:
        entity = self._entity(handle)
        return normalize_chat(entity, handle if isinstance(handle, str) else None)

    def chat_history(
        self,
        chat_id: int | str,
        *,
        limit: int = 100,
        from_message_id: int = 0,
        channel: str | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        target = max(0, int(limit))
        if target == 0:
            return {"messages": [], "total_count": 0, "next_from_message_id": None}
        entity = self._entity(chat_id)
        assert self._client is not None
        max_id = int(from_message_id) if from_message_id else 0
        messages = list(self._client.iter_messages(entity, limit=target, max_id=max_id))
        normalized = [
            normalize_message(m, channel=channel or "", username=username) for m in messages
        ]
        next_cursor = messages[-1].id if messages else None
        return {
            "messages": normalized,
            "total_count": len(normalized),
            "next_from_message_id": next_cursor,
        }

    def message_thread(
        self,
        chat_id: int | str,
        message_id: int | str,
        *,
        limit: int = 100,
        channel: str | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        entity = self._entity(chat_id)
        assert self._client is not None
        messages = list(
            self._client.iter_messages(entity, limit=int(limit), reply_to=int(message_id))
        )
        normalized = [
            normalize_message(m, channel=channel or "", username=username) for m in messages
        ]
        return {"messages": normalized, "total_count": len(normalized)}

    def search_messages(
        self,
        chat_id: int | str,
        query: str,
        *,
        limit: int = 100,
        channel: str | None = None,
        username: str | None = None,
    ) -> dict[str, Any]:
        entity = self._entity(chat_id)
        assert self._client is not None
        messages = list(
            self._client.iter_messages(entity, search=query, limit=int(limit))
        )
        normalized = [
            normalize_message(m, channel=channel or "", username=username) for m in messages
        ]
        return {"messages": normalized, "total_count": len(normalized)}

    def chat_statistics(self, chat_id: int | str) -> dict[str, Any]:
        from telethon.tl import functions

        entity = self._entity(chat_id)
        assert self._client is not None
        try:
            result = self._client(functions.stats.GetBroadcastStatsRequest(channel=entity))
        except Exception as exc:
            raise ChappeError(
                f"Channel statistics unavailable: {exc}",
                ExitCode.TELEGRAM_ERROR,
            ) from exc
        return result.to_dict() if hasattr(result, "to_dict") else dict(result)

    def similar_chats(self, chat_id: int | str) -> dict[str, Any]:
        from telethon.tl import functions

        entity = self._entity(chat_id)
        assert self._client is not None
        request_cls = getattr(functions.channels, "GetChannelRecommendationsRequest", None)
        if request_cls is None:
            return {
                "chats": [],
                "note": "Telethon on this version does not expose channel recommendations.",
            }
        try:
            result = self._client(request_cls(channel=entity))
        except Exception as exc:
            return {"chats": [], "error": str(exc)}
        chats = [normalize_chat(chat) for chat in getattr(result, "chats", []) or []]
        return {"chats": chats}

    def send_text(self, chat_id: int | str, text: str) -> dict[str, Any]:
        entity = self._entity(chat_id)
        assert self._client is not None
        sent = self._client.send_message(entity, text)
        return {
            "id": getattr(sent, "id", None),
            "date": _iso(getattr(sent, "date", None)),
            "chat_id": chat_id,
        }


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

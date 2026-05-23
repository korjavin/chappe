from datetime import datetime, timezone
from types import SimpleNamespace

from chappe.config import ChappeConfig
from chappe.errors import ChappeError
from chappe.gateway import (
    AUTH_READY,
    AUTH_WAIT_CODE,
    AUTH_WAIT_PASSWORD,
    TelegramGateway,
    normalize_chat,
    normalize_message,
    telethon_available,
)


def _telethon_message(**fields):
    base = {
        "id": 0,
        "message": "",
        "date": None,
        "views": 0,
        "forwards": 0,
        "replies": None,
        "reactions": None,
        "media": None,
    }
    base.update(fields)
    return SimpleNamespace(**base)


def test_telethon_available_smoke():
    assert telethon_available() is True


def test_normalize_message_extracts_metrics_and_link():
    msg = _telethon_message(
        id=123,
        message="hello",
        date=datetime(2026, 5, 23, 10, 0, tzinfo=timezone.utc),
        views=100,
        forwards=5,
        replies=SimpleNamespace(replies=9),
        reactions=SimpleNamespace(results=[SimpleNamespace(count=3), SimpleNamespace(count=4)]),
    )

    post = normalize_message(msg, channel="@x", username="x")

    assert post["id"] == "123"
    assert post["text"] == "hello"
    assert post["views"] == 100
    assert post["forwards"] == 5
    assert post["replies"] == 9
    assert post["reactions"] == 7
    assert post["link"] == "https://t.me/x/123"
    assert post["date"] == "2026-05-23T10:00:00+00:00"


def test_normalize_message_handles_missing_reactions_and_replies():
    msg = _telethon_message(id=42, message="solo")
    post = normalize_message(msg, channel="@x")
    assert post["replies"] == 0
    assert post["reactions"] == 0
    assert post["media_type"] == "text"


def test_normalize_message_classifies_media_type():
    class MessageMediaPhoto:
        pass

    class MessageMediaDocument:
        def __init__(self, mime_type: str):
            self.document = SimpleNamespace(mime_type=mime_type)

    photo_msg = _telethon_message(id=1, media=MessageMediaPhoto())
    doc_msg = _telethon_message(id=2, media=MessageMediaDocument("video/mp4"))

    assert normalize_message(photo_msg, channel="@x")["media_type"] == "photo"
    assert normalize_message(doc_msg, channel="@x")["media_type"] == "video"


def test_normalize_chat_uses_username_for_handle():
    entity = SimpleNamespace(id=42, username="x", title="X", first_name=None)
    chat = normalize_chat(entity)
    assert chat["handle"] == "@x"
    assert chat["title"] == "X"


def test_login_bot_requires_token(tmp_path):
    cfg = ChappeConfig.load(tmp_path / "config.toml")
    gateway = TelegramGateway(cfg)
    try:
        gateway.login_bot(None)
    except ChappeError as exc:
        assert "Bot token is required" in exc.message
    else:
        raise AssertionError("expected ChappeError when no token is supplied")


def test_login_bot_calls_sign_in_with_token(monkeypatch, tmp_path):
    cfg = ChappeConfig.load(tmp_path / "config.toml")
    gateway = TelegramGateway(cfg)

    captured: dict[str, object] = {}

    class FakeClient:
        def is_user_authorized(self):
            return False

        def sign_in(self, **kwargs):
            captured.update(kwargs)

        def connect(self):
            captured["connected"] = True

    def fake_ensure_client(self):
        self._client = FakeClient()

    monkeypatch.setattr(TelegramGateway, "_ensure_client", fake_ensure_client)

    result = gateway.login_bot("123456:ABC")

    assert captured == {"connected": True, "bot_token": "123456:ABC"}
    assert result == {"authorized": True, "state": AUTH_READY}


def test_login_interactive_persists_code_hash_then_signs_in(monkeypatch, tmp_path):
    cfg = ChappeConfig.load(tmp_path / "config.toml")
    cfg.ensure_dirs()
    gateway = TelegramGateway(cfg)

    sign_in_calls: list[dict[str, object]] = []

    class FakeClient:
        def __init__(self):
            self.authorized = False
            self.code_sent_to: str | None = None

        def is_user_authorized(self):
            return self.authorized

        def connect(self):
            pass

        def send_code_request(self, phone):
            self.code_sent_to = phone
            return SimpleNamespace(phone_code_hash="HASH123")

        def sign_in(self, **kwargs):
            sign_in_calls.append(kwargs)
            self.authorized = True

    fake_client = FakeClient()

    def fake_ensure_client(self):
        self._client = fake_client

    monkeypatch.setattr(TelegramGateway, "_ensure_client", fake_ensure_client)

    step1 = gateway.login_interactive("+15551234567")
    assert step1["state"] == AUTH_WAIT_CODE
    pending = gateway._load_pending_phone_auth()
    assert pending == {
        "phone": "+15551234567",
        "phone_code_hash": "HASH123",
        "stage": "wait_code",
    }

    step2 = gateway.login_interactive(code="12345")
    assert step2 == {"authorized": True, "state": AUTH_READY}
    assert sign_in_calls == [
        {"phone": "+15551234567", "code": "12345", "phone_code_hash": "HASH123"}
    ]
    assert gateway._load_pending_phone_auth() is None


def test_login_interactive_handles_2fa(monkeypatch, tmp_path):
    from telethon.errors import SessionPasswordNeededError

    cfg = ChappeConfig.load(tmp_path / "config.toml")
    cfg.ensure_dirs()
    gateway = TelegramGateway(cfg)

    sign_in_calls: list[dict[str, object]] = []

    class FakeClient:
        def __init__(self):
            self.authorized = False

        def is_user_authorized(self):
            return self.authorized

        def connect(self):
            pass

        def send_code_request(self, phone):
            return SimpleNamespace(phone_code_hash="HASH")

        def sign_in(self, **kwargs):
            sign_in_calls.append(kwargs)
            if "code" in kwargs:
                raise SessionPasswordNeededError(request=None)
            self.authorized = True

    fake_client = FakeClient()
    monkeypatch.setattr(TelegramGateway, "_ensure_client", lambda self: setattr(self, "_client", fake_client))

    gateway.login_interactive("+15550000000")
    after_code = gateway.login_interactive(code="111111")
    assert after_code["state"] == AUTH_WAIT_PASSWORD

    after_password = gateway.login_interactive(password="hunter2")
    assert after_password == {"authorized": True, "state": AUTH_READY}
    assert sign_in_calls[-1] == {"password": "hunter2"}


def test_chat_history_calls_iter_messages_with_limit_and_cursor(monkeypatch, tmp_path):
    cfg = ChappeConfig.load(tmp_path / "config.toml")
    cfg.ensure_dirs()
    gateway = TelegramGateway(cfg)

    iter_calls: list[dict[str, object]] = []
    fake_entity = object()

    class FakeClient:
        def iter_messages(self, entity, **kwargs):
            iter_calls.append({"entity": entity, **kwargs})
            return iter(
                [
                    _telethon_message(id=30, message="three"),
                    _telethon_message(id=20, message="two"),
                ]
            )

        def get_entity(self, handle):
            return fake_entity

        def is_user_authorized(self):
            return True

        def connect(self):
            pass

    monkeypatch.setattr(TelegramGateway, "_ensure_client", lambda self: setattr(self, "_client", FakeClient()))

    history = gateway.chat_history(
        "@x", limit=2, from_message_id=40, channel="@x", username="x"
    )

    assert iter_calls == [
        {"entity": fake_entity, "limit": 2, "max_id": 40},
    ]
    assert [m["id"] for m in history["messages"]] == ["30", "20"]
    assert history["next_from_message_id"] == 20
    assert history["total_count"] == 2


def test_chat_history_handles_zero_limit(tmp_path):
    cfg = ChappeConfig.load(tmp_path / "config.toml")
    gateway = TelegramGateway(cfg)
    result = gateway.chat_history("@x", limit=0)
    assert result == {"messages": [], "total_count": 0, "next_from_message_id": None}

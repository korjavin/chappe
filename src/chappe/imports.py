from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import ChappeError, ExitCode


def _iso_from_unix(ts: str | int | None) -> str | None:
    if ts is None or ts == "":
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except (TypeError, ValueError):
        return None


def _join_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for run in value:
            if isinstance(run, str):
                parts.append(run)
            elif isinstance(run, dict):
                parts.append(str(run.get("text") or ""))
        return "".join(parts)
    return str(value)


def _media_type(message: dict[str, Any]) -> str:
    if message.get("photo"):
        return "photo"
    if message.get("poll"):
        return "poll"
    mtype = message.get("media_type")
    if mtype == "video_file":
        return "video"
    if mtype == "audio_file":
        return "audio"
    if mtype == "voice_message":
        return "voice"
    if mtype == "video_message":
        return "video"
    if mtype == "animation":
        return "animation"
    if mtype == "sticker":
        return "sticker"
    if message.get("file"):
        return "document"
    return "text"


def _reactions_total(message: dict[str, Any]) -> int:
    reactions = message.get("reactions") or []
    if not isinstance(reactions, list):
        return 0
    total = 0
    for reaction in reactions:
        if isinstance(reaction, dict):
            total += int(reaction.get("count") or 0)
    return total


def normalize_export_message(message: dict[str, Any], *, channel: str) -> dict[str, Any]:
    handle = (channel or "").lstrip("@")
    post_id = str(message.get("id"))
    iso_date = _iso_from_unix(message.get("date_unixtime")) or message.get("date")
    return {
        "id": post_id,
        "date": iso_date,
        "text": _join_text(message.get("text")),
        "views": 0,
        "forwards": 0,
        "replies": 0,
        "reactions": _reactions_total(message),
        "media_type": _media_type(message),
        "link": f"https://t.me/{handle}/{post_id}" if handle and post_id else None,
    }


def parse_desktop_export(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ChappeError(
            f"Could not read JSON export at {path}: {exc}",
            ExitCode.USAGE_ERROR,
        ) from exc
    if not isinstance(data, dict) or "messages" not in data:
        raise ChappeError(
            f"{path} does not look like a Telegram Desktop JSON export "
            "(missing 'messages' key).",
            ExitCode.USAGE_ERROR,
        )
    return data


def collect_posts(
    export: dict[str, Any], *, channel: str
) -> tuple[list[dict[str, Any]], int]:
    messages = export.get("messages") or []
    posts: list[dict[str, Any]] = []
    skipped_service = 0
    for message in messages:
        if not isinstance(message, dict):
            continue
        if message.get("type") != "message":
            skipped_service += 1
            continue
        posts.append(normalize_export_message(message, channel=channel))
    return posts, skipped_service


IMPORT_WARNINGS = [
    "Desktop JSON export does not include view counts; views=0 for every imported post. "
    "Do not rank by views from imported data.",
    "Desktop JSON export does not include forward counts; forwards=0 for every imported post. "
    "Do not rank by forwards from imported data.",
    "Comments are not included in a channel-only export. Export the linked discussion "
    "group separately and rerun chappe import to populate comment data.",
]

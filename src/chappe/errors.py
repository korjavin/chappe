from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class ExitCode(IntEnum):
    OK = 0
    TELEGRAM_ERROR = 1
    USAGE_ERROR = 2
    AUTH_ERROR = 3
    PERMISSION_DENIED = 4
    RATE_LIMITED = 5
    NOT_FOUND = 6
    UNSAFE_MUTATION = 7


@dataclass
class ChappeError(Exception):
    message: str
    code: ExitCode = ExitCode.TELEGRAM_ERROR
    details: dict[str, Any] | None = None
    next_command: str | None = None

    def payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": False,
            "error": {
                "message": self.message,
                "code": int(self.code),
                "name": self.code.name.lower(),
            },
        }
        if self.details:
            payload["error"]["details"] = self.details
        if self.next_command:
            payload["next_command"] = self.next_command
        return payload


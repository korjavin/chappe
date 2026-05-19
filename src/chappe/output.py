from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import typer

from .errors import ChappeError


def _default(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)


def emit(payload: Any, *, pretty: bool = False, stderr: bool = False) -> None:
    text = json.dumps(payload, ensure_ascii=False, default=_default, indent=2 if pretty else None)
    print(text, file=sys.stderr if stderr else sys.stdout)


def fail(error: ChappeError, *, pretty: bool = False) -> None:
    emit(error.payload(), pretty=pretty, stderr=True)
    raise typer.Exit(int(error.code))


from __future__ import annotations

from typing import Any


def lint_draft(text: str, *, max_chars: int = 4096) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    stripped = text.strip()
    if not stripped:
        errors.append({"code": "empty", "message": "Draft text is empty."})
    if len(text) > max_chars:
        errors.append({"code": "too_long", "message": f"Draft is longer than {max_chars} characters."})
    if text.count("http://") + text.count("https://") > 3:
        warnings.append({"code": "many_links", "message": "Draft contains more than three links."})
    if len(stripped.splitlines()[0]) > 180 if stripped else False:
        warnings.append({"code": "long_hook", "message": "First line is long for a Telegram hook."})
    if not any(mark in stripped for mark in ["?", ":", "—", "-", "🔥", "🤖", "AI", "ИИ"]):
        warnings.append({"code": "weak_hook_signal", "message": "Hook lacks a clear question, contrast, or signal."})
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "stats": {"chars": len(text), "lines": len(text.splitlines()), "links": text.count("http")},
    }


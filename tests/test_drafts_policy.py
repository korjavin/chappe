import pytest

from chappe.drafts import lint_draft
from chappe.errors import ChappeError
from chappe.policy import assert_publish_allowed, validate_policy


def test_lint_rejects_empty_draft():
    result = lint_draft("")
    assert not result["ok"]
    assert result["errors"][0]["code"] == "empty"


def test_policy_requires_channel():
    with pytest.raises(ChappeError):
        validate_policy({"enabled": True})


def test_publish_policy_allows_matching_actor():
    result = assert_publish_allowed(
        {"channel": "@x", "allowed_agents": ["codex"], "draft_lint": {"require_lint_ok": True}},
        channel="@x",
        text="AI agents: useful update",
        actor="codex",
    )
    assert result["lint"]["ok"]


def test_publish_policy_rejects_actor():
    with pytest.raises(ChappeError):
        assert_publish_allowed(
            {"channel": "@x", "allowed_agents": ["codex"]},
            channel="@x",
            text="AI agents: useful update",
            actor="hermes",
        )

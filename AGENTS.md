# Chappe Agent Guide

Chappe is an agent-native Telegram channel growth CLI. Agents working in this
repo should preserve the public CLI contract and avoid private Telegram state.

## Development Commands

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
```

## Product Rules

- Chappe is a CLI-first project, not MCP-first.
- Agents and humans must use the public `chappe` CLI, not private Python APIs.
- First-run setup must remain guided through `chappe onboard` and `agent_guided_setup`.
- JSON output is the stable interface. Diagnostics and failures should go to stderr.
- Publishing must require explicit user intent, `--commit`, and an enabled local policy.
- Every successful mutation should write an audit event.

## Safety Rules

- Do not commit `.env`, Telegram sessions, TDLib state, audit logs, fetched media,
  channel exports, or personal config files.
- Do not print Telegram API hashes, phone numbers, login codes, or 2FA passwords
  in prose.
- Do not run channel sync or analysis until auth is `authorizationStateReady`.
- Do not add LLM-provider calls to v1; Chappe prepares agent-ready evidence but
  does not call model APIs itself.

## Public Repo Scope

Keep the public repo focused on:

- `src/chappe/`
- tests
- docs
- examples
- agent integration assets
- Chappie mascot assets that are safe to publish

The old MCP prototype is reference material only and should not be copied here.

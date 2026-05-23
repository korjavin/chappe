# Contributing To Chappe

Thanks for working on Chappe. This project is early alpha, so useful changes
are narrow and tested. Tie each one to a real user workflow.

## Local Setup

```bash
git clone https://github.com/anovosel/chappe.git
cd chappe
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run checks:

```bash
ruff check .
pytest -q
```

## Contribution Guidelines

- Keep behavior exposed through the `chappe` CLI.
- Preserve compact JSON output by default.
- Send diagnostics and failures to stderr.
- Add or update tests when you change CLI output, config loading, policy
  validation, analytics scoring, or Telethon message normalization.
- Keep public docs accurate for agents and humans.
- Do not commit local Telegram state, `.env` files, session files, fetched media,
  audit logs, or channel exports.

## Pull Request Checklist

- [ ] `ruff check .` passes.
- [ ] `pytest -q` passes.
- [ ] README or docs updated if behavior changed.
- [ ] No private Telegram data, secrets, sessions, or local config files.
- [ ] Publishing behavior remains policy-gated and audited.

## Release Notes

For user-facing changes, add a short entry to `CHANGELOG.md` under `Unreleased`.

# Contributing To Chappe

Thanks for helping improve Chappe. This project is early alpha, so the most
valuable contributions are small, tested, and clear about the user workflow they
improve.

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
- Add or update tests for CLI output, config loading, policy validation,
  analytics scoring, and TDLib normalization when you change those areas.
- Keep public docs accurate for agents and humans.
- Do not commit local Telegram state, `.env` files, session files, fetched media,
  audit logs, or channel exports.

## Pull Request Checklist

- [ ] `ruff check .` passes.
- [ ] `pytest -q` passes.
- [ ] README or docs updated if behavior changed.
- [ ] No private Telegram data, secrets, sessions, or local config files included.
- [ ] Publishing behavior remains policy-gated and audited.

## Release Notes

For user-facing changes, add a short entry to `CHANGELOG.md` under `Unreleased`.

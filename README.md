# Chappe

![Chappe social preview](assets/social-preview.png)

Chappe is an Apache-2.0, agent-native Telegram channel growth CLI.

It helps channel owners and coding agents collect evidence, understand what is
spreading, mine audience demand, draft posts, and publish through explicit local
safety policy. It is named after Claude Chappe, whose optical telegraph networks
helped messages travel farther and faster.

Meet **Chappie**, the little tower keeper watching Telegram signals, recording
what spreads, and helping channel owners grow.

## What Chappe Is

Chappe is built for Telegram channel owners, not for generic chat automation.
It focuses on:

- guided first-run Telegram setup for humans and agents
- channel metadata, post history, and post performance snapshots
- top posts, outliers, forwarding signals, replies, reactions, and views
- comment mining for audience questions and content demand
- evidence bundles that agents can use without scraping private state
- draft creation, linting, preview, and policy-gated publishing
- native installable guidance for Codex, Claude Code, OpenCode, OpenClaw, and Hermes

Chappe is not MCP-first, not a general Telegram desktop client, and not an LLM
wrapper. Agents call the same public `chappe` CLI that humans call.

## Status

Chappe is early alpha. The repository is public-ready but the implementation is
still v1: expect sharp edges, fixture-backed tests, and a manual live auth path.
The repo intentionally excludes the old MCP prototype, local `.env` files,
Telegram sessions, fetched media, and private Claude Desktop configuration.

## Install

Development install:

```bash
git clone https://github.com/crimeacs/chappe.git
cd chappe
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
chappe doctor
```

Future public install after PyPI release:

```bash
uvx chappe doctor
pipx install chappe
```

## First Run

Start with the guided onboarding output:

```bash
chappe --pretty onboard --channel @nn_for_science
```

The response includes:

- `state`: config, TDLib, credential, and auth readiness
- `setup_steps`: human-readable next commands
- `agent_guided_setup`: machine-readable setup contract for Codex and similar agents
- `credential_help`: where to get Telegram API credentials

Agents should parse `agent_guided_setup`, ask for only the listed values, treat
all `sensitive: true` fields as secrets, and avoid channel sync or analysis
until `chappe onboard --check-auth` reports `authorizationStateReady`.

## Telegram Credentials

Create Telegram API credentials at [my.telegram.org/apps](https://my.telegram.org/apps).
You need:

- `api_id`
- `api_hash`
- the phone number for the Telegram account that administers or can read the channel

Recommended setup keeps the API hash out of the visible command line:

```bash
export TELEGRAM_API_ID="123456"
export TELEGRAM_API_HASH="your-api-hash"
chappe setup --channel @nn_for_science
```

You can also pass the values directly:

```bash
chappe setup --api-id "$TELEGRAM_API_ID" --api-hash "$TELEGRAM_API_HASH" --channel @nn_for_science
```

`chappe setup` writes `~/.config/chappe/config.toml` and generates a local TDLib
database encryption key. If you prefer a template config and environment-based
secret storage:

```bash
chappe config init
export TELEGRAM_API_ID="123456"
export TELEGRAM_API_HASH="your-api-hash"
export CHAPPE_TDLIB_KEY="stable-local-tdlib-key"
```

## Authentication

TDLib auth is intentionally step-by-step, so agents can guide it safely:

```bash
chappe onboard --check-auth
chappe auth login --phone +15551234567
chappe auth login --code 12345
chappe auth login --password "2fa-password-if-needed"
```

Auth states:

1. `authorizationStateWaitPhoneNumber`: run `chappe auth login --phone ...`.
2. `authorizationStateWaitCode`: enter the Telegram login code with `--code`.
3. `authorizationStateWaitPassword`: enter the Telegram 2FA password with `--password`.
4. `authorizationStateReady`: Chappe can sync, analyze, and publish for configured channels.

Chappe never asks an agent to guess credentials. If an agent sees missing
credentials or auth state, it should stop analysis and guide setup first.

## Common Workflows

Health check:

```bash
chappe doctor
```

Sync channel evidence:

```bash
chappe channel get @nn_for_science
chappe sync @nn_for_science --limit 100
chappe sync @nn_for_science --limit 100 --comments
```

Channel analytics:

```bash
chappe channel stats @nn_for_science --period 7d
chappe channel graphs @nn_for_science --period 90d
chappe channel similar @nn_for_science
```

Growth research:

```bash
chappe posts top @nn_for_science --by forwards --period 365d
chappe posts top @nn_for_science --by views --period 365d
chappe posts outliers @nn_for_science
chappe post report @nn_for_science 2655
chappe comments mine @nn_for_science --period 180d
chappe ideas @nn_for_science --count 20
chappe briefing @nn_for_science --period 90d --budget tokens:12000
```

Agent evidence bundle:

```bash
chappe agent-context @nn_for_science --period 90d --budget tokens:12000
```

Draft and publish:

```bash
chappe draft create @nn_for_science --file post.md
chappe draft lint draft_123
chappe draft preview draft_123
chappe automate enable @nn_for_science --policy examples/chappe.yaml
chappe publish draft_123 --commit --actor codex
```

Publishing requires `--commit` and an enabled local automation policy for the
target channel. Every successful mutation writes an audit event.

## JSON Contract

Chappe emits compact JSON by default and diagnostics to stderr. Use `--pretty`
before the command when reading manually:

```bash
chappe --pretty doctor
```

Expected shell behavior:

- exit code `0`: success
- nonzero exit: JSON error payload on stderr
- stdout: parseable command result
- stderr: diagnostics and failures

The output contract is intentionally boring so agents can use it reliably.

## Automation Policy

Chappe blocks autonomous publishing unless a local policy explicitly allows it.
See [examples/chappe.yaml](examples/chappe.yaml):

```yaml
channel: "@nn_for_science"
enabled: true
allowed_agents:
  - codex
  - claude-code
  - opencode
  - openclaw
  - hermes
rate_limits:
  max_posts_per_day: 3
draft_lint:
  require_lint_ok: true
  max_chars: 4096
audit:
  destination: "~/.local/state/chappe/audit.jsonl"
```

Install the policy:

```bash
chappe automate enable @nn_for_science --policy examples/chappe.yaml
```

## Agent Integrations

Install host-specific assets:

```bash
chappe agent list
chappe agent install codex
chappe agent install claude-code
chappe agent install opencode
chappe agent install openclaw
chappe agent install hermes
```

Installed assets teach each host to:

- start with `chappe onboard`
- respect `agent_guided_setup`
- parse JSON instead of scraping prose
- block sync and analysis until auth is ready
- block publishing unless policy and explicit user intent are present

All integrations call the public CLI. They do not import private Python APIs.

## Local Data And Privacy

By default Chappe stores local state under:

- config: `~/.config/chappe/config.toml`
- derived analytics store: `~/.local/share/chappe/chappe.db`
- TDLib state: `~/.local/state/chappe/tdlib`
- audit log: `~/.local/state/chappe/audit.jsonl`

Do not commit local configs, `.env` files, TDLib state, Telegram sessions,
downloaded media, channel exports, or audit logs. The repository `.gitignore`
blocks these by default.

## Development

Run tests and lint:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
```

Build package artifacts:

```bash
python -m pip install build
python -m build
```

Install the local CLI in another environment:

```bash
pipx install /path/to/chappe
```

## Public Release Setup

Repository and PyPI release setup are documented in
[docs/publication.md](docs/publication.md). The release workflow uses PyPI
Trusted Publishing through GitHub Actions OIDC, so Chappe does not need a
long-lived PyPI token in GitHub secrets.

## Repository Layout

```text
src/chappe/                 Python package and CLI
src/chappe/agent_assets/    Codex, Claude Code, OpenCode, OpenClaw, Hermes assets
tests/                      Unit and fixture-backed CLI tests
examples/                   Example automation policy
assets/                     Chappie mascot and repository visuals
docs/                       Brand and project notes
agents/                     Human-readable agent integration notes
```

## Roadmap

- hardened live TDLib sync for large channels
- richer admin statistics and historical snapshots
- better similar-channel discovery
- comment-topic clustering and audience jobs-to-be-done reports
- stricter publish policy enforcement and scheduling windows
- public PyPI release
- deeper examples for channel growth workflows

## License

Apache-2.0. See [LICENSE](LICENSE).

## Disclaimer

Chappe is unofficial and is not affiliated with Telegram. Use it within
Telegram's terms, local laws, and your channel's trust expectations.

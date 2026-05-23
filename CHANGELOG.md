# Changelog

User-facing Chappe changes are documented here.

This project follows a simple pre-1.0 changelog: user-facing changes, breaking
CLI changes, and security fixes should be listed under `Unreleased` until a
tagged release is cut.

## Unreleased

- **Breaking:** replaced the TDLib backend with Telethon. Existing sessions
  under `~/.local/state/chappe/tdlib/` no longer authorize Chappe; sign in
  again with `chappe auth login --phone ...` (or `chappe auth login-bot`).
- Removed the `tdjson` native dependency. Telethon is pure Python.
- Removed `--tdlib-key` from `chappe setup`. Telethon's session file does
  not need a separate database encryption key. The `database_encryption_key`
  TOML field is silently ignored if present.
- Renamed JSON output keys for the new backend: `tdjson_available` →
  `telethon_available`, `tdlib_dir` → `session_dir`. The `tdlib_dir` config
  field name is preserved so existing configs still load.
- Step-by-step phone login still works (`--phone` → `--code` → `--password`
  for 2FA). Chappe persists the Telethon `phone_code_hash` between CLI
  invocations under `<session_dir>/auth_state.json`.
- Added bot-account auth: `chappe auth login-bot --token <BotFather token>`
  signs in via Telethon's bot sign-in path. Bots can publish to channels
  where they are administrators; Telegram still restricts reading channel
  history for bot accounts.
- Added `--bot-token` to `chappe setup` and `bot_token` / `bot_token_env`
  fields on `TelegramConfig` (env var defaults to `TELEGRAM_BOT_TOKEN`).
- Documented bot mode in the README under Authentication.

## 0.2.0 — 2026-05-19

- Added `chappe compare @ch1 @ch2 [@ch3 ...]` for cross-channel post leaderboards.
  Returns per-channel top posts, a combined leaderboard, and a summary that
  names the mean-forward-rate leader and the raw-metric leader.
- Added `chappe wrapped @channel` which renders a shareable PNG dashboard plus
  a caption template. The card is the Chappe brand: cream paper, forest-green
  and sepia ink, Chappie embedded as a hero illustration. Each channel gets a
  deterministically-chosen mascot pose for variety.
- Added `Pillow>=10` dependency to support PNG rendering.
- Bundled Chappie mascot illustrations (`chappie-recorder`, `signal-operator`,
  `lookout`, `night-watch`, `scout-map-reader`) inside the installed wheel.
- Wired `chappe wrapped` into `bootstrap` `fastest_path_to_value` and the
  `onboard` setup steps once a channel has at least twenty stored posts.

## Pre-0.2 history

- Created Chappe package and CLI.
- Added TDLib-backed auth flow with guided first-run onboarding.
- Added bootstrap diagnostics as the default first-run experience.
- Added one-command GitHub installer script.
- Added local SQLite analytics store for channel records; post records; comment
  records; drafts; policy files; audit events.
- Added channel sync; channel stats; channel graphs.
- Added post ranking and outlier detection.
- Added comment mining; ideas; briefing; agent-context commands.
- Added policy-gated draft publishing with audit events.
- Added Codex/Claude Code/OpenCode/OpenClaw/Hermes integration assets.
- Added Chappie mascot assets and public documentation.

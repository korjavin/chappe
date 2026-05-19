# GitHub Launch Plan

Goal: earn stars from agent users and Telegram channel owners in the first 48
hours after a public push.

## Positioning

One-line:

```text
Ask Codex or Claude Code to grow a Telegram channel. Chappe is the CLI they call.
```

Short description:

```text
CLI tool surface for Telegram channel agents.
```

## Why This Fits GitHub Now

Current GitHub Trending is crowded with agent tooling, Claude Code skills,
memory tools, and installable command surfaces. Chappe should speak to that
audience first, then Telegram channel owners second.

## Above-The-Fold Checklist

- Show the mascot/social preview.
- State the agent-host use case in the first sentence.
- Put one copy-paste agent prompt before the first explanatory section.
- Include install and `chappe onboard` inside that prompt.
- Name supported hosts near the top: Codex/Claude Code/OpenCode/OpenClaw/Hermes.
- Keep privacy visible: TDLib local state, SQLite local store, policy-gated publish.
- Keep the README first screen under one minute to scan.

## Repo Metadata

Description:

```text
CLI tool surface for Telegram channel agents
```

Topics:

```text
telegram, telegram-channel, telegram-cli, claude-code, codex, opencode,
openclaw, hermes, agent-tools, channel-analytics, tdlib, python
```

## Launch Copy

GitHub/HN short post:

```text
I built Chappe, an Apache-2.0 CLI that lets Codex or Claude Code analyze a
Telegram channel.

It uses TDLib locally, stores derived analytics in SQLite, and gives agents
JSON outputs for top posts, comments, audience questions, draft ideas, and
policy-gated publishing.

Repo: https://github.com/crimeacs/chappe
```

X/Bluesky:

```text
Chappe is a CLI tool surface for Telegram channel agents.

Ask Codex or Claude Code: "analyze my channel and tell me what to post next."

TDLib local session. SQLite local store. JSON for agents. Policy-gated publish.
https://github.com/crimeacs/chappe
```

Telegram channel note:

```text
I opened Chappe: a local Telegram channel analytics CLI for agent hosts.

Goal: let Codex or Claude Code study @nn_for_science, find the posts that
traveled, mine reader questions, and draft better posts without handing channel
data to an LLM provider.

https://github.com/crimeacs/chappe
```

## Launch Sequence

1. Keep `main` green.
2. Pin a short GitHub issue: "What channel reports should Chappe generate next?"
3. Post the launch in the owner Telegram channel.
4. Post to X/Bluesky with the social preview image.
5. Share in Claude Code/Codex/OpenCode communities with the agent prompt, not a
   generic project pitch.
6. Ask early users to star the repo only if they want more Telegram agent tools.

## Next Product Proof

The highest-conversion demo is a real `@nn_for_science` report with private
values redacted:

- top forwarded posts
- comment questions
- audience-demand clusters
- draft ideas
- policy result for one draft

Ship it as `examples/nn_for_science_briefing.redacted.json` once live sync has
been tested.

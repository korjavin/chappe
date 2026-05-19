---
description: Build a Telegram channel growth briefing with Chappe
argument-hint: [channel] [period]
allowed-tools: Bash(chappe:*)
---

Run:

```bash
chappe onboard --channel ${1:-@channel}
chappe doctor
chappe briefing ${1:-@channel} --period ${2:-90d} --budget tokens:12000
```

Use the JSON evidence to summarize growth signals, audience demand, top posts, and next content ideas.

---
name: chappe
description: Use Chappe for Telegram channel growth intelligence, research, drafts, and policy-gated publishing.
---

# Chappe

Run `chappe onboard --channel @channel` and `chappe doctor` before use. For strategy work, call:

```bash
chappe briefing @channel --period 90d --budget tokens:12000
```

For autonomous publishing, Hermes must use an actor name:

```bash
chappe publish draft_id --commit --actor hermes
```

Only publish when Chappe reports an enabled automation policy for the target channel.

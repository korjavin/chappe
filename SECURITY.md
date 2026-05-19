# Security Policy

Chappe touches Telegram account authentication and local channel analytics data.
Treat security issues as high priority.

## Reporting A Vulnerability

Please do not open a public issue for vulnerabilities that expose credentials,
sessions, private channel data, publishing bypasses, or audit-log tampering.

Until a dedicated security email exists, report privately to the repository
owner through GitHub. Include:

- affected Chappe version or commit
- operating system and Python version
- steps to reproduce
- expected and actual behavior
- whether credentials, TDLib state, or channel data may be exposed

## Sensitive Data

Never commit:

- `.env` files
- Telegram API hashes
- phone numbers, login codes, or 2FA passwords
- TDLib directories
- Telethon or TDLib session files
- local SQLite analytics stores
- audit logs
- fetched media or channel exports

## Publishing Safety

Publishing must remain blocked unless all of these are true:

- the user explicitly requested publishing
- the command includes `--commit`
- the target channel has an enabled local policy
- the actor is allowed by policy
- draft lint passes when policy requires it
- an audit event is written after success

## Supported Versions

Chappe is pre-1.0. Security fixes target the latest commit on `main` until a
formal release policy exists.

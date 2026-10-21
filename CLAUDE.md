# ipay

Rebuild of iPay (Ingenious Payroll), Ingenious Business Software Pte Ltd's payroll product, as a cloud web app for Singapore and Malaysian payroll. Each company turns on one or both countries. The legacy app is a .NET Framework WinForms desktop app (VB.NET, DevExpress 13.1, one SQL Server database per company) covering Singapore only. Decisions: [docs/design/decisions.md](docs/design/decisions.md). UI rules: [docs/design/ui.md](docs/design/ui.md).

## Stack and running it

Flask, PostgreSQL 16 (one `platform` schema plus one schema per company, `co_000001`, ...), htmx, and a hand-written OKLCH design system with no build step. It follows the house layout: `libraries/libraries.py` is the only import surface for views; business logic goes in `modules/` (no Flask imports); the only database access is through `schemaconnect/`; views and controllers use the blueprint and template naming from dasonapp's module-structure skill.

```bash
docker compose up -d db                                   # local Postgres on 127.0.0.1:5433
.venv\Scripts\python -m schemaconnect.postgres.migrations.migrate
.venv\Scripts\python routing.py                           # http://127.0.0.1:4000
.venv\Scripts\python -m pytest tests/test_x.py            # test only the blast radius
```

Secrets live in `.env` (gitignored; `.env.example` lists the keys). Tests use a throwaway `ipay_test` database.

## Always-on skills: every session, every prompt, no invocation needed

The three skills imported below load at session start and apply from the first reply to the last, also after /compact and /clear. They are non-negotiable project rules.

1. caveman: every chat message to the owner is in caveman talk.
2. output-token-optimization: say only what the owner needs.
3. surgical-testing: when work changes code or behaviour, test only its blast radius, once. Default zero subagents; without ultracode 1, at most 2-3, when the radius needs it; with ultracode a handful in total (aim for 5 or fewer) and never more than 8 running at once. Anything more needs the owner's go-ahead after stating agent count and token cost.

How they fit: caveman sets how chat words look, output-token-optimization sets what and how much to say, and surgical-testing sets how much to test and how many agents to use. None of them ever drops a warning, a failure or a number. Content written to files or for other readers stays in normal English.

@.claude/skills/caveman/SKILL.md

@.claude/skills/output-token-optimization/SKILL.md

@.claude/skills/surgical-testing/SKILL.md

## Workflow: every change is tracked, committed and deployed

1. Track it in Vikunja first (the vikunja-project skill; tasks are II-1, II-2, ...).
2. Make the change, then run the surgical test for its blast radius.
3. Commit as ahmedwaqas92, with a message that starts with the task ref (`II-7 Add EPF bands`; add `fixes II-7` when the commit finishes the task), then deploy with `bash deploy/deploy.sh`. That pushes to GitHub and ships the committed HEAD to the server.

## Server

- `ipay-ingenious`: AWS EC2 (Debian 13, x86_64, 2 vCPU, 2 GB), reached over Tailscale at `100.99.145.7` as `admin` with key `~/.ssh/ipay.pem` (SSH alias `ipay-ingenious`). Never use the public IP.
- Code in `/opt/ipay/src`. Secrets in `/opt/ipay/.env`, created on the server; never copy them off it or into chat.
- Stack: `docker-compose.prod.yml`, compose project `ipay`. etcd plus PostgreSQL 16 under Patroni (`deploy/patroni/`), and the app on Apache + mod_wsgi, bound to 127.0.0.1:8080.
- Public: https://ipay.ddns.net (No-IP DNS → Elastic IP 15.134.221.45). Caddy (`public` profile, set by `COMPOSE_PROFILES=public` in the server `.env`) binds the private address `PUBLIC_BIND_IP=172.31.23.244`, gets the certificate automatically, and proxies to the app.
- Tailnet: https://ipay-ingenious.tail46f212.ts.net, via `tailscale serve` on 100.99.145.7:443.

## Legacy source

- `documents/` is gitignored client material; never commit it. `documents/legacy-src/` holds the ILSpy decompilation of Payroll.exe, iPay_IRAS_API.dll and iPayLicenseService.exe (v21.1.0.4). It may contain hardcoded secrets: never copy their values anywhere.
- Never open the legacy install's config files (`Customers/Ingenious/iPay/iPay/DBList.xml`, `*.ipay`, `Setting.setting`): they hold live database credentials.
- `docs/legacy/`: the legacy specification, agent-written from the decompiled source. Start at docs/legacy/README.md. All 18 docs are drafted. In 02, the rules and data model are done, but every section after Data model still says "(in progress)". Only four high-stakes claims have been spot-checked against the source, and all four were correct. docs/legacy/ and docs/design/decisions.md stay out of git while the GitHub repository is public, because they describe security holes in the legacy app that customers still run. Everything else is unverified: check the cited File.cs:line before relying on a rule.

## Modules

| Module | Path | Status |
| --- | --- | --- |
| caveman | .claude/skills/caveman/ | always on |
| output-token-optimization | .claude/skills/output-token-optimization/ | always on |
| surgical-testing | .claude/skills/surgical-testing/ | always on |
| Legacy decompiled source | documents/legacy-src/ | local only, gitignored |
| Legacy specification | docs/legacy/ (start at README.md) | drafted, mostly unverified |
| Platform: setup, sign-in, companies | views/{setup,login,companies}, modules/platform | built, tested |
| Company settings: SG/MY toggles, statutory IDs | views/settings, modules/settings | built, tested |
| Design system | static/{css,javascript}/design-system | built |
| AWS demo deploy (Apache + mod_wsgi, Caddy HTTPS, Postgres) | Dockerfile, docker-compose.prod.yml, deploy/ (runbook: deploy/README.md) | built, tested locally; waiting for Ingenious AWS account |
| Statutory rules 2026 (SG + MY) | docs/design/statutory-rules-2026.md | researched, 51 official sources; 10 items unconfirmed (its §0) |
| Employees, pay items, pay engine, statutory engines | — | next |

A UserPromptSubmit hook in .claude/settings.json adds a one-line reminder of these rules to every prompt.

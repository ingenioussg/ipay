---
name: surgical-testing
description: Always-on rule for this project. Whenever work changes code or behaviour, test only the blast radius of that change, and test it once. Loaded at session start through CLAUDE.md.
disable-model-invocation: true
---

# Surgical testing

Test what the change can break. Nothing more, nothing less, and only once.

Why: holistic and repeated testing (full suites, re-runs, duplicate verify passes under ultracode) burns tokens and dev time without finding more bugs. A check that covers the blast radius proves the change. Everything else only re-proves code that did not change.

## When it applies

It applies to every prompt whose work changes code or behaviour: code, config, compose or env files, scripts, DB schema or data, dependencies or image versions, payroll configuration (rate tables, pay item flags, formulas), and Claude Code config (CLAUDE.md, skills, hooks, settings). Pure questions, explanations, plans and doc wording need no tests.

## Method

1. List what changed: files, functions, config keys.
2. Map the blast radius: the changed units, their direct dependents, and touched contracts (signatures, config keys, env vars, DB schema, file formats, CLI arguments). Find dependents with targeted grep, not by reading the whole repo.
3. Run the existing tests that cover the radius: the tests of the changed units AND the tests of their direct dependents, in one targeted command (for example `python -m unittest tests.test_tax tests.test_invoice`). They are the cheapest proof and they catch expectations the change made wrong. An ad hoc check never replaces them. A test whose expectation the requested change makes outdated is inside the radius: update it, never skip it.
4. Only where the radius has no tests, pick the cheapest check that proves the change: a static check first, then a unit test, then a targeted integration check, then end-to-end. Stop at the first level that really proves it.
5. Run it once. Re-run a passing check only if the code changed since.
6. Report in 1-2 lines: what was checked, the result, and what was deliberately not tested. Never claim untested parts work.

## Honest radius

Never shrink the radius to save time. Widen it one ring at a time when the change touches shared or core code, dependency or image upgrades, DB migrations, auth or security, money logic (CPF and other statutory contributions, proration, rounding, net pay, totals, GL posting), or build and deploy config. Money changes always get at least one check with concrete numbers.

## Banned

- Full suites or the whole stack for a local change.
- Re-running passing checks when nothing changed, or re-reading a file after a successful edit just to confirm it.
- Multi-agent sweeps and large workflow fan-outs. Default is zero subagents.
  - Without ultracode: when the radius grows past what one context can check, use 1 agent, at most 2-3, each on a distinct part of the radius.
  - With ultracode on: a handful of agents in total (aim for 5 or fewer), and never more than 8 running at the same time. A workflow script must keep at most 8 agent() calls in flight, for example by processing items in batches of 8 or fewer.
  - Anything beyond these limits needs the owner's explicit go-ahead in the current prompt, after stating the agent count and rough token cost.
- Several agents or verify passes testing the same scope. One targeted check per claim.
- Testing framework or library behaviour, or the decompiled legacy code in documents/legacy-src/, beyond what the change touches.
- Writing broad new test suites when one targeted test proves the change.

## On failure

Fix it, then re-run only the failed check plus the radius of the fix. Widen only if the failure shows wider impact.

## Owner override

Only an explicit owner request in the current prompt (for example "run the full suite before deploy") widens testing beyond the computed radius.

## Cheapest checks for this stack

- Python module: `python -m py_compile <file>`, then pytest for that module and its direct dependents only (`pytest tests/test_x.py -k <name>`).
- Flask route or template: one request to the touched route, expect 200 and a render.
- Payroll or statutory calculation (CPF, SDL, SHG, FWL, proration, OT, leave pay, net pay): one case with known numbers, compare to the cent. Use the worked examples in docs/legacy/ where they exist.
- File export (CPF e-submission, bank GIRO, IRAS file or API payload): generate one file from a fixture and diff it against the expected layout.
- DB migration: run it on a copy or inside a transaction, then one query on the changed table.
- Legacy spec claim in docs/legacy/: check the cited File.cs:line with Grep or Read directly. No verify agents.
- docker-compose.yml or .env: `docker compose config -q`, then the health of the touched service only.
- Bash or PowerShell script: run it on test data or in dry-run mode.
- settings.json or hooks: parse the JSON and pipe-test the hook command once.

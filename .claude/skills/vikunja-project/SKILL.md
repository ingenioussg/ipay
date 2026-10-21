---
name: vikunja-project
description: "Track this repository's work in its Lojicloop Vikunja project, iPay-Ingenious (II), with tasks, status, progress and comments. Use before starting any piece of work, as it progresses, when it is done, and when asked about the project's tasks or progress."
---

# Vikunja project tracking (Lojicloop)

This repository (ingenioussg/ipay) belongs to the Lojicloop Vikunja project **iPay-Ingenious**, whose tasks are II-1, II-2 and so on. The client follows the project through a public link that shows task titles, status, who works on them, dates and how tasks moved over time. It never shows descriptions or comments.

Tool: `python .claude/skills/vikunja-project/vik.py <command>` (Python 3, no packages). It reads the dashboard's address and Waqas Ahmed's own key from `.vikunja.env` beside it. The `.gitignore` beside it keeps that file out of git: never commit it, never print the key, never paste it into files or messages.

This tooling was made for Waqas Ahmed and works only while Waqas Ahmed can edit the project in Vikunja.

## Workflow

1. Before starting a piece of work, run `vik.py tasks` and find its task. If none fits, create one: `vik.py add "Title" --desc "What and why" --claude`. Then `vik.py start REF`.
2. Split larger work into tasks, one per deliverable the client would recognise, before starting.
3. While working: `vik.py progress REF 50` at milestones; `vik.py comment REF "..."` for decisions, findings or blockers.
4. When the work is done and checked: `vik.py done REF --comment "What changed and how it was checked."`
5. Start commit messages with the task reference (`II-12 Add SST rates`); add `fixes II-12` when the commit finishes the task. The bridge then moves the task to In testing (staging branch) and Done (main branch).
6. New work found along the way becomes a new task.

## Rules

- Every task is assigned to waqas automatically. Add `--claude` when Claude does the work; leave it off for tasks only a person can do (decisions, accounts, payments, anything outside this repository).
- Titles are short, plain and fit for the client to read. Details go in the description or comments.
- Only this project is reachable. Tasks cannot be deleted here: ask an admin to delete one in Vikunja.
- If the tool answers that the key is not valid or has stopped working, stop tracking and tell Waqas Ahmed. A fresh copy of this tooling comes from the dashboard (https://vikunja.lojicloop.com/dashboard#p=II, Claude tooling).

## Commands

| Command | Does |
| --- | --- |
| `vik.py project` | project name, statuses, owner |
| `vik.py tasks [--all]` | open tasks (`--all`: done too) |
| `vik.py show REF` | one task with description and comments |
| `vik.py add "Title" [--desc TEXT] [--status S] [--due YYYY-MM-DD] [--percent N] [--claude]` | new task |
| `vik.py start REF` | move to the in-progress status |
| `vik.py move REF "Status"` | move to any status of the board |
| `vik.py progress REF N` | percent done (0-100) |
| `vik.py done REF [--comment TEXT]` | mark done, with a closing comment |
| `vik.py reopen REF` | back to the first status |
| `vik.py comment REF TEXT` | add a comment (`-` reads standard input) |
| `vik.py edit REF [--title T] [--desc D] [--due D] [--claude/--no-claude]` | change a task |

`--json` before the command prints the raw answer.

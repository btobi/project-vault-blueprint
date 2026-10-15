---
name: meeting-ingest
description: Works a past meeting's notes/transcript (in source/meetings/) into the wiki — distilling each fact into the right topic file, resolving answered open questions, and updating index/log. Use after a meeting has happened and its notes need folding into context/, or when invoked as /meeting-ingest.
---

# Meeting ingest

Take a finished meeting file from `source/meetings/` and work its content into
the wiki (`context/`). Post-meeting counterpart to `/meeting-prep`.

`source/meetings/` is raw and immutable — read it, never rewrite it. Formats:
[[Meeting]], [[Topic]], [[Task]], [[Project]] hubs in `context/categories/`.

## 1. Pick the source

- Ask which meeting to ingest if not given (default: most recent file in
  `source/meetings/` without a matching `context/_log.md` entry).
- Read it fully. Translate to the wiki language (Project facts) where needed.

## 2. Break into bits

Decompose into discrete bits; skip scheduling and pleasantries. Route each:

| Bit | Destination |
| --- | --- |
| Knowledge — fact, decision, answer to / new open question | **Wiki** (`context/`), step 3 |
| Action, self-contained, no artifact | **`projects/tasks.md`** — one `#todo` line with `📅`/`⏳` |
| Action that is complex (deliverable, sub-steps, attachment, AI execution) | **New project**, step 4 |
| Small step (sub-step of an existing project, prep) | Plain `- [ ]` in that project's Plan |

Open questions (knowledge gaps → stay in `context/` as `#todo` if they pass the
impact test, also when raised by a person) are not actions (→ `projects/`).
Never put actions in the wiki.
`⏫` only if the item blocks the project timeline or a pending decision.

An attachment (spreadsheet, doc) belongs to a project: move it into that
project's folder and link it under `Inputs`.

Participants without a file in `context/people/` → create one from
`templates/Person Template.md` (see [[Person]]). Missing from the meeting's
`persons:` → add them there (frontmatter only; never touch the body).

## 3. File knowledge bits

Follow the `/file-context` procedure for every knowledge bit: classify, place
in the right section, strike through answered questions, record
contradictions, skip duplicates, set `updated:`.

## 4. Create projects for complex actions

- Propose the projects first (titles + due dates) and wait for confirmation;
  simple `projects/tasks.md` lines need no gate.
- Create each per the Project hub: folder `<today> <kebab-slug>` (e.g.
  `2026-01-15 acme-cost-check`), project file from
  `templates/Project Template.md`, Inbox file from
  `templates/Project Inbox Template.md` holding the meeting's raw points.
- Fill `Goal`, link the meeting + related wiki pages under `Context`, attachments
  under `Inputs`, draft `Plan` steps. The header task carries the real `📅` due
  date — ask if the meeting didn't state one; `⏫` only if genuinely high-prio.
- Log `## [<today>] project | <slug> created` in `projects/_log.md`.

## 5. Index and log

- `context/_index.md` — entries for any new page/subtopic.
- `context/_log.md` — one entry at the top:
  `## [YYYY-MM-DD] ingest | meeting <filename> → <topics touched>`

## 6. Report back

- Bits filed and where each went.
- Actions created (task lines, projects with due dates).
- Questions answered (struck through) and new ones raised.
- Contradictions, called out explicitly.
- Further-research suggestions (no `#todo` unless confirmed).
- Numbered list of all new todos (text + file).

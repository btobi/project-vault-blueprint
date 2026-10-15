---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Project

One piece of operational work with a deliverable — the control surface for doing it.

| | |
| --- | --- |
| Use for | Complex actions: a deliverable, sub-steps, an artifact, or AI execution |
| Not for | One-line actions (→ [[Task]] in `projects/tasks.md`); knowledge (→ [[Topic]]) |
| Lives in | `projects/<YYYY-MM-DD slug>/` — one folder per project: project file, Inbox file, artifacts |
| Filename | Folder `<created date> <kebab-slug>`; project file `<Project Name>.md`; `<Project Name> Inbox.md`; artifacts `<Project Name> – <Artifact>.md`; all names unique |
| Frontmatter | `type`, `date`, `updated`, `status` (`todo` · `in-progress` · `waiting` · `done`), `due`, `drives` (`AI` · `me` · `AI+me`), `tags` |
| Sections | Header task line, `## Goal`, `## Briefing`, `## Context`, `## Inputs`, `## Open questions`, `## Plan`, `## Findings` (optional, written by `/work`), `## Log` (see `templates/Project Template.md`) |
| Created by | `/file-project`, `/meeting-ingest`, `/shutdown` |
| Processed by | `/work` (next Plan step, close-out); `/file-project` re-run (folds new Inbox thoughts); `/daily`, Dashboard (header task) |
| Lifecycle | `todo` → `in-progress` → `waiting` (header task tagged `#waiting`) → `done`; on `done` the conclusion is folded into the wiki |

## Rules

- One action `#todo` per project: the header task `- [ ] #todo <Name> ⏫ 📅 <due> ➕ <created>`. Omit `⏫` unless it blocks the timeline or a pending decision; omit `📅` if there is no due date. It stays open until `status: done`; tick both together.
- Open questions may carry `#todo` only if they pass the impact test.
- Plan steps are plain `- [ ]`; all todos that emerge stay in this file — never in `projects/tasks.md` or `context/`.
- Goal, due and Plan may change; log every change with its reason in `## Log` (newest first, `- YYYY-MM-DD — <text>`).
- `## Briefing` is regenerated on every `/file-project` run.
- Inbox file (`type: "[[Source]]"`): the user's raw thoughts, append-only, never emptied; processed content ends with `<!-- processed YYYY-MM-DD -->`.
- Outward communication always gets its own artifact file (`type: "[[Communication Draft]]"`), never sent by Claude.

![[Project.base]]

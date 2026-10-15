---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Topic

One subject area of the project, kept current — the heart of the wiki.

| | |
| --- | --- |
| Use for | Durable knowledge on one subject: facts, open questions, impact |
| Not for | Things to do (→ [[Project]] / [[Task]]); dated deliverables (→ [[Report]]); raw notes (→ [[Meeting]], [[Source]]) |
| Lives in | `context/topics/` |
| Filename | `<Topic Name>.md`, Title Case, plain spaces |
| Frontmatter | `type`, `date`, `updated`, `status`, `tags` (optional) |
| Sections | `## Description`, `## Subtopics`; per subtopic `### <Name>` with `#### Current state`, `#### Open questions`, `#### Impact` |
| Created by | Owner decision, from `templates/Topic Template.md` (`/file-context` asks before creating one) |
| Processed by | `/file-context`, `/meeting-ingest`, `/work` close-out (write); `/vault-lint`, `/vault-reindex` (check, catalog) |
| Lifecycle | `draft` → `current` → `stale`; `updated` set on every edit, `date` never bumped |

## Rules

- One file = one topic. The topic set is deliberate; prefer a new `###` subtopic over a new file.
- Facts → `Current state`; knowledge gaps → `- [ ] #todo` under `Open questions`, only if they pass the impact test (`CLAUDE.md`).
- An answered question is struck through (drop `#todo` and date); the answer goes under `Current state`, not next to the question.
- A contradiction is recorded inline with both versions and flagged — never silently overwritten.
- Terse, telegraphic bullets; wikilinks only where meaningful.

![[Topic.base]]

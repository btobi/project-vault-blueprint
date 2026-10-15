---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Person

A person the project deals with — a link target, not a profile.

| | |
| --- | --- |
| Use for | Anyone who appears in meetings, projects or mails; the link target for `persons` and stakeholders |
| Not for | Any judgement about a person — performance, absence, personal details (never recorded) |
| Lives in | `context/people/` |
| Filename | `<First Last>.md` |
| Frontmatter | `type`, `date`, `aliases`, `org`, `role`, `email`; optional `teams_chat_id` (cache for `/teams-read`). No `updated`, `status`, `name` |
| Sections | None — frontmatter only, no body |
| Created by | `templates/Person Template.md`; when a new participant appears in `/meeting-prep` or `/meeting-ingest` |
| Processed by | `vault.py` link hops (e.g. `persons.org~acme`); `/email` and `/teams-read` read and backfill `email` / `teams_chat_id` |
| Lifecycle | Created once; fields backfilled; never deleted while linked |

## Rules

- Business-contact data only; nothing personal or evaluative.
- Aliases hold short names and spellings so links and queries resolve.

![[Person.base]]

---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Task

A single actionable checkbox line that must surface on the dashboards. Also the type of `projects/tasks.md`.

| | |
| --- | --- |
| Use for | Standalone actions; project header lines; knowledge gaps that pass the impact test |
| Not for | Small steps — prep, sub-steps of a project (→ plain `- [ ]` without `#todo`); anything complex (→ [[Project]]) |
| Lives in | `projects/tasks.md` (simple actions), project header lines, `Open questions` in topics and meetings, meeting `Next steps` |
| Filename | — (a line, not a file); the list file is `projects/tasks.md` |
| Frontmatter | Line: `- [ ] #todo <text> ⏫ 🔁 <rule> 📅 <due> ⏳ <scheduled> ➕ <created>` — emojis in this order, all optional except `➕`. List file: `type`, `date`, `updated`, `status` |
| Sections | — (tasks.md is one flat list) |
| Created by | `/meeting-ingest`, `/shutdown`, `/file-context` (open questions), the user |
| Processed by | `/daily`, `projects/Dashboard.md` (Tasks plugin queries); `/vault-lint` (todo hygiene) |
| Lifecycle | open `[ ]` → done `[x] ✅ YYYY-MM-DD` or cancelled `[-]`; stuck → tag `#waiting` / `#blocked` |

## Rules

- Only lines carrying `#todo` are tasks (Tasks plugin global filter); plain `- [ ]` never reaches a dashboard.
- `⏫` only if the item blocks the project timeline or a pending decision.
- Never inside a table — the Tasks plugin can't read it.
- Views (`daily/`, Dashboard) only query tasks; tasks are never stored there.

![[Task.base]]

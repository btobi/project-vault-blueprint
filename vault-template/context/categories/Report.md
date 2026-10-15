---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Report

A dated deliverable: status, findings or a decision ask for a named audience.

| | |
| --- | --- |
| Use for | Deliverables that leave the team: status reports, assessments, decision docs |
| Not for | Living knowledge (→ [[Topic]]); working analyses inside a project (→ [[Analysis]]) |
| Lives in | `context/reports/` |
| Filename | `YYYY-MM-DD <Title>.md` |
| Frontmatter | `type`, `date`, `updated`, `status`, `audience` (`internal` · `management`), `tags` |
| Sections | Free; open with the summary or the decision asked for, then the supporting facts |
| Created by | On request from the owner (Claude drafts, owner finalizes) |
| Processed by | `/vault-reindex` (catalog), `/vault-lint` |
| Lifecycle | `draft` → `current` (delivered) → `stale` (superseded by a newer dated report) |

## Rules

- Delivered reports are not rewritten; changes go into a new dated version.
- Write at the reader's level: decision-relevant facts, no internal detail.
- Every table cell states something; no ranges or caveat-only rows.
- Reports published outside the vault contain no wikilinks.

![[Report.base]]

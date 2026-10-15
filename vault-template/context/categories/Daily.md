---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Daily

Today's generated morning brief — a view, never a store.

| | |
| --- | --- |
| Use for | The day's schedule, focus list and task views |
| Not for | Storing tasks or notes worth keeping (→ [[Task]], [[Topic]], [[Project]]) |
| Lives in | `daily/` |
| Filename | `YYYY-MM-DD.md` |
| Frontmatter | `type`, `date` |
| Sections | `# <date> · <weekday>`, `## Schedule`, `## Focus today`, `## Due today`, `## Overdue`, `## Due in the next 5 days`, `## Waiting on others`, `## Todo hygiene`, `## Notes` |
| Created by | `/daily` (interactive, or headless via `scripts/optional/daily-brief.sh`) |
| Processed by | `/shutdown` (reviews it, carries loose ends from `## Notes` into projects) |
| Lifecycle | Regenerated on every run; only `## Notes` is preserved |

## Rules

- Focus items are plain `- [ ]` linking to their source — never `#todo`.
- Task sections are live Tasks-plugin queries, so they stay correct during the day.
- Without a calendar connector, `## Schedule` notes `calendar unavailable`.

![[Daily.base]]

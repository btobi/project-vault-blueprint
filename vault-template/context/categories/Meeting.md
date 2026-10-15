---
type: "[[Category]]"
date: __SETUP_DATE__
updated: __SETUP_DATE__
status: current
---
# Meeting

A record of one meeting: prep before, notes and outcomes after.

| | |
| --- | --- |
| Use for | Any meeting worth preparing or remembering: briefing, questions, notes, next steps |
| Not for | Distilled knowledge (→ [[Topic]]); follow-up work (→ [[Task]] / [[Project]]) |
| Lives in | `source/meetings/` |
| Filename | `YYYY-MM-DD <Topic> – <Counterpart>.md`, Title Case, plain spaces (counterpart = person, team or organisation met) |
| Frontmatter | `type`, `date` (meeting date), `persons` (list of `[[Person]]` links), `tags` (optional) |
| Sections | `# <Topic> – <Counterpart> — YYYY-MM-DD`, intro line, `## Briefing`, `## Prep`, `## Questions to answer`, `## Open questions`, `## Notes`, `## Next steps` |
| Created by | `/meeting-prep`, or manually from `templates/Meeting Template.md` |
| Processed by | `/meeting-ingest` (into the wiki); `/daily` (flags meetings without a file) |
| Lifecycle | prepped → held (notes added by the user) → ingested (`ingest` entry in `context/_log.md`); raw and immutable after ingest |

## Rules

- `## Prep` holds plain `- [ ]` steps only — never `#todo`, `⏫` or dates.
- `## Questions to answer` are the meeting's purpose: plain bullets, not `#todo`.
- `## Open questions` gets `#todo` only for questions passing the impact test.
- After the meeting, knowledge moves to topics via `/meeting-ingest`; the meeting file is never rewritten.

![[Meeting.base]]

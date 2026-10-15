---
name: meeting-prep
description: Prepares for an upcoming meeting by asking for topic, participants, and questions to answer, then creates a new meeting file with frontmatter, a briefing from the provided info and existing vault context, a plain prep checklist, and researched open questions (Obsidian todos only if they pass the impact test). Use when the user wants to prep for/plan an upcoming meeting, or invokes /meeting-prep.
---

# Meeting prep

Create a new meeting file in `source/meetings/`. Filename, frontmatter and
sections: the [[Meeting]] hub (`context/categories/Meeting.md`) and
`templates/Meeting Template.md` — read the hub first.

## 1. Gather inputs

Ask for whatever the request didn't give — one batched, numbered block:

- Meeting topic
- Participants
- Questions the meeting must answer
- Date (default: today)

Unclear topic or participants → ask, don't guess.

## 2. Gather context

- Search `context/topics/` and `source/` for related content; start from
  `context/_index.md`.
- Collect open `#todo`s on the topic — fold relevant ones into the meeting's
  questions (link them, don't duplicate).
- Resolve participants to `context/people/` files; for a new participant,
  create a person file from `templates/Person Template.md` (see [[Person]]).

## 3. Research the topic

- Web-search the topic for external background and best practices — general
  findings, not claims about the client.
- Combine with the vault scan to derive open questions the user didn't list.

## 4. Create the meeting file

Per the Meeting hub. Content:

- Intro paragraph: purpose and participants, wikilinked to relevant topics.
- `## Briefing` — short bullets: the user's input plus relevant vault context.
- `## Prep` — always present; plain `- [ ]` steps ("have X ready", "align with
  Y") — never `#todo`, `⏫`, `📅` or `➕`.
- `## Questions to answer` — the user's questions as plain bullets.
- `## Open questions` — questions from research/vault scan. Only those passing
  the impact test (root `CLAUDE.md`) become `- [ ] #todo <text> ➕ <today>`;
  the rest stay plain bullets.
- `persons:` frontmatter lists every participant as `"[[First Last]]"`.

## 5. Formatting

- Tab indents; bullets ≤2 sentences.
- Wikilinks only where meaningful. Terse prose.

## 6. Report back

- The file created.
- Relevant open questions elsewhere (pointed to, not duplicated).
- Reminder: after the meeting, add notes and run `/meeting-ingest`.

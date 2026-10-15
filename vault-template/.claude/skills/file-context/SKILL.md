---
name: file-context
description: Files a new bit of information (fact, meeting excerpt, answer to an open question) into the correct topic file under context/topics/, following this vault's conventions. Use when the user pastes a note, quote, or fact and asks to add/file/work it into the context, or invokes /file-context.
---

# File context

Take one input "bit" of information and file it into the right place in
`context/topics/`. Treat `context/` as the single source of truth (root
`CLAUDE.md`). Format of topic files: the [[Topic]] hub
(`context/categories/Topic.md`) — read it first.

## 0. Translate

If the input isn't in the wiki language (Project facts in `CLAUDE.md`),
translate it first.

## 1. Classify

Determine the target topic file and subtopic:

- Start from `context/_index.md`, then the `### ` subtopic headings across
  `context/topics/*.md`; pick the closest match.
- Overlapping topics → pick the more specific one. When two topics keep
  competing for the same kind of bit, note the split rule in both topics'
  `## Description`.
- Nothing fits → prefer a new `### ` subtopic (with the standard children per
  the Topic hub) in the closest file. Don't create a new topic file without
  asking — the topic set is deliberate.

**Classification genuinely ambiguous, or the input has likely typos or missing
detail that changes where/how it is filed → stop and ask.**

## 2. Determine the section

Within the chosen subtopic:

- Fact/statement → short bullet(s) under `#### Current state` (or a more
  specific existing `#####` sub-heading).
- Open question → `- [ ] #todo <text> ➕ <today>` under `#### Open questions`,
  only if it passes the impact test in root `CLAUDE.md` (otherwise a one-line
  gap note). `⏫` only if it blocks the project timeline or a pending decision.
- Answers an existing open question → strike the question through (drop
  `#todo` and the date) and add the answer under `Current state`, not next to
  the question.
- Bits from `source/` or `_inbox/`: never edit `source/`; file the distilled fact.
- Relevant to the project's goal → short bullet under `#### Impact`.
- Reformulate concisely. Ask if the meaning is unclear — don't just transcribe.

## 3. Check for collisions

Skim the target file (and linked topics) for content the bit contradicts or
duplicates.

- Contradiction: don't overwrite. Record both versions inline ("Contradicts X
  recorded elsewhere — unresolved") and flag it in the report.
- Straight duplicate: skip and say so.

## 4. Formatting

- Tab indents for nested bullets; bullets ≤2 sentences, else sub-bullets.
- Wikilinks (`[[Topic]]`, `[[Topic#Heading|alias]]`) only where the bit
  meaningfully relates to another page.
- Never bump `date:`; set `updated:` to today on every wiki file you edit.
- Terse, telegraphic style matching the file.

## 5. Index and log

- `context/_index.md` — new topic/subtopic/page → add or refresh its one-line
  entry. No new page → no change.
- `context/_log.md` — one entry at the top (below the intro):
  `## [YYYY-MM-DD] ingest | <short description> → <file(s) touched>`

## 6. Report back

- File, subtopic and section the bit went to (or the new subtopic created).
- Any collision, called out explicitly.
- **Further research points** the bit raises — suggestions only; no `#todo`
  unless the user confirms.

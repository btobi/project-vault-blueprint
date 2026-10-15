---
name: file-project
description: Turns loose thoughts on a new initiative into a structured project under projects/<YYYY-MM-DD slug>/ — an Inbox file holding the thoughts, plus a project file with goal, briefing, open questions, plan and "look at next", built from existing vault context. Re-run on an existing project to fold in thoughts added to its Inbox since the last run. Use when the user dumps thoughts on a new topic/project/initiative, asks to structure them into a project, asks to process a project inbox, or invokes /file-project.
---

# File project

Inbox for initiatives. The user dumps thoughts; this skill turns them into a
project they can act on. Folder, files, frontmatter, sections and lifecycle:
the [[Project]] hub (`context/categories/Project.md`) — read it first.

| File | Owner | Role |
| --- | --- | --- |
| `<Project Name> Inbox.md` | user | Raw thoughts, append-only, never emptied |
| `<Project Name>.md` | Claude (user reviews) | Structured project: goal, briefing, questions, plan, log |

## 1. Capture

- **New project:** the user dumps initial thoughts in chat, possibly pointing
  at a source (meeting, document, folder).
- **Existing project:** `/file-project <name>` → read its Inbox below the last
  `<!-- processed YYYY-MM-DD -->` marker (no marker = whole file). Nothing new
  → say so and stop.
- Apply the client data policy (Project facts) to the input and any referenced
  source. Customer, health, HR/applicant data or secrets → stop and flag.
- Translate to the wiki language.

## 2. Match

- Compare against existing projects (`vault.py find type=Project --show status,due`):
  titles, Goal, tags.
- Clear overlap → ask: add to the existing project (append to its Inbox, continue
  as re-run) or create a new one.

## 3. Create the files (new project)

- Folder `projects/<today> <kebab-slug>/`; name short, Title Case, unique across
  the vault (check first).
- **Inbox file** from `templates/Project Inbox Template.md`: the thoughts under
  `## <today>`, lightly structured — grouped, typos fixed, nothing added. Then
  the processed marker.
- **Project file** from `templates/Project Template.md`, filled per §4–7.
  Replace every `{{…}}`; drop lines that don't apply — never leave an
  unresolved `[[{{…}}]]` link.

## 4. Gather context (read-only)

Traverse per root `CLAUDE.md` (no permission prompts): `vault.py`, parallel
`Read`, `Grep`/`Glob`; one simple Bash command per call at most.

- **`context/`**: from `_index.md` into topics, reports, people — facts framing
  the initiative, open `#todo`s on it (link, never duplicate), stakeholders.
- **`projects/`**: other projects and `tasks.md` — overlaps, dependencies.
- **`source/`**: named files plus related ones found by search.
- **Calendar**, next 2 weeks, if a calendar connector is available: meetings on
  the topic (subject/time/attendees only). Unavailable → skip, note it.
- Other systems (chat, tickets, wiki) only if the user asks.

## 5. Structure

- **Goal** — one sentence + definition of done.
- **Due date** — from thoughts or a known deadline; none → ask (§6).
- Stakeholders, constraints, unknowns/risks.
- **Look at next** — top 3 things to examine, ranked by how much they could
  change goal, cost or timeline.
- **Re-run:** do the new thoughts change Goal, DoD, due or Plan? Change only
  with a logged reason.

## 6. Clarify

- One batched, numbered round — only for gaps that change Goal, DoD, due date
  or scope.
- Everything else → proceed with a stated assumption, listed in the report.

## 7. Write

Project file, per the hub's sections:

- `## Briefing` — **regenerated every run**: Situation, What we know (with
  wikilinks), Stakeholders, Constraints / deadlines, Unknowns / risks, Look at
  next (1–3).
- `## Open questions` — `#todo` only if it passes the impact test.
- `## Plan` — plain `- [ ]` steps, first one `⏳ <today>`; last steps: review
  with the user, fold the conclusion into the wiki.
- Header task and frontmatter per the hub (`status: todo`, `due`, `drives`,
  `updated`); `⏫` only if high-prio, no `📅` without a due date.

Re-run rules:

| Section | On re-run |
| --- | --- |
| Briefing | Regenerate fully |
| Goal, Plan, due | Revise only if the thoughts change them; log the reason |
| Open questions | Append new; tick answered (`[x]` + `✅ <today>` + answer as sub-bullet) |
| Context, Inputs, Log | Append |

Inbox file: append `<!-- processed <today> -->`; never edit the user's thoughts.

Logs:

- Project `## Log`, newest first: `- <today> — <created | inbox processed>; <what changed>`.
- `projects/_log.md`, top: `## [<today>] project | <slug> <created | inbox processed>`.
- Never `context/_log.md` — this skill only reads `context/`.

## 8. Artifacts

Work that needs its own surface — always outward communication (mail drafts,
messages, agendas) — gets `<Project Name> – <Artifact>.md` in the folder,
`type: "[[Communication Draft]]"` or `"[[Analysis]]"`, `status: draft`, linked
from `## Inputs` and its Plan step. Never send anything; Outlook drafts go
through `/email` if it is enabled.

## 9. Formatting

Tab indents; blank lines around blocks; bullets ≤2 sentences; wikilinks only
where meaningful; todos never in tables.

## 10. Report back

- Paths created/updated; **Look at next**.
- Goal/Plan/due changes and why (re-run).
- Assumptions and skipped sources.
- Numbered list of all new todos (text + file), so the user can pick which to
  keep; remove the deselected ones on reply.

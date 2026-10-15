---
name: daily
description: Assembles the morning brief for today into daily/YYYY-MM-DD.md — pulling today's calendar (if a calendar connector is available), flagging meetings without prep, querying dated tasks, and proposing a ranked focus list. Use at the start of the day, when invoked as /daily, or when run headless by a scheduled job.
---

# Daily brief

Generate today's brief at `daily/<YYYY-MM-DD>.md` — a **view**, regenerated
each run, never a store for tasks. Sections and rules: the [[Daily]] hub.

Tasks are vault-authoritative: read them from the vault. External tickets may
be referenced by link if a task names one.

## 1. Resolve the date

- Today = system date (`date +%Y-%m-%d`), or the date passed as argument.
- File exists → regenerate in place, keeping everything under `## Notes`.

## 2. Calendar (optional)

Only if a calendar connector is available (e.g. Microsoft 365:
`outlook_calendar_search` with `afterDateTime: "<date>T00:00:00"`,
`beforeDateTime: "<date>T23:59:59"`, local time). **No connector → skip this
step, write `calendar unavailable` under `## Schedule`, continue.**

- Dedupe events by subject + start; drop cancelled ones.
- Per event: time range, subject, attendees (names only).
- No matching file in `source/meetings/` (date or counterpart in the name) →
  flag `⚠ no prep` and offer `/meeting-prep`.
- **Guardrail:** subject / time / attendees only — never meeting bodies. Never
  use calendar data to reason about colleagues' absence or performance.

## 3. Gather tasks

Use `vault.py tasks` (see root `CLAUDE.md`) and bucket open `#todo`s:

- **Overdue** — `📅` or `⏳` before today.
- **Due today** — `📅` or `⏳` today.
- **Upcoming** — next 5 days (lookahead only; not a focus-list source).
- **In flight** — projects with `status: in-progress`.
- **Waiting** — `status: waiting`, or tagged `#waiting` / `#blocked`.

Todo hygiene (read-only, never edit todos here), max ~5 one-line findings with
the file as wikilink:

- Duplicates
- Small steps carrying `#todo` (prep, project sub-steps)
- Questions already answered elsewhere
- Stale items (prep for past meetings, long overdue)

## 4. Focus list

- **3–5** items from overdue + due today + in flight.
- Rank: overdue high-prio → today high-prio → in flight → rest.
- One plain `- [ ] <item> — <≤10-word why>` each, item as wikilink to its
  project. Never `#todo`. Honest capacity.
- Note collisions (deliverable due while meetings eat the morning).

## 5. Write the note

```markdown
---
type: "[[Daily]]"
date: <date>
---
# <date> · <weekday>

## Schedule

## Focus today

## Due today

## Overdue

## Due in the next 5 days

## Waiting on others

## Todo hygiene

## Notes
```

Due today / Overdue / Next 5 days are live Tasks queries:

- Due today:
  ```tasks
  not done
  path does not include templates
  (due on today) OR (scheduled on today)
  sort by priority
  ```
- Overdue:
  ```tasks
  not done
  path does not include templates
  (due before today) OR (scheduled before today)
  sort by due
  ```
- Next 5 days:
  ```tasks
  not done
  path does not include templates
  ((due after today) AND (due before in 6 days)) OR ((scheduled after today) AND (scheduled before in 6 days))
  sort by due
  ```

Omit `## Todo hygiene` if there are no findings.

## 6. Log

`daily/_log.md`, top: `## [<date>] daily | brief generated — <n> meetings, <n> focus items`

## 7. Report back (interactive runs only)

Focus list, `⚠ no prep` meetings, hygiene findings. Headless (`claude -p`):
write silently; the note and log entry are the output.

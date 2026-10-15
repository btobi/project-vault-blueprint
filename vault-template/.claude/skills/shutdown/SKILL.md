---
name: shutdown
description: End-of-day wrap — reviews today's daily note, carries unfinished tasks forward, captures loose ends into projects/, and adds a summary to the daily log (daily/_log.md). Use at the end of the workday or when invoked as /shutdown.
---

# Evening shutdown

Close the day cleanly so tomorrow's `/daily` starts oriented.

## 1. Review today

- Open `daily/<today>.md`. For each item in **Focus today** and **Due today**,
  ask or infer done vs. not.

## 2. Carry forward

- Open tasks due today: leave them — they resurface as overdue tomorrow (don't
  duplicate).
- Loose ends in `## Notes` that imply an action → a `#todo` line in
  `projects/tasks.md` (simple, per [[Task]]) or a new project (complex, per
  [[Project]]), with a `📅`/`⏳` date.

## 3. Capture knowledge

- Durable facts from today not yet filed → `/file-context`.

## 4. Log

`daily/_log.md`, top: `## [<date>] shutdown | <n> done, <n> carried, <n> captured`
(`/file-context` runs log in `context/_log.md` themselves).

## 5. Report

One short paragraph: what closed, what carries to tomorrow, anything at risk.

---
name: work
description: Executes one project under projects/<YYYY-MM-DD slug>/<Project Name>.md with the user in the loop — reading its artifact and linked context, doing the next Plan step, writing findings back into the file, and on completion folding the conclusion into the wiki. Use when the user wants to progress/work a project, or invokes /work.
---

# Work a project

Operate a single project. The project file is the control surface: read it,
advance it, write back to it. Keep the user in the loop — propose, don't
surprise. Statuses, header task and log format: the [[Project]] hub.

## 1. Pick the project

- Not named → list open projects
  (`vault.py find type=Project status!=done --show status,due`), ask which.
  Default: due soonest.
- Read it fully (incl. `## Briefing`), its `Inputs` and its `Context` links.
- Inbox has content below the last `<!-- processed … -->` marker → process it
  first with the `/file-project` re-run logic.

## 2. Data check

Before loading any artifact, apply the client data policy (Project facts).
Customer, health, HR/applicant or secret data → stop and flag.

## 3. Do the next step

- Take the first unchecked `Plan` step and execute it.
- Write the result **into the project** (under the step, or a `## Findings`
  block) — not into chat.
- `status: in-progress` while active; `waiting` (+ `#waiting` on the header
  task) when it needs a decision or an external answer; `#blocked` if stuck.
- Tick the step; set `updated:`; add a `## Log` line at the top.
- Never tick the header task here.
- Emerging todos go into this file (`## Open questions` or `## Plan`).
- Goal, DoD, due and Plan may change with circumstances — log the reason and
  refresh `## Briefing` (esp. *Look at next*).
- Outward communication → separate artifact file, linked from `Inputs`.

## 4. Review gate

After a step that produces a judgement (discrepancy, recommendation), stop and
present it for a decision before continuing.

## 5. Close out

- Tick the header task and set `status: done` — together.
- **Fold the conclusion into the wiki** (`/file-context` logic) with a link
  back. The knowledge lives in `context/`; the project becomes a closed record.
- `projects/_log.md`, top: `## [<date>] work | <slug> done → <wiki pages touched>`.
- The wiki fold logs its own `ingest` entry in `context/_log.md`.

---
type: "[[Logfile]]"
date: __SETUP_DATE__
---
# Activity Log

Append-only, newest first (insert new entries directly below this intro). Format: `## [YYYY-MM-DD] <op> | <summary>`.

Ops: `ingest`, `query`, `lint`, `reindex`, `bootstrap`, `report`.

Only changes to `context/`. Operational runs log in `daily/_log.md` (daily, shutdown) and `projects/_log.md` (work, project).

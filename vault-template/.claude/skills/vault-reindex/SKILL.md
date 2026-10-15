---
name: vault-reindex
description: Rebuilds context/_index.md (the wiki catalog / MOC) from scratch by scanning all wiki pages and their frontmatter. Use to bootstrap the index, or to recover it after drift, or when invoked as /vault-reindex.
---

# Vault reindex

Rebuild `context/_index.md` ([[Indexfile]]) from the current state of
`context/`. Use to bootstrap, or when drift is beyond the incremental updates
made by `/file-context` and `/meeting-ingest`.

## Procedure

1. Scan every `.md` under `context/` except `_index.md` and `_log.md`
   (`vault.py find --in context --show type,status`).
2. Per page: `type` and a one-line summary (from `## Description` or the
   opening sentence).
3. Group, in this order:
	- Topics (`context/topics/`)
	- Reports (`context/reports/`)
	- One group per domain folder added under `context/` (folder map in root
	  `CLAUDE.md`)
	- Overview / cross-cutting (top-level `context/` files)
	- Types (`context/categories/`) — one line linking [[Category]] is enough
4. Write `context/_index.md`: keep its frontmatter (set `updated: <today>`),
   intro line, then `## <Group>` with `- [[Page Name]] — one-line summary`.
   Wikilinks by filename only; one terse line per page. `context/people/` is
   not catalogued.

## After rebuilding

- `context/_log.md`, top: `## [YYYY-MM-DD] reindex | rebuilt index (<N> pages)`.
- Report page count per group and any pages skipped for missing frontmatter.

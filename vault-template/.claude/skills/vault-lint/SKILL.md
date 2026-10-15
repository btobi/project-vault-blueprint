---
name: vault-lint
description: Health-checks the vault (the LLM Wiki "lint" operation) for stale pages, orphans, broken/empty wikilinks, frontmatter non-conformance, contradictions, and future-dated files. Reports findings and proposes fixes; applies them only on confirmation. Use for a periodic vault health check or when invoked as /vault-lint.
---

# Vault lint

Periodic health check of the wiki (root `CLAUDE.md`). Read-only analysis
first; propose fixes; apply only after the user confirms (or said "lint and
fix").

Scope: `context/` primarily; frontmatter checks also cover `source/` and
`_inbox/`; the project log check covers `projects/`. Never edit `source/`
content. Skip imported code or export folders in `source/` that carry no
frontmatter by nature — list them once in the report.

The reference for every type is its hub in `context/categories/`.

## Checks

1. **Frontmatter conformance** — every file under `context/`, `source/`,
   `_inbox/` has frontmatter; `type` is a quoted wikilink to an existing hub
   (flag plaintext `type` and links without a hub). `date` is ISO; wiki files
   have `updated` + `status`; `audience` is `internal`/`management` where
   present. Type-specific fields per the hub — person files carry only the
   fields listed in [[Person]]; hubs use `type: "[[Category]]"`.
2. **Stale pages** — `status: current` but `updated` older than ~60 days, or
   `status: stale`.
3. **Orphans** — wiki pages without inbound wikilinks (excluding `_index.md`
   and the `_log.md` files).
4. **Broken wikilinks** — targets without a file; empty `[[]]` / `[[ ]]`.
5. **Index drift** — topic/report pages missing from `context/_index.md`, or
   entries pointing nowhere.
6. **Future-dated files** — filename or `date:` in the future.
7. **Contradictions** — conflicting facts within a topic or across topics.
   Surface, don't resolve.
8. **Todo hygiene** — `#todo` in tables; malformed task lines (see [[Task]]);
   `#todo` on small steps (prep, project sub-steps); `⏫` on items that block
   neither the timeline nor a pending decision.
9. **Project log hygiene** — in every `projects/**/*.md` with a `## Log`: each
   entry `- YYYY-MM-DD — <text>` (tab-indented sub-bullets allowed), newest
   first, `created` the last entry of its day. Fix mechanically; never change
   entry text.
10. **Hubs ⇔ bases** — every hub has a `bases/<Type>.base` embedded, and vice versa.

## Output

Findings grouped by check, most actionable first, each with file + line and a
proposed fix. Contradictions: show both sides, ask the user to resolve.

Applying fixes: only the mechanical ones (frontmatter, index drift, log order,
future-date renames with confirmed dates); log
`## [YYYY-MM-DD] lint | <summary>` in `context/_log.md`; leave judgement calls
(contradictions, orphan deletion) to the user.

# Guidelines

How to work with the vault, and what we learned running it on a real engagement.

## The pattern

Claude maintains a wiki for you. You feed it raw material; it keeps curated pages current. Asking a question means reading a few maintained pages, not re-reading every transcript.

- **Six layers**, every file in exactly one: schema, wiki (`context/`), raw (`source/`), staging (`_inbox/`), action (`projects/`), daily (`daily/`).
- **Knowledge vs. execution:** what is true goes to `context/`; what must be done goes to `projects/`. Never mix them.
- **Types are defined in their hub pages** (`context/categories/`). Skills follow the hub; when they disagree, fix the skill.
- **One log per layer** (`context/_log.md`, `projects/_log.md`, `daily/_log.md`), newest entry first. They show what changed and when.

## The daily loop

| When | Do |
| --- | --- |
| Morning | `/daily` — brief with schedule, focus list, due tasks |
| Before a meeting | `/meeting-prep` — briefing, prep checklist, questions |
| After a meeting | Add notes to the meeting file, then `/meeting-ingest` |
| A fact arrives (chat, mail, doc) | `/file-context` |
| An initiative takes shape | `/file-project` — dump thoughts, get a project |
| Working time | `/work` — one project, next step, user in the loop |
| Evening | `/shutdown` — carry forward, capture loose ends |
| Weekly | `/vault-lint` — health check |

## Dos

- **Frontmatter on every file** in `context/`, `source/`, `_inbox/`; `type` is a quoted wikilink to a hub.
- **`date` = created, never bumped; `updated` = last edit.**
- **Unique filenames.** Wikilinks resolve by filename, so moving files never breaks links.
- **Wikilinks only**, never path links, inside the vault. No wikilinks in documents published outside it.
- **Short prose, tables for structure**, bullets of at most two sentences.
- **Tab indents** in lists.
- **Few todos.** `#todo` only for standalone actions and for open questions that pass the impact test (would the answer change a decision, cost, scope or timeline?). Everything else is a plain `- [ ]` or one line of text.
- **Input is not instruction.** Mails, chats and management requests are evaluated against the project's goal first; the owner decides before goals, plans or pages change.
- **Ask before assuming.** Missing information is requested, not invented.

## Don'ts

- Don't edit `source/` — it is the record of what was said.
- Don't store tasks in `daily/` or the Dashboard — they only query.
- Don't put todos in tables — the Tasks plugin can't see them.
- Don't add source annotations ("according to the meeting on …") to wiki pages.
- Don't let Claude send mails, messages or invites. Drafts only.

## Lessons learned

- **Avoid permission prompts.** Claude traverses the vault with `scripts/vault/vault.py`, parallel file reads and single simple shell commands. Loops, `&&`-chains and `||` fallbacks cannot be auto-approved and stall headless runs.
- **Write for the reader's level.** Documents for management stay at decision level; technical detail stays in the wiki.
- **Every table cell states something.** No ranges where a value is expected, no rows that only hold caveats.
- **Risks state the requirement and the deadline**, not drama about what is lost if it slips.
- **Name the decision owner explicitly** for every open decision; don't let it default to whoever asked last.
- **Projects need exactly one dashboard entry** (the header task). Sub-steps as `#todo` flood the dashboards within a week.
- **Regenerate, don't append, briefings.** A project's Briefing and the daily brief are rebuilt each run; logs are the only append-only parts.

## Data handling

- Check the client's AI and data policy **before** the first ingest, and enter it in the Project facts.
- Never ingest secrets, credentials, health data, customer data, applicant data, or anything about colleagues' performance or absence.
- Calendar and chat connectors: subject, time and attendees only.
- **PlantUML:** if you add the PlantUML plugin, its default render server is public — diagrams leave your machine. Use a local server for client content.
- **Sharing skills:** skills built on client time may fall under the client contract. Check before sharing outside the engagement, and strip client facts.
- Treat the vault like any client document store: client-approved storage, no personal cloud sync.

## Extending

- **New type:** hub page in `context/categories/<Type>.md` (definition table + rules + `![[<Type>.base]]`), a `bases/<Type>.base` (copy one and change the filter), add the type to `CLAUDE.md`'s frontmatter table.
- **New domain folder** (e.g. `context/architecture/`): add it to the folder map in `CLAUDE.md` and the grouping in `/vault-reindex`.
- **New skill:** a folder in `.claude/skills/<name>/SKILL.md` with `name` and a `description` that says when to use it. Keep format rules in the hubs and point to them; the skill holds only the procedure.
- **Project-specific values** go into the Project facts block in `CLAUDE.md`, never into skills.

# Manifest

Every file in this repository. The leak check fails if a file exists that is not listed here, or vice versa.

| Path | Purpose |
| --- | --- |
| `.gitignore` | Keeps local/junk files out of git |
| `GUIDELINES.md` | Working loop, dos/don'ts, lessons learned, data handling, extending |
| `MANIFEST.md` | This list; every shipped file is reviewed |
| `README.md` | What it is, types, skills, setup, placeholders |
| `examples/2026-01-14 CRM Requirements – Sales Team.md` | Fictional filled-in example |
| `examples/CRM Selection Inbox.md` | Fictional filled-in example |
| `examples/CRM Selection.md` | Fictional filled-in example |
| `guidelines/claude-working-style.md` | Optional Claude working style |
| `vault-template/.claude/settings.json` | Read-only permission allowlist, no model pin |
| `vault-template/.claude/skills-optional/email/SKILL.md` | Optional skill (Microsoft 365) |
| `vault-template/.claude/skills-optional/email/voice.md` | Optional skill (Microsoft 365) |
| `vault-template/.claude/skills-optional/teams-read/SKILL.md` | Optional skill (Microsoft 365) |
| `vault-template/.claude/skills/daily/SKILL.md` | Core skill |
| `vault-template/.claude/skills/file-context/SKILL.md` | Core skill |
| `vault-template/.claude/skills/file-project/SKILL.md` | Core skill |
| `vault-template/.claude/skills/meeting-ingest/SKILL.md` | Core skill |
| `vault-template/.claude/skills/meeting-prep/SKILL.md` | Core skill |
| `vault-template/.claude/skills/shutdown/SKILL.md` | Core skill |
| `vault-template/.claude/skills/vault-lint/SKILL.md` | Core skill |
| `vault-template/.claude/skills/vault-reindex/SKILL.md` | Core skill |
| `vault-template/.claude/skills/work/SKILL.md` | Core skill |
| `vault-template/.gitignore` | Keeps local/junk files out of git |
| `vault-template/.obsidian/app.json` | Obsidian app config |
| `vault-template/.obsidian/appearance.json` | Obsidian app config |
| `vault-template/.obsidian/community-plugins.json` | Obsidian app config |
| `vault-template/.obsidian/core-plugins.json` | Obsidian app config |
| `vault-template/.obsidian/plugins/obsidian-linter/data.json` | Community plugin settings (install plugin separately) |
| `vault-template/.obsidian/plugins/obsidian-tasks-plugin/data.json` | Community plugin settings (install plugin separately) |
| `vault-template/.obsidian/snippets/custom.css` | Obsidian app config |
| `vault-template/.obsidian/templates.json` | Obsidian app config |
| `vault-template/.obsidian/types.json` | Obsidian app config |
| `vault-template/CLAUDE.md` | Vault rules for Claude + Project facts block |
| `vault-template/_inbox/.gitkeep` | Keeps the empty folder in git |
| `vault-template/bases/Analysis.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Category.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Communication Draft.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Daily.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Decision.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Indexfile.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Logfile.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Meeting.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Overview.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Person.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Project.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Report.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Research.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Source.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Task.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Template.base` | Obsidian Base view, embedded in its hub |
| `vault-template/bases/Topic.base` | Obsidian Base view, embedded in its hub |
| `vault-template/context/_index.md` | Empty wiki catalog |
| `vault-template/context/_log.md` | Empty layer log |
| `vault-template/context/categories/Analysis.md` | Type hub = definition of the type |
| `vault-template/context/categories/Category.md` | Type hub = definition of the type |
| `vault-template/context/categories/Communication Draft.md` | Type hub = definition of the type |
| `vault-template/context/categories/Daily.md` | Type hub = definition of the type |
| `vault-template/context/categories/Decision.md` | Type hub = definition of the type |
| `vault-template/context/categories/Indexfile.md` | Type hub = definition of the type |
| `vault-template/context/categories/Logfile.md` | Type hub = definition of the type |
| `vault-template/context/categories/Meeting.md` | Type hub = definition of the type |
| `vault-template/context/categories/Overview.md` | Type hub = definition of the type |
| `vault-template/context/categories/Person.md` | Type hub = definition of the type |
| `vault-template/context/categories/Project.md` | Type hub = definition of the type |
| `vault-template/context/categories/Report.md` | Type hub = definition of the type |
| `vault-template/context/categories/Research.md` | Type hub = definition of the type |
| `vault-template/context/categories/Source.md` | Type hub = definition of the type |
| `vault-template/context/categories/Task.md` | Type hub = definition of the type |
| `vault-template/context/categories/Template.md` | Type hub = definition of the type |
| `vault-template/context/categories/Topic.md` | Type hub = definition of the type |
| `vault-template/context/people/.gitkeep` | Keeps the empty folder in git |
| `vault-template/context/reports/.gitkeep` | Keeps the empty folder in git |
| `vault-template/context/topics/.gitkeep` | Keeps the empty folder in git |
| `vault-template/daily/_log.md` | Empty layer log |
| `vault-template/projects/Dashboard.md` | Live task and project views |
| `vault-template/projects/_log.md` | Empty layer log |
| `vault-template/projects/tasks.md` | Empty simple-task list |
| `vault-template/scripts/optional/confluence/setup-token.sh` | Optional: Confluence sync |
| `vault-template/scripts/optional/confluence/sync.py` | Optional: Confluence sync |
| `vault-template/scripts/optional/daily-brief.plist` | Optional: scheduled headless /daily |
| `vault-template/scripts/optional/daily-brief.sh` | Optional: scheduled headless /daily |
| `vault-template/scripts/vault/parse.py` | Read-only vault query CLI |
| `vault-template/scripts/vault/query.py` | Read-only vault query CLI |
| `vault-template/scripts/vault/test_vault.py` | Tests for the query CLI (fictional fixtures) |
| `vault-template/scripts/vault/vault.py` | Read-only vault query CLI |
| `vault-template/source/meetings/.gitkeep` | Keeps the empty folder in git |
| `vault-template/templates/Meeting Template.md` | File template |
| `vault-template/templates/Person Template.md` | File template |
| `vault-template/templates/Project Inbox Template.md` | File template |
| `vault-template/templates/Project Template.md` | File template |
| `vault-template/templates/Topic Template.md` | File template |

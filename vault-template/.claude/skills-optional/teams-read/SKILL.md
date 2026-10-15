---
name: teams-read
description: Reads recent Microsoft Teams messages (1:1 chats, group chats, channels) via the Microsoft 365 connector — the fast path that skips discovery by reading cached chat IDs from the vault's person files. Use when the user wants the last messages with/from someone, to catch up on a chat or channel, or invokes /teams-read.
---

# Teams read

Read Teams messages **fast** by skipping tool-schema discovery and people/chat
search — the two round-trips that make a naive read slow.

Read-only. Sending is a separate, explicitly confirmed action (not this skill).
Requires the Microsoft 365 connector.

## Fast path

### 1. Load the tools in ONE call

```
ToolSearch: select:mcp__claude_ai_Microsoft_365__read_resource,mcp__claude_ai_Microsoft_365__teams_list_chats,mcp__claude_ai_Microsoft_365__search_people
```

`read_resource` alone covers a known chat ID; the other two are for discovery (2b).

### 2. Resolve the chat ID

**2a — Known person (preferred).** `teams_chat_id` in
`context/people/<Name>.md` frontmatter, e.g.:

```
grep -h teams_chat_id "context/people/Alice Example.md"
```

Known group chats (no person file) — cache them here:

| Chat | ID |
| --- | --- |
| <!-- e.g. Project team (group) --> | <!-- chat ID found via step 2b --> |

**2b — Unknown person / missing ID.** Only then discover: `search_people`
and/or `teams_list_chats` (the oneOnOne whose members include the
counterpart). **Backfill** the ID into the person file (or the table above).

### 3. Read the messages

```
read_resource  uri: teams:///chats/<CHAT_ID>/messages
read_resource  uri: teams:///teams/<TEAM_ID>/channels/<CHANNEL_ID>/messages
```

One read returns ~50 messages, ordered by **last-updated** — a just-sent
message can lag; say so if recency matters.

## Present

- Table: time (UTC → time zone from Project facts), sender, message.
- Strip HTML; flag cut previews.
- Short assessment after the table: open threads, who awaits a reply.

## Guardrails

- Sending is external communication → only on explicit user confirmation.
- Never use chat data to reason about colleagues' absence or performance.

## Maintenance

New frequent contact → discover once (2b), backfill. Chat IDs are stable.

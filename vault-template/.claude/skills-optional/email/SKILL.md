---
name: email
description: Drafts an e-mail or a meeting invite in the owner's voice via the Microsoft 365 connector — new mails and replies (reply / reply-all) as Outlook drafts, and meeting invites (with agenda) as an attendee-less calendar placeholder plus invite text; recipients resolved from the vault's person files. Never sends. Use whenever the user wants to write, draft, answer, or forward something by e-mail, or invite people to a meeting, or invokes /email.
---

# E-mail & invite

Draft a mail or meeting invite in the owner's voice (Project facts in root
`CLAUDE.md`, style in `voice.md` next to this file). Never send — sending stays
with the user.

Requires the Microsoft 365 connector. Not connected → write the text into the
vault (project artifact, [[Communication Draft]]) and say so.

## 1. Clarify input first

Content unclear → ask, one batched, numbered block:

- What's the point / desired outcome?
- Rough content as bullets (if not given).
- Mail: new or reply? Reply to which mail?
- Invite: date, time, duration, attendees? (Default 30 min, online meeting.)

Clear enough → go to step 2. Pull facts from the vault instead of asking.

## 2. Load tools in ONE call

Mail:

```
ToolSearch: select:mcp__claude_ai_Microsoft_365__search_people,mcp__claude_ai_Microsoft_365__outlook_create_draft,mcp__claude_ai_Microsoft_365__outlook_email_search,mcp__claude_ai_Microsoft_365__outlook_create_reply_draft,mcp__claude_ai_Microsoft_365__outlook_create_reply_all_draft
```

Invite:

```
ToolSearch: select:mcp__claude_ai_Microsoft_365__search_people,mcp__claude_ai_Microsoft_365__find_meeting_availability,mcp__claude_ai_Microsoft_365__outlook_create_event
```

## 3. Resolve recipients

1. `email` from `context/people/<Name>.md` (filename or `aliases`).
2. Missing → `search_people`; prefer an address in the client mail domain
   (Project facts).
3. Backfill `email` (and empty `role`) into the person file.
4. Several plausible matches → ask.

## 4. Write

Language: communication language (Project facts). Address and sign-off per
`voice.md` (internal vs. external recipients).

### Phrasing rules (mail and invite)

- **Write fresh for the recipient.** Never condense an internal doc 1:1 — wrong level of detail.
- **Start directly.** One short intro line; no metadata header (prices, deadlines, IDs) up front.
- **Plain words, no project jargon.** No ticket IDs or internal code names.
- **Problem, not plan.** Leave out internal milestones unless the recipient needs them to decide.
- **First person for own work and opinion.** "I checked …", "I would ask for …".
- **Proposals, not facts.** "We should …" — never present an open action as done.
- **Hedge what may change.** "As of today" for facts still in negotiation.
- **Stay neutral on open points.** Don't prejudge solutions or assign tasks to recipients in writing.
- **Sensitive topics not in writing.** Personnel, individual contracts, works council → in person.
- **Name trade-offs.** Add the caveat when a demand has a cost.
- **Only decision-relevant numbers.** Before/after and the delta; drop derivations and minor amounts.
- **Add nothing unasked.** No summary or extra point the user didn't request.
- **Short.**

### Mail format

- Numbered short headings per topic, otherwise plain sentences. No bold, no nested bullets.
- Each point 2–4 sentences.

Example (fictional):

```
Hi Dan,
here is my short take on the design-software licence renewal.

1. Seat count – too high
We pay for 40 seats, but only 26 people logged in during the last quarter. We should renew 30 seats and add more when needed. That saves about 1,400 € a year.

2. Price increase
The list price rises by 8 %. I would ask for the old price in exchange for a two-year commitment, depending on how much flexibility we want to keep.

Best regards
Alice
```

### Invite format

- **Subject:** the topic in plain words.
- **Intro, one sentence:** the invitation, why we need to talk, what must be decided.
- **Agenda:** numbered points with short sub-bullets; open questions phrased as questions.
	- An open or sensitive point stays one neutral line without sub-bullets.
- No time allocations per point, no goal/result block.

Example (fictional):

```
Hi Dan, hi Erin,

let's plan the office move to the third floor together. The new space is ready in March, and we need to decide when each team moves and what happens to the meeting rooms in between.

Agenda

1. Timing
	- Which team moves first?
	- Can we avoid the end-of-quarter weeks?
2. Meeting rooms during the move
	- Which rooms stay bookable, which close?
3. Desk assignment
4. Who coordinates with facilities?

Best regards
Alice
```

## 5. Create the draft

### Mail

- New → `outlook_create_draft`, `bodyType: "html"`; paragraphs in `<p>`, line breaks `<br>`, headings `<p>1. …</p>`. Use only `p`, `br`, `ol`, `ul`, `li` — no `span`, `font` or images.
- Reply → find the original via `outlook_email_search`, then `outlook_create_reply_draft` (or `_reply_all_draft`).
- No signature is added — the sign-off is the whole closing.

### Invite

`outlook_create_event` **with attendees sends invitations immediately**.

1. Check the slot with `find_meeting_availability` (UTC). Busy → propose the nearest free slots.
2. Save the invite (subject, slot, attendees, text) in the vault: under `## Invite (draft)` in the project's agenda artifact, or the meeting file.
3. Create a placeholder event **without attendees** (`isOnlineMeeting: true`, `bodyType: "html"`). The user adds attendees and sends.
	- User sends manually → skip.

## 6. Report

- The text in chat, plus the draft's or placeholder's `webLink`.
- One line per assumption (recipient resolved, address form, slot free).
- **Never call `outlook_send_draft` or `outlook_send_mail`, and never `outlook_create_event` with attendees** — sending only on an explicit, separate user instruction.

---
name: session-handoff
description: Use when ending a session with unfinished work, when someone says "hand off" / "pick this up tomorrow" / "save state", or when context is running low mid-task. Writes the one file a cold future agent reads first to resume.
---

# session-handoff

A handoff is the file a future agent, with none of this conversation, reads **first** to resume the work. It is present-tense state plus resume steps. It is never a story of the session.

**Where:** `<handoffs_dir>/handoff-<topic-slug>.md` (config). One file per work stream; **update it in place** on later sessions. Parallel handoff files fork and go stale.

## The file is this template (all sections, this order)

```markdown
---
topic: <slug>
updated: <YYYY-MM-DD HH:MM TZ>
status: <active | blocked | done>
---
# Handoff: <topic>

## Resume here (do these, in order)
1. <action>: <exact target: file path, URL, ID or command>

## Current state
- <fact> [evidence: <how it was verified: command run, test output, commit, URL checked>]
- <fact> [UNVERIFIED: <why you believe it>]

## Blockers / waiting on
- <who or what>: unblocked by <a specific event>

## Gotchas (will bite a cold agent)
- <non-obvious trap found this session>

## Pointers
- <note, repo or doc>: <what deeper context is there>
```

## Rules that make it trustworthy

- Every current-state fact carries `[evidence: …]` or `[UNVERIFIED: …]`. A fact you can't tag honestly stays out.
- Evidence means something you saw **this session**: an ID you read, a command you ran, a file you opened. Writing plausible evidence to fill the slot ("logs show it works") is exactly the failure this rule exists to stop.
- Every ID, URL, path and setting name appeared word for word in this session. Never a plausible one.
- Resume steps name exact targets. "Re-enable the nodes" fails; "re-enable nodes 'Fetch' and 'Draft reply' in workflow `<id>`, then publish" resumes.
- Pointers link to deeper context; don't paste it in.
- No secrets and no personal data. Handoffs get synced and shared like any other file.

## Common mistakes

- A narrative recap ("first we built, then we fixed…"): the next agent re-derives everything. Write present truth.
- Filler where knowledge ends ("credentials will auto-link"): the next agent acts on fiction. Tag it UNVERIFIED or leave it out.
- Saving it somewhere other than `handoffs_dir`: it is never found.

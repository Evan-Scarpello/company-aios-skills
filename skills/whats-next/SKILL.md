---
name: whats-next
description: Use when someone asks what's pending, what to work on next, or where things were left ("what's on deck", "catch me up"), says "continue" or "resume X" without a pointer, or a fresh session needs to find the work in flight. Answers from a few fixed pointer files instead of crawling the whole notes folder.
---

# whats-next: orientation without the crawl

The biggest cost at the start of a session is re-orientation: reading half the notes folder to work out what is going on. Answer "what's next?" from fixed pointers instead, at most 7 file reads.

Settings (config): `handoffs_dir`, `state_file`, `daily_logs_dir`, `needs_you_file`.

## Reads, in order

| # | Read | Why |
|---|---|---|
| 1 | `handoffs_dir`: list it, read the files changed in the last 14 days | Live mid-task handoffs: the usual meaning of "continue" |
| 2 | `state_file` (your STATE.md) | What is live, what is blocked, the top focus |
| 3 | The newest 1–2 daily logs | What actually happened most recently |
| 4 | `needs_you_file` and your memory index (if already loaded) | What waits on the human; standing projects |

## Hard limits

- No searching across the whole notes folder. If the pointers disagree or look stale, say so and ask.
- Don't open individual project notes unless the person picks one.
- If "resume X" names something with a handoff file, skip orientation: read that handoff and start.

## Output (exactly this shape)

1. **In flight:** a table: `Project | Status | Next concrete action | Pointer file`. Only items with a live handoff, or touched in the last ~10 days.
2. **Recommendation:** one line: which to resume and why (deadline first, then blocked-on-the-human, then momentum).
3. **Resume prompts:** for the top 3 rows, a one-line prompt that names the pointer file, for example
   `Resume the billing export: read <handoffs_dir>/handoff-billing-export.md and continue from "Resume here".`

## Common mistakes

- Treating STATE.md as complete. It lags behind; handoffs and the newest daily log win.
- Listing all 30 items. People want the resumable few, not a census.
- Answering "continue" from memory instead of reading pointer 1 first.

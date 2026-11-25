---
name: needs-you
description: Use when the human asks what is waiting on them ("what's blocked on me", "my queue", "open loops", "/needs-you"), or to refresh the single needs-you list after new daily logs or handoffs are written.
---

# needs-you: one list of everything only the human can do

Agents finish their side the same day. The 15-minute jobs only the human can do (sign in to something, pick between two options, approve a spend, make a call) then stall for days, scattered across a dozen notes and chat threads. This skill keeps **one** list, sorted by how long each item has waited, and never brings back an item that is finished.

Settings (config): `owner_name`, `daily_logs_dir`, `handoffs_dir`, `needs_you_file`.

## Procedure

1. **Read the sources** from the last 14 days: every "Open loops" / "Blocked on" / "Needs you" section in the daily logs, every handoff's "Blocked / waiting on" section, and any decision cards still open.
2. **Keep only what needs the human personally.** Signals: "<owner_name> to…", "needs <owner_name>", sign-ins in their own browser, decisions, approvals, spending, anything on their personal accounts or devices.
   - Drop anything an agent can do (searches, code, drafts, analysis): that is not their job.
   - Things waiting on other people go under `## Waiting on others (not you)`.
   - Items for projects that were stopped: drop them, with one footnote naming the decision that stopped the project.
3. **Merge by meaning.** The same task worded three ways on three days is one item; `first seen` is its earliest date.
4. **Clear only on evidence.** An item is done only when a later note says so (a done mark, or a decision that replaces it). An item missing from later notes is NOT done. Cleared items stay under `## Recently cleared` for 14 days, so the next refresh can't bring them back.
5. **Write the whole file** (`needs_you_file`):
   ```markdown
   ---
   type: needs-you
   updated: <YYYY-MM-DD>
   ---
   ## <project area 1>
   - [ ] <task in plain words> · ~<minutes>m · first seen <YYYY-MM-DD> · unblocks: <what it unblocks>
   ## Waiting on others (not you)
   ## Recently cleared
   - [x] <task> · cleared <YYYY-MM-DD> (first seen <YYYY-MM-DD>)
   ```
   Oldest first in every section.
6. **Reply with the 3 oldest open items**, one line each, with how many minutes each takes.

## Rules

- Each line must make sense to someone who has just woken up: name the project and the thing. Never "it", "#3" or "option B".
- This skill reads notes and writes one file. It sends nothing and schedules nothing.
- Never copy personal data from the sources into the list.

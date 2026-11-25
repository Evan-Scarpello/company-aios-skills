---
name: morning-brief
description: Use when the coordinator seat is asked for the daily brief, or when a scheduled brief fires ("morning brief", "brief me", "what happened overnight"). Produces a brief of at most 12 lines for the human, built from the sources, not from memory.
---

# morning-brief

The human reads this on a phone, often hours later, with none of your context. It is the one message a day that must be right.

Settings (config): `owner_name`, `state_file`, `needs_you_file`, `queue_file`, `room_channels`.

## Before you write a word: re-sweep the sources

1. Room channels since the last brief (all of them, not only the ones you posted in).
2. The work queue: rows whose status changed.
3. Every seat's output folder: files changed since the last brief.
4. Handoffs and decision cards still open.
5. `needs_you_file`: refresh it (the `needs-you` skill). Close what's done, add what's new, flag what's overdue.
6. System health: seats online, disk use, the newest backup and whether it finished.

Check claims yourself before they go in the brief. "Lane 3 says it shipped" is not "shipped" until you've seen the file, the deploy or the test output.

## The format (at most 12 lines)

```
BRIEF <Day MM-DD>
DONE since last brief: <item (checked: how)>; <item (checked: how)>
IN PROGRESS: <item> (<who>, ETA <day time>)
BLOCKED / NEEDS YOU: <one line each, the oldest first, minutes each>
NEXT: <top 3>
SYSTEM: <seats online>, disk <n>%, last backup <time> <ok/failed>
```

## Rules

- **Outcome first, absolute dates.** "Tue 03-10, 7:00 AM", never "next week". Status words people can trust: "done (checked: …)", "started", "blocked on <who>", "not done". Never "should work".
- **Every line stands alone.** Name the project and the thing. No "it", "#3", "option B" or "as discussed".
- **Questions don't hide in the brief.** Each decision goes out separately as a decision card (see `templates/DECISION-CARD.md`).
- If a source couldn't be read (a script failed, a folder was missing), say so in the brief. A silent gap reads as "all clear".

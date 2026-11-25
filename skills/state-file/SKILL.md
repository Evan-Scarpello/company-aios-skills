---
name: state-file
description: Use at the start of every session of a long-running seat (coordinator or lane) and after every milestone, or when someone says "you got reset", "pick up where you left off", "update your state". Keeps one STATE.md that lets a freshly started seat resume in five minutes.
---

# state-file: survive a reset

Long-running seats get reset: context fills, the machine restarts, a session is replaced. Without a state file, the new session rebuilds the world from chat history and gets it subtly wrong. With one, it reads one file and resumes.

Settings (config): `state_file` (one per seat).

## At the start of a session

1. Read `state_file` before anything else, then only the files it links to under "Read next".
2. Re-create anything listed under "Jobs that die with the session" (session-only schedules, watchers).
3. Say in one line what you resumed: `resumed from STATE.md (updated <time>): doing <task>, ETA <time>`.

## Keep it current

Update it **after every milestone and before any long task**, never "at the end". Ends are where resets happen. Use `templates/STATE.md`. The sections that matter most:

- **Role and goal:** one paragraph. Why this seat exists and what "winning" means this week.
- **Start-of-session routine:** the exact reads, in order.
- **Live right now (with undo):** a table of everything running in production that this seat changed: what, its state, the exact undo command.
- **In flight:** each task, who has it, next step, pointer file.
- **Waiting on the human:** the item, since when, and the card or message where it was asked.
- **Jobs that die with the session:** anything to re-create after a reset.
- **Done (don't redo):** recent finished work, one line each, so a fresh session doesn't repeat it.

## Rules

- Present tense, facts with evidence. Same tagging as `session-handoff`: `[evidence: …]` or `[UNVERIFIED: …]`.
- Keep it short enough to read in five minutes. Move old "Done" lines to a dated archive file.
- No secrets. Say where a secret lives, never what it is.

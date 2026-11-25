---
name: session-self-audit
description: Use when someone asks to audit past sessions or Claude usage ("look through everything we've done", "find recurring patterns", "what's wasting tokens", "build skills from our history", "monthly self-audit"), or any request to mine conversation history for gaps, waste or skill ideas.
---

# session-self-audit: mine history in parallel, build only what recurs

## 1. Fan out three parallel read-only agents

| Agent | Reads | Returns |
|---|---|---|
| Skills | `~/.claude/skills/*/SKILL.md`, `~/.claude/commands/` | Weak or stale skills, broken references, skills that never fire |
| Notes | your daily logs, topic notes, STATE.md, needs-you list | Recurring work with dates, recorded pain points |
| Transcripts | `~/.claude/projects/*/*.jsonl` (top level only) | Per session: the ask, the skills used, the friction |

All three mask personal data in what they return.

## 2. How to scan transcripts (the part that gets reinvented)

- Top-level `*.jsonl` only. Ignore `<session-id>/subagents/` folders. Skip the current session.
- Per file: the first few user messages and any summary lines. Never read whole multi-megabyte files.
- **File modified times lie** (a copy or restore stamps them all the same). Date a session by the timestamp on its first line.
- Note per session: what was asked, which skills fired, whether the work was improvised, and the friction (permission fights, repeated failed calls, facts rediscovered).

## 3. The bar for building something

- A gap becomes a build only with **recurrence: 2 or more separate sessions** (or one session plus a written "make this a skill" note). One-offs get a "watch" flag.
- Collect the opposite signal too: skills that existed but didn't fire. Fix their descriptions instead of building new ones.
- Rank token waste by cost. The usual top three: re-orientation crawls through notes, facts derived again, and whole-file reads.

## 4. Deliverables

1. A ranked gap list with session-level evidence.
2. New or improved skills, written test-first: a recorded real failure counts as the failing case. Check every file a skill references exists.
3. Friction and token findings, each with a fix.
4. Update your memory index and notes at the end.

## Common mistakes

- Reading transcripts one by one in the main context. Always hand it to agents; the files are huge.
- Building a skill from one occurrence. The skill list bloats and the right skill stops firing.
- Auditing transcripts but skipping the notes, or the other way round. Each catches gaps the other can't see.

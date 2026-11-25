---
name: notes-sync
description: Use when someone says "sync notes" / "save this conversation", at the end of a working session, or to backfill a past date. Distills Claude Code sessions into a daily log plus durable topic notes (Obsidian-style markdown), written for an agent to re-read fast, with personal data masked.
---

# notes-sync: sessions into notes an agent can recall

Conversations vanish; notes stay. This turns sessions into a **daily log** and **topic notes** that put the current truth first, so the next session finds the answer before the history.

Settings (config): `notes_dir` (holds `Daily/`, `Topics/` and an index note), `transcripts_dir` (Claude Code keeps one `<session-id>.jsonl` per session under `~/.claude/projects/<project>/`).

## Modes

1. **Current session** (default): distill the conversation you are in, from context.
2. **A date** (`/notes-sync 2026-01-31` or `today`): read every top-level `*.jsonl` with messages on that date and merge them into one daily log. Ignore `<session-id>/subagents/` folders: those are worker logs, not the conversation. Date a session by the timestamp on its **first line**, not by the file's modified time (bulk copies rewrite modified times).

## Hard rule: mask personal data (this overrides "capture everything")

Never write: government ID or tax numbers; bank, card or routing numbers; birth dates, home addresses, personal phone numbers or emails; pay figures; the contents of tax or ID documents; record IDs that identify a specific person or customer. A customer's name tied to money gets generalized ("a mid-five-figure deal", not the name and amount). Keep the decision, the mechanism and the structure; drop the identifiers. When unsure, generalize.

## Daily log: `Daily/YYYY-MM-DD.md`

Frontmatter: `type: daily-log`, `date`, `projects: []`, `tags: []`, and `sessions:` as a **list of session IDs** (the transcript file names), never a count. When merging into an existing log, append IDs; never replace the list. A list can be checked for gaps later; a count can't, and a single log can hide every other session that day.

Body (skip empty sections): `## Summary` (2–3 lines) · `## Decisions` (what and why) · `## Facts established` · `## Artifacts` (files with paths) · `## Open loops` · `## Topics` (`[[slug]]` links).

## Topic note: `Topics/<slug>.md`

Frontmatter: `type: topic`, `slug`, `created`, `updated`, `tags`, `related`. Body: **Current state first**: the answer, as dense present-tense bullets. Then `## Log`, newest entry first.

## Procedure

1. Pick the scope (this session or a date).
2. Extract while masking: decisions, durable facts, files touched, open loops, topics.
3. Write or merge the daily log; never duplicate a fact already there; append every session ID you read.
4. For each topic: create or update its note: refresh "Current state", add a dated log entry at the top.
5. Add any new topic to the index note.
6. One good pass, terse. No open-ended loops.

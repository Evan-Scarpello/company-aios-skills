---
name: cross-device-handoff
description: Use when someone asks for a prompt to paste into another machine, app or Claude session ("give me a prompt for my other laptop", "write something I can paste over there to continue this"), or wants skills, settings or in-progress work moved to another device.
---

# cross-device-handoff: a paste-prompt that works on arrival

The deliverable is **one fenced plain-text block** the person copies whole. The target session has none of this conversation and none of this machine's files, so everything it needs rides inside the prompt.

## Decide the shape first

- **Same machine, different app:** pointers to local paths are fine; don't inline.
- **Different machine:** inline every file it needs, word for word, with paths rewritten for the target.
- **"Set up this fresh machine / make it behave the same":** if you keep an install runbook, point at that runbook (in the target's own copy of your notes) and only write a prompt for what the runbook does not cover.
- **Synced folders are not a delivery method.** Sync lags and can silently keep the last writer's copy. Inline anyway, and if both machines edited the same notes that day, tell the target to look for conflict copies.

## The prompt is this template (all parts, this order, one fenced block)

```
<one-line goal>

FILL THESE IN FIRST (only if something is genuinely unknown; otherwise leave this block out):
- <thing only the person knows>

Context: you are on <target machine>. Check with `whoami` (expect <user>).
If the user or the paths below don't match, STOP and say so.

1. <step>: <exact path or command ON THE TARGET>
2. ...
N. Verify: <an observable check: file exists, skill listed, command exits 0>
Report back: <what to confirm when done>

--- payload: <target path for file 1> ---
<full file content, paths already rewritten for the target>
--- end payload ---
```

## Assembly rules

- **You do the copying.** Read each payload file in this session and inline it. Never ask the person to "open X and paste it below".
- Rewrite machine-specific paths before inlining, and tell the target to flag any assumption that doesn't hold instead of silently keeping it.
- **No secrets in the prompt.** It travels through chat. Point at where the secret lives on the target.
- If the target machine has stricter rules (a work machine, a production box), don't include steps that would trigger production writes or outbound messages without a confirmation on that side.
- Deliver the block as plain text in your final message.

## Common mistakes

- Writing a summary instead of a paste-ready prompt. If it can't be pasted and left alone, it's the wrong shape.
- Pointing the other machine at this machine's paths: dead on arrival.
- Leaving out the verify and report-back steps: the target ends in an unproven state.

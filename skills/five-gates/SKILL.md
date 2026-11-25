---
name: five-gates
description: Use on non-trivial multi-step work (debugging, edits based on someone else's diagnosis or a stated premise, ambiguous builds, data migrations) or any change about to be declared done. Runs the work through five gates: scope, evidence, attack the plan, verify, report calibrated. Skip for trivial one-step edits.
---

# five-gates: working discipline that transfers between models

Intelligence doesn't transfer between models; working discipline does. Run every non-trivial task through five gates, in order. The gates are cheap, and skipping one is how confident wrong answers happen.

Calibrate first: for a trivial, reversible one-step task, gates 1–3 take a moment's thought. Don't pad small jobs with ceremony.

## Gate 1: Scope

State the actual outcome wanted (not just the literal instruction), the deliverable, and the unknowns: what would make this plan wrong? Match effort to the task: one lookup for a simple fact, 3–5 for a normal task, 5–10+ for deep research.

## Gate 2: Evidence before action

Before changing anything, look at the live state the request depends on: the actual file, the actual data header, the actual config, the actual error. A prompt implying a file exists doesn't mean it does. Remembering something doesn't mean it is still true.

For any "change X because Y": **check Y, then change X.** If the live state contradicts the premise, don't make the change. Report what you saw and stop. That includes the tempting middle path: "I'll change it now and it'll be right once the new data arrives" turns a working system into a broken one on an unverified claim.

## Gate 3: Attack your plan

Before executing, argue against it: which input breaks this? Which failure haven't you checked? A diagnosis someone hands you (a comment, a README, "it's the tax function") is a hypothesis to test, not a fact. Reproduce the symptom and trace the real cause. Root cause before fix.

## Gate 4: Verify before "done"

Run it and watch it work on real data. No "this should work now" without having run it. If your change made things worse, go back to the last known-good state before handing back. Never leave it broken while waiting on a decision. If an attempt fails, change the approach before retrying; never rerun a failed attempt unchanged.

## Gate 5: Report calibrated

Lead with the outcome in one sentence. Keep what you verified (ran and saw) separate from what you assumed. Prose first, tables only for truly tabular facts. At most one question back, and answer what you can first. If something went wrong, say exactly what and stay on it.

## Standing habits

- Minimal diffs: change what the outcome needs. Fixing the real bug is in scope even when the request pointed at the wrong place; refactoring nearby code is not. Flag adjacent issues instead of silently fixing them.
- When directing sub-agents: plan carefully, hand mechanical work to cheaper models, and check results as they return.

## Red flags: go back a gate

- About to edit on a premise you haven't looked at: Gate 2.
- About to write "should work" or "is fixed" without running it: Gate 4.
- About to hand back a broken state with options: revert first, then Gate 4.
- Report longer than the work: Gate 5. Cut 30% with no information lost.

---
*Credit: the five-gate framing was inspired by a public video by Nate Herk on making other models work with a stronger model's discipline. This text is our own write-up and test of the idea.*

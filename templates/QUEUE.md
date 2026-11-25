# Work queue

One row per task. The COO adds rows and assigns lanes; a lane changes only the status of its own rows. Back this file up before editing it, and match a row by number **and** lane (numbers get reused).

| # | Lane | Task | Status | Review | Deadline | Pointer |
|---|---|---|---|---|---|---|
| 1 | lane1 | <task> | started / at review r1 / FIX r2 / PASS / installed / blocked on <who> | <REVIEW file> | <Day MM-DD> | <brief path> |

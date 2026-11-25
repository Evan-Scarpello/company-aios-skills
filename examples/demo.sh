#!/usr/bin/env bash
# 60-second tour of the review gate, in a throwaway folder. Nothing outside it is touched.
#   bash examples/demo.sh
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
P="python3 $repo/skills/review-packet/scripts/packet.py"
V="python3 $repo/skills/review-verdict/scripts/verdict.py"
d="$(mktemp -d)"; trap 'rm -rf "$d"' EXIT
cd "$d"

echo "== 1. A lane writes a change and a README for the reviewer"
printf 'def add(a, b):\n    return a + b\n' > calc.py
cat > README.draft.md <<'MD'
# calc: add()
## Bottom line
add() works; 1 test passes.
## Not checked
Large numbers, non-numbers.
## Undo
git revert <commit>
MD

echo; echo "== 2. It builds a packet (files + SHA256SUMS)"
$P build --out packet-r1 --round 1 README.draft.md:README.md calc.py
digest="$($P digest packet-r1)"

echo; echo "== 3. The reviewer answers. (This review is written by the demo, for illustration.)"
printf '# calc review round 1\n\nPASS\n\nChecked: add(). Digest %s\n' "$digest" > CALC-REVIEW-r1.md
$V classify CALC-REVIEW-r1.md

echo; echo "== 4. No install without a go record for this exact digest"
printf '{"decision": "GO", "digest": "%s", "by": "coo"}\n' "$digest" > go.json
$V install-check --review CALC-REVIEW-r1.md --packet packet-r1 --go go.json

echo; echo "== 5. Someone edits a file after the review..."
echo '# sneaky edit' >> packet-r1/calc.py
$V install-check --review CALC-REVIEW-r1.md --packet packet-r1 --go go.json || echo "   -> refused (exit $?), as it should be"

echo; echo "== 6. Round 4 does not exist: the third FIX becomes a decision for the human"
printf '# calc review round 3\n\nFIX\n' > CALC-REVIEW-r3.md
$V card --review CALC-REVIEW-r3.md --item calc --out DECISION-CARD.md || true
sed -n '1,4p' DECISION-CARD.md
$P build --out packet-r4 --round 4 README.draft.md:README.md calc.py || echo "   -> round 4 refused (exit $?)"

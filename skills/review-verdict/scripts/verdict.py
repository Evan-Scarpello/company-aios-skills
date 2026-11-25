#!/usr/bin/env python3
"""Read a reviewer's verdict and decide the next step, with a hard limit on review rounds.

    verdict.py classify REVIEW.md [--round N]
    verdict.py card --review REVIEW.md --item NAME --out DECISION-CARD.md [--round N] [--max-rounds 3]
    verdict.py card-ready DECISION-CARD.md
    verdict.py install-check --review REVIEW.md --packet DIR --go GO.json

classify   prints PASS or FIX and the round. Refuses (exit 2) when the review says both, neither,
           or the round can't be found.
card       after a FIX on the last round, writes the decision card for the human (exit 10 = fill
           it in). There is no extra round.
card-ready exit 0 only when no <FILL ...> placeholder is left in the card.
install-check  exit 0 only when: the review is a PASS, it names the packet's full 64-hex digest,
           the go record approves that same digest, and the files on disk still match it.
           It never installs anything itself.

Exit codes: 0 ok · 2 unclear verdict/round · 3 not a PASS · 4 go record missing or wrong ·
            7 packet changed since review · 10 decision card written, fill it in · 11 card not ready
"""
import argparse, json, os, re, sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "review-packet", "scripts"))  # the sibling skill
import packet  # noqa: E402

VERDICT = re.compile(r"(?<![A-Za-z])(PASS|FIX)(?![A-Za-z])")


def classify_text(text, name="", forced_round=None):
    """Return (verdict, round) or raise ValueError with the reason."""
    head = "\n".join(text.strip().splitlines()[:6])          # the verdict must be stated up top
    found = set(VERDICT.findall(head))
    if len(found) != 1:
        raise ValueError("the first lines of the review must say exactly one of PASS or FIX "
                         f"(found: {', '.join(sorted(found)) or 'neither'})")
    rnd = forced_round
    if rnd is None:
        m = re.search(r"(?:-r|round[ _-]?)(\d+)\b", name, re.I) or re.search(r"\bround\s+(\d+)\b", head, re.I)
        if not m:
            raise ValueError("can't tell the round: name the file ...-r<N>.md or say 'round N' in the title")
        rnd = int(m.group(1))
    return found.pop(), rnd


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


CARD = """# DECISION NEEDED ({item}): <FILL the question, in plain words>

The reviewer said FIX on round {rnd} of {max_rounds}, the last round. There is no round {next_round}:
this card goes to the human instead.

**Why it matters:** <FILL what is blocked, or what it costs>

**What is still open (from the review):**
<FILL one line per open finding, in plain words>

**A)** <FILL option>: <FILL what happens>
**B)** <FILL option>: <FILL what happens>

**My pick:** <FILL A or B>, because <FILL one reason>

**If no answer by** <FILL day and time>: <FILL what you will do, which must be the safe default>

Review: {review}
"""


def cmd_classify(a):
    try:
        v, r = classify_text(read(a.review), os.path.basename(a.review), a.round)
    except ValueError as e:
        print(f"unclear: {e}", file=sys.stderr); return 2
    print(f"{v} round {r}")
    return 0


def cmd_card(a):
    try:
        v, r = classify_text(read(a.review), os.path.basename(a.review), a.round)
    except ValueError as e:
        print(f"unclear: {e}", file=sys.stderr); return 2
    if v != "FIX":
        print("the review is a PASS: no decision card needed", file=sys.stderr); return 3
    if r < a.max_rounds:
        print(f"FIX on round {r} of {a.max_rounds}: fix the findings and send round {r + 1}", file=sys.stderr)
        return 0
    if os.path.exists(a.out):
        print(f"{a.out} exists; not overwriting", file=sys.stderr); return 2
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(CARD.format(item=a.item, rnd=r, max_rounds=a.max_rounds, next_round=r + 1, review=a.review))
    print(f"FIX on the last round. Decision card written: {a.out}. Fill every <FILL ...>, then send it to the human.")
    return 10


def cmd_card_ready(a):
    left = [l.strip() for l in read(a.card).splitlines() if "<fill" in l.lower()]
    if left:
        print("not ready, still to fill:\n  - " + "\n  - ".join(left), file=sys.stderr); return 11
    print("ready")
    return 0


def cmd_install_check(a):
    text = read(a.review)
    try:
        v, r = classify_text(text, os.path.basename(a.review))
    except ValueError as e:
        print(f"unclear: {e}", file=sys.stderr); return 2
    if v != "PASS":
        print(f"the review is {v}, not PASS: nothing may be installed", file=sys.stderr); return 3
    digest, problems = packet.check(a.packet)
    if problems:
        print("packet does not match its manifest:\n  - " + "\n  - ".join(problems), file=sys.stderr); return 7
    if digest not in text.lower():
        print(f"the review does not name this packet's full digest ({digest}); a PASS on other bytes "
              "is not a PASS on these", file=sys.stderr)
        return 7
    try:
        go = json.loads(read(a.go))
    except (OSError, ValueError) as e:
        print(f"go record unreadable: {e}", file=sys.stderr); return 4
    if not isinstance(go, dict) or go.get("decision") != "GO" or str(go.get("digest", "")).lower() != digest:
        print("go record must be a JSON object with \"decision\": \"GO\" and this packet's digest", file=sys.stderr)
        return 4
    print(f"ok to install: PASS round {r}, digest {digest}, go by {go.get('by', '?')}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify"); c.add_argument("review"); c.add_argument("--round", type=int)
    k = sub.add_parser("card")
    k.add_argument("--review", required=True); k.add_argument("--item", required=True)
    k.add_argument("--out", required=True); k.add_argument("--round", type=int)
    k.add_argument("--max-rounds", type=int, default=3)
    cr = sub.add_parser("card-ready"); cr.add_argument("card")
    i = sub.add_parser("install-check")
    i.add_argument("--review", required=True); i.add_argument("--packet", required=True); i.add_argument("--go", required=True)
    a = ap.parse_args(argv)
    return {"classify": cmd_classify, "card": cmd_card, "card-ready": cmd_card_ready,
            "install-check": cmd_install_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

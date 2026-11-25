#!/usr/bin/env python3
"""Build and verify a review packet: a folder of files plus a SHA256SUMS manifest.

A packet is what a builder hands to a reviewer (another model, a teammate). The reviewer
reads the files, names the packet's digest in its verdict, and nothing is installed unless
the files on disk still hash to that digest. Standard library only.

    packet.py build  --out DIR --round N [--max-rounds 3] [--update] README.md file1 src:dest ...
    packet.py verify DIR [--digest HEX]
    packet.py digest DIR

Exit codes: 0 ok · 2 bad usage · 5 round above the limit · 6 README lint failed ·
            7 packet does not match (changed, missing or extra files) · 9 output exists
"""
import argparse, hashlib, os, re, shutil, sys, time

SUMS = "SHA256SUMS"
REQUIRED = ("Bottom line", "Not checked", "Undo")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def headings(text):
    return [m.group(1).strip().lower() for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.M)]


def lint_readme(text, rnd, max_rounds, report_only=False):
    """Return a list of problems with the packet README (empty = fine)."""
    hs = headings(text)
    need = [r for r in REQUIRED if not (report_only and r == "Undo")]
    problems = [f"missing a '## {r}' section" for r in need if not any(h.startswith(r.lower()) for h in hs)]
    if rnd >= 2 and not any(h.startswith(f"round {rnd}") for h in hs):
        problems.append(f"round {rnd} needs a '## Round {rnd}' section saying what changed since the last review")
    if rnd == max_rounds and not any(h.startswith("residual") for h in hs):
        problems.append(f"round {rnd} is the last round: add a '## Residuals' section (what you will hand to the human if this is not a PASS)")
    if "<fill" in text.lower():
        problems.append("README still contains <FILL ...> placeholders")
    return problems


def write_sums(folder):
    names = sorted(n for n in os.listdir(folder) if n != SUMS)
    lines = []
    for n in names:
        p = os.path.join(folder, n)
        if os.path.islink(p) or not os.path.isfile(p):
            raise SystemExit(f"refusing {n}: packets hold plain files only (no folders, no links)")
        lines.append(f"{sha256_file(p)}  {n}\n")
    with open(os.path.join(folder, SUMS), "w", encoding="utf-8") as f:
        f.writelines(lines)
    return sha256_file(os.path.join(folder, SUMS))


def check(folder):
    """Return (digest, problems). The digest is the SHA-256 of the SHA256SUMS file itself."""
    sums = os.path.join(folder, SUMS)
    if not os.path.isfile(sums):
        return None, [f"no {SUMS} in {folder}"]
    listed, problems = {}, []
    with open(sums, encoding="utf-8") as f:
        for line in f:
            m = re.fullmatch(r"([0-9a-f]{64})  ([^/\\\n]+)\n?", line)
            if not m:
                problems.append(f"bad line in {SUMS}: {line.rstrip()!r}")
                continue
            listed[m.group(2)] = m.group(1)
    on_disk = {n for n in os.listdir(folder) if n != SUMS}
    for n in sorted(on_disk - listed.keys()):
        problems.append(f"extra file not in {SUMS}: {n}")
    for n, want in sorted(listed.items()):
        p = os.path.join(folder, n)
        if n not in on_disk:
            problems.append(f"missing: {n}")
        elif os.path.islink(p) or not os.path.isfile(p):
            problems.append(f"not a plain file: {n}")
        elif sha256_file(p) != want:
            problems.append(f"changed since the manifest was written: {n}")
    return sha256_file(sums), problems


def cmd_build(a):
    if a.round < 1:
        print("--round starts at 1", file=sys.stderr); return 2
    if a.round > a.max_rounds:
        print(f"round {a.round} is above the limit of {a.max_rounds}. Do not open another round: "
              f"write the decision card for the human instead (verdict.py card).", file=sys.stderr)
        return 5
    pairs = []
    for spec in a.files:
        src, _, dest = spec.partition(":") if ":" in spec and not os.path.exists(spec) else (spec, "", "")
        dest = dest or os.path.basename(src)
        if "/" in dest or "\\" in dest or dest in ("", ".", "..", SUMS):
            print(f"bad destination name: {dest!r}", file=sys.stderr); return 2
        if not os.path.isfile(src):
            print(f"not a file: {src}", file=sys.stderr); return 2
        pairs.append((src, dest))
    dests = [d for _, d in pairs]
    if len(set(dests)) != len(dests):
        print("two files map to the same name in the packet", file=sys.stderr); return 2
    readme = [s for s, d in pairs if d == "README.md"]
    if not readme:
        print("a packet needs a README.md (pass it as README.md or src:README.md)", file=sys.stderr); return 6
    with open(readme[0], encoding="utf-8") as f:
        problems = lint_readme(f.read(), a.round, a.max_rounds, a.report_only)
    if problems:
        print("README lint failed, nothing written:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 6
    if os.path.exists(a.out):
        if not a.update:
            print(f"{a.out} exists; pass --update to publish a new revision (the old one is kept)", file=sys.stderr)
            return 9
        keep = f"{a.out.rstrip('/')}.prev-{time.strftime('%Y%m%d-%H%M%S')}"
        os.rename(a.out, keep)
        print(f"previous revision kept at {keep}")
    tmp = a.out.rstrip("/") + ".tmp-build"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    for src, dest in pairs:
        shutil.copyfile(src, os.path.join(tmp, dest))
    digest = write_sums(tmp)
    os.rename(tmp, a.out)
    print(f"packet: {a.out}\nfiles: {len(pairs)}\ndigest (sha256 of {SUMS}): {digest}")
    return 0


def cmd_verify(a):
    digest, problems = check(a.dir)
    if a.digest and digest and digest != a.digest.lower():
        problems.append(f"digest is {digest}, expected {a.digest.lower()}")
    if problems:
        print("packet does NOT match:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 7
    print(f"ok: {a.dir} matches its {SUMS} (digest {digest})")
    return 0


def cmd_digest(a):
    digest, problems = check(a.dir)
    if problems:
        print("\n".join(problems), file=sys.stderr); return 7
    print(digest)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", required=True)
    b.add_argument("--round", type=int, required=True)
    b.add_argument("--max-rounds", type=int, default=3)
    b.add_argument("--update", action="store_true")
    b.add_argument("--report-only", action="store_true", help="a report with no live change: no Undo section needed")
    b.add_argument("files", nargs="+")
    v = sub.add_parser("verify"); v.add_argument("dir"); v.add_argument("--digest")
    d = sub.add_parser("digest"); d.add_argument("dir")
    a = ap.parse_args(argv)
    return {"build": cmd_build, "verify": cmd_verify, "digest": cmd_digest}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

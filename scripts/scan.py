#!/usr/bin/env python3
"""Scan a folder for things that must not be published: emails, phone numbers, IP addresses,
private paths, hostnames, key-shaped strings, and any words in your own deny-list.

    python3 scripts/scan.py [ROOT] [--deny FILE] [--exclude FILE ...]

--deny FILE: one word or phrase per line (case-insensitive; '#' starts a comment). Keep that file
OUTSIDE the repo: it lists exactly the names you don't want published.
Exit 0 = clean, 1 = findings (each printed as path:line: kind: the match, masked).
"""
import argparse, os, re, sys

SKIP_DIRS = {".git", "__pycache__", "node_modules"}
ALLOW_EMAIL = re.compile(r"@(example\.(com|org|net)|users\.noreply\.github\.com)$", re.I)
ALLOW_IP = {"127.0.0.1", "0.0.0.0"}
PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("phone", re.compile(r"(?<![\w.])(?:\+?1[ .-]?)?\(?[2-9]\d{2}\)?[ .-]\d{3}[ .-]\d{4}(?!\w)")),
    ("ipv4", re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")),
    ("home path", re.compile(r"(?:/home/|/Users/|[A-Za-z]:\\Users\\)(?!<|\{|you\b|me\b|USER\b|\$)[A-Za-z0-9._-]+", re.I)),
    ("private host", re.compile(r"[A-Za-z0-9-]+\.(?:ts\.net|local|internal|lan)\b", re.I)),
    ("artifact/share link", re.compile(r"claude\.ai/(?:artifact|code/artifact|share|chat)/[A-Za-z0-9-]+", re.I)),
    ("key-shaped", re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}"
                              r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")),
    ("secret path", re.compile(r"~/\.secrets\b|_secrets[\\/]", re.I)),
]


def mask(s):
    return s if len(s) <= 6 else s[:3] + "…" + s[-2:]


def load_deny(path):
    words = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            w = line.split("#", 1)[0].strip()
            if w:
                words.append(w.lower())
    return compile_deny(words)


def compile_deny(words):
    """Whole-word matching, so 'cope' does not fire inside 'scopes'."""
    return [(w, re.compile(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])")) for w in words]


def scan_text(text, deny=()):
    """Yield (line_no, kind, match) for each finding."""
    low_lines = text.lower().splitlines()
    for i, line in enumerate(text.splitlines(), 1):
        for kind, rx in PATTERNS:
            for m in rx.finditer(line):
                hit = m.group(0)
                if kind == "email" and ALLOW_EMAIL.search(hit):
                    continue
                if kind == "ipv4":
                    parts = hit.split(".")
                    if hit in ALLOW_IP or any(int(p) > 255 for p in parts):
                        continue
                yield i, kind, hit
        for w, rx in deny:
            if rx.search(low_lines[i - 1]):
                yield i, "deny-list", w


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--deny")
    ap.add_argument("--exclude", action="append", default=[], help="a file to skip (test fixtures); listed in the output")
    a = ap.parse_args(argv)
    skip = {os.path.abspath(x) for x in a.exclude}
    for x in sorted(skip):
        print(f"excluded on purpose: {os.path.relpath(x, a.root)}", file=sys.stderr)
    deny = load_deny(a.deny) if a.deny else []
    if not os.path.exists(a.root):
        print(f"no such file or folder: {a.root}", file=sys.stderr)
        return 2
    if os.path.isfile(a.root):                    # os.walk on a file yields nothing: scan it directly
        base = os.path.dirname(os.path.abspath(a.root))
        walk = [(base, [], [os.path.basename(a.root)])]
        a.root = base
    else:
        walk = os.walk(a.root)
    found = 0
    for dirpath, dirnames, filenames in walk:
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            if os.path.abspath(p) in skip or (a.deny and os.path.abspath(p) == os.path.abspath(a.deny)):
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    text = f.read()
            except (UnicodeDecodeError, OSError):
                with open(p, "rb") as f:          # binary: still check the deny-list and key shapes
                    text = f.read().decode("latin-1")
            for line_no, kind, hit in scan_text(text, deny):
                found += 1
                print(f"{os.path.relpath(p, a.root)}:{line_no}: {kind}: {mask(hit)}")
    print(f"{found} finding(s)", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

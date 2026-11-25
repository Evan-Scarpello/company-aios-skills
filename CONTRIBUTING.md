# Contributing

Issues and pull requests are welcome. A few rules keep this repo useful.

1. **Only work you have the right to share.** Write it yourself, or bring something whose license allows it and say where it came from in `PROVENANCE.md`.
2. **No personal or company data.** No names of real customers, no emails, phone numbers, IP addresses, hostnames, account IDs or private paths. Use placeholders and `config.example.json`. Run `scripts/scan.sh` before you open a PR.
3. **A new skill needs a reason.** Say in the PR which repeated failure it fixes (two separate sessions is the bar). One-off procedures don't belong here.
4. **Keep `SKILL.md` short and testable.** A description that says when to use it, a procedure, rules, common mistakes. Scripts are Python standard library only, with tests in `tests/`.
5. **Run the tests:** `python3 -m unittest discover -s tests`.
6. **No growth hacks.** Please don't trade stars or use bots. We'd rather have ten people who use this than a thousand who don't.

#!/usr/bin/env python3
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import scan  # noqa: E402

def kinds(text, deny=()):
    return sorted({k for _, k, _ in scan.scan_text(text, deny)})

class ScanTests(unittest.TestCase):
    def test_finds_each_kind(self):
        self.assertEqual(kinds("mail jane.doe@acme-plumbing.com"), ["email"])
        self.assertEqual(kinds("call (201) 555-0142 now"), ["phone"])
        self.assertEqual(kinds("server 203.0.113.7"), ["ipv4"])
        self.assertEqual(kinds("see /home/jdoe/work"), ["home path"])
        self.assertEqual(kinds(r"see C:\Users\jdoe\x"), ["home path"])
        self.assertEqual(kinds("open box-1.tail1234.ts.net"), ["private host"])
        self.assertEqual(kinds("https://claude.ai/artifact/AbC123"), ["artifact/share link"])
        self.assertEqual(kinds("key ghp_" + "a" * 30), ["key-shaped"])
        self.assertEqual(kinds("cat ~/.secrets/x"), ["secret path"])

    def test_allows_placeholders(self):
        for ok in ("sam@example.com", "127.0.0.1", "/home/<you>/x", "~/.claude/skills", "version 1.2.3.4567",
                   "sha 0123456789abcdef", "/home/$USER/x", "999.1.1.1"):
            self.assertEqual(kinds(ok), [], ok)

    def test_deny_list_is_case_insensitive(self):
        deny = scan.compile_deny(["acme plumbing", "cope"])
        self.assertEqual(kinds("Built for ACME Plumbing", deny), ["deny-list"])
        self.assertEqual(kinds("token scopes", deny), [], "whole words only")

    def test_single_file_and_missing_path_are_not_silently_clean(self):
        import io, tempfile, contextlib
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "notes.txt")
            with open(f, "w") as fh:
                fh.write("mail jane.doe@acme-plumbing.com\n")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(scan.main([f]), 1, "a file path must be scanned, not walked")
            self.assertIn("email", out.getvalue())
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(scan.main([os.path.join(d, "missing")]), 2, "a missing path is an error, not 0 findings")

if __name__ == "__main__":
    unittest.main()

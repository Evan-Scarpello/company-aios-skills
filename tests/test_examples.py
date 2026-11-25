#!/usr/bin/env python3
"""Public-content guards: examples must be synthetic, and the README must not carry dated internal metrics."""
import glob, os, re, unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()

class ExampleTests(unittest.TestCase):
    def test_every_example_brief_is_marked_synthetic(self):
        briefs = glob.glob(os.path.join(ROOT, "examples", "*.md"))
        self.assertTrue(briefs, "expected at least one example brief")
        for path in briefs:
            with open(path, encoding="utf-8") as f:
                head = f.read(600)
            self.assertIn("synthetic example", head.lower(), os.path.basename(path))
            self.assertNotIn("real brief", head.lower(), os.path.basename(path))

    def test_readme_does_not_present_examples_as_real(self):
        self.assertNotRegex(read("README.md").lower(), r"\breal (coo )?brief\b")

    def test_readme_has_no_dated_internal_counts(self):
        text = read("README.md")
        self.assertNotRegex(text, r"\d{2,}\+\s+(handoff|review)", "internal operational counts")
        self.assertNotRegex(text, r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w* \d{1,2} to ", "dated range")

if __name__ == "__main__":
    unittest.main()

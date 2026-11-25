#!/usr/bin/env python3
"""Tests for scripts/packet.py and scripts/verdict.py.   python3 -m unittest discover -s tests"""
import io, json, os, shutil, sys, tempfile, unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "review-packet", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "review-verdict", "scripts"))
import packet, verdict  # noqa: E402

README_R1 = "# Packet\n\n## Bottom line\nIt works.\n\n## Not checked\nLive.\n\n## Undo\nrm it\n"


def run(fn, argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = fn(argv)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="aios-test-")
        self.addCleanup(shutil.rmtree, self.d, True)

    def file(self, name, text):
        p = os.path.join(self.d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def build(self, readme=README_R1, rnd=1, extra=(), out="pkt", more=()):
        r = self.file("README.src.md", readme)
        a = self.file("a.py", "print('a')\n")
        return run(packet.main, ["build", "--out", os.path.join(self.d, out), "--round", str(rnd), *more,
                                 f"{r}:README.md", a, *extra])


class PacketTests(Base):
    def test_build_then_verify(self):
        code, out, _ = self.build()
        self.assertEqual(code, 0, out)
        p = os.path.join(self.d, "pkt")
        self.assertEqual(sorted(os.listdir(p)), ["README.md", "SHA256SUMS", "a.py"])
        code, _, err = run(packet.main, ["verify", p])
        self.assertEqual(code, 0, err)

    def test_sums_file_is_sha256sum_compatible(self):
        self.build()
        with open(os.path.join(self.d, "pkt", "SHA256SUMS")) as f:
            lines = f.read().splitlines()
        self.assertEqual(len(lines), 2)
        for l in lines:
            h, name = l.split("  ")
            self.assertEqual(len(h), 64)
            self.assertEqual(packet.sha256_file(os.path.join(self.d, "pkt", name)), h)

    def test_changed_extra_and_missing_files_fail_verify(self):
        self.build()
        p = os.path.join(self.d, "pkt")
        with open(os.path.join(p, "a.py"), "a") as f:
            f.write("# tampered\n")
        self.assertEqual(run(packet.main, ["verify", p])[0], 7)
        self.build(out="pkt2")
        p2 = os.path.join(self.d, "pkt2")
        open(os.path.join(p2, "new.txt"), "w").close()
        self.assertEqual(run(packet.main, ["verify", p2])[0], 7)
        self.build(out="pkt3")
        p3 = os.path.join(self.d, "pkt3")
        os.remove(os.path.join(p3, "a.py"))
        self.assertEqual(run(packet.main, ["verify", p3])[0], 7)

    def test_wrong_expected_digest_fails(self):
        self.build()
        self.assertEqual(run(packet.main, ["verify", os.path.join(self.d, "pkt"), "--digest", "0" * 64])[0], 7)

    def test_round_above_limit_is_refused_and_writes_nothing(self):
        code, _, err = self.build(rnd=4)
        self.assertEqual(code, 5)
        self.assertIn("decision card", err)
        self.assertFalse(os.path.exists(os.path.join(self.d, "pkt")))

    def test_readme_lint(self):
        code, _, err = self.build(readme="# x\n## Bottom line\nok\n")
        self.assertEqual(code, 6)
        self.assertIn("Not checked", err)
        code, _, err = self.build(rnd=2)
        self.assertEqual(code, 6)
        self.assertIn("Round 2", err)
        code, _, err = self.build(rnd=3, readme=README_R1 + "\n## Round 3\nfixed\n")
        self.assertEqual(code, 6)
        self.assertIn("Residuals", err)
        code, _, _ = self.build(rnd=3, readme=README_R1 + "\n## Round 3\nfixed\n\n## Residuals\nnone\n")
        self.assertEqual(code, 0)
        code, _, err = self.build(out="p9", readme=README_R1 + "\n<FILL me>\n")
        self.assertEqual(code, 6)

    def test_report_only_needs_no_undo(self):
        code, _, _ = self.build(readme="## Bottom line\nx\n## Not checked\ny\n", more=["--report-only"])
        self.assertEqual(code, 0)

    def test_existing_output_needs_update_and_keeps_old(self):
        self.build()
        code, _, _ = self.build()
        self.assertEqual(code, 9)
        code, out, _ = self.build(more=["--update"])
        self.assertEqual(code, 0)
        self.assertTrue(any(n.startswith("pkt.prev-") for n in os.listdir(self.d)))

    def test_bad_destination_names_refused(self):
        for bad in ("../x", "SHA256SUMS", "a/b"):
            code, _, _ = self.build(extra=[f"{self.file('z.txt', 'z')}:{bad}"], out="p-" + str(abs(hash(bad))))
            self.assertEqual(code, 2, bad)


class VerdictTests(Base):
    def review(self, name, text):
        return self.file(name, text)

    def test_classify(self):
        r = self.review("ITEM-REVIEW-r2.md", "# Item review\n\n**FIX before install.**\n\nPASS on the tests though.\n")
        code, out, err = run(verdict.main, ["classify", r])
        self.assertEqual(code, 2, "PASS and FIX both near the top must be unclear")
        r = self.review("ITEM-REVIEW-r2.md", "# Item review\n\n**FIX before install.**\n\nDetails below.\n")
        code, out, _ = run(verdict.main, ["classify", r])
        self.assertEqual((code, out.strip()), (0, "FIX round 2"))

    def test_classify_needs_a_round(self):
        r = self.review("review.md", "# Review\n\nPASS\n")
        self.assertEqual(run(verdict.main, ["classify", r])[0], 2)
        self.assertEqual(run(verdict.main, ["classify", r, "--round", "1"])[1].strip(), "PASS round 1")

    def test_not_fooled_by_words_containing_pass(self):
        r = self.review("x-r1.md", "# Review\n\nPassword handling looks FIXed? no.\n\nFIX\n")
        self.assertEqual(run(verdict.main, ["classify", r])[1].strip(), "FIX round 1")

    def test_last_round_fix_writes_card_then_card_ready_gate(self):
        r = self.review("ITEM-REVIEW-r3.md", "# Item review round 3\n\nFIX\n")
        card = os.path.join(self.d, "DECISION-CARD.md")
        code, out, _ = run(verdict.main, ["card", "--review", r, "--item", "Item", "--out", card])
        self.assertEqual(code, 10)
        with open(card) as f:
            self.assertIn("There is no round 4", f.read())
        self.assertEqual(run(verdict.main, ["card-ready", card])[0], 11)
        with open(card, "w") as f:
            f.write("# DECISION NEEDED (Item): ship it?\nall filled\n")
        self.assertEqual(run(verdict.main, ["card-ready", card])[0], 0)

    def test_early_fix_means_next_round_not_card(self):
        r = self.review("ITEM-REVIEW-r1.md", "FIX\n")
        card = os.path.join(self.d, "c.md")
        code, _, err = run(verdict.main, ["card", "--review", r, "--item", "I", "--out", card])
        self.assertEqual(code, 0)
        self.assertIn("send round 2", err)
        self.assertFalse(os.path.exists(card))

    def _passed_packet(self, name_digest=True, go=None):
        self.build()
        p = os.path.join(self.d, "pkt")
        digest = run(packet.main, ["digest", p])[1].strip()
        r = self.review("I-REVIEW-r1.md", "# Review\n\nPASS\n\n" + (f"Digest {digest}\n" if name_digest else ""))
        g = self.file("go.json", json.dumps(go if go is not None else {"decision": "GO", "digest": digest, "by": "coo"}))
        return r, p, g, digest

    def test_install_check_happy_path(self):
        r, p, g, _ = self._passed_packet()
        code, out, err = run(verdict.main, ["install-check", "--review", r, "--packet", p, "--go", g])
        self.assertEqual(code, 0, err)

    def test_install_check_refusals(self):
        r, p, g, _ = self._passed_packet(name_digest=False)
        self.assertEqual(run(verdict.main, ["install-check", "--review", r, "--packet", p, "--go", g])[0], 7)
        shutil.rmtree(p)
        r, p, g, _ = self._passed_packet(go={"decision": "GO", "digest": "f" * 64})
        self.assertEqual(run(verdict.main, ["install-check", "--review", r, "--packet", p, "--go", g])[0], 4)
        shutil.rmtree(p)
        r, p, g, _ = self._passed_packet()
        with open(os.path.join(p, "a.py"), "a") as f:
            f.write("# changed after review\n")
        self.assertEqual(run(verdict.main, ["install-check", "--review", r, "--packet", p, "--go", g])[0], 7)
        fix = self.review("I-REVIEW-r2.md", "FIX\n")
        self.assertEqual(run(verdict.main, ["install-check", "--review", fix, "--packet", p, "--go", g])[0], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

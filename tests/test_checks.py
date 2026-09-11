"""Diagnostic-parser failure modes, separate from real CLI/MCP acceptance."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from librepcb_mcp.adapters.checks import interpret_check
from librepcb_mcp.adapters.cli import ProcessResult


class CheckInterpretationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project.lpp"

    def result(self, count=0, stderr="", *, exit_code=None, ending=None, extra="", outcome="completed"):
        stdout = (f"Open project '{self.project}'...\nRun ERC...\n  Approved messages: 2\n"
                  f"  Non-approved messages: {count}\n" + (ending if ending is not None else
                  ("Finished with errors!" if count else "SUCCESS")) + "\n" + extra)
        out, err = self.root / "stdout.txt", self.root / "stderr.txt"
        out.write_text(stdout, encoding="utf-8")
        err.write_text(stderr, encoding="utf-8")
        return ProcessResult(("test-fixture",), outcome, (1 if count else 0) if exit_code is None else exit_code,
                             0, str(out), str(err), stdout[:4000], stderr[:4000], len(stdout)>4000, len(stderr)>4000)

    def test_approved_findings_survive_a_pass(self):
        record = interpret_check(self.result(), "erc", self.project)
        self.assertEqual((record["outcome"], record["approved_count"], record["unapproved_count"]), ("passed", 2, 0))

    def test_rule_violation_is_a_completed_check(self):
        record = interpret_check(self.result(1, "    - [WARNING] Open wire\n"), "erc", self.project)
        self.assertEqual(record["outcome"], "violations")
        self.assertEqual(record["findings"], [{"severity":"warning", "message":"Open wire", "approved":False}])

    def test_unknown_or_fatal_stderr_cannot_be_clean(self):
        for stderr in ("FATAL ERROR: check computation failed\n", "unrecognized diagnostic\n"):
            with self.subTest(stderr=stderr):
                record = interpret_check(self.result(stderr=stderr), "erc", self.project)
                self.assertEqual(record["outcome"], "indeterminate")

    def test_missing_terminal_marker_cannot_be_clean(self):
        self.assertEqual(interpret_check(self.result(ending=""), "erc", self.project)["outcome"], "indeterminate")

    def test_exit_count_and_finding_mismatch_cannot_be_clean(self):
        for kwargs in ({"exit_code":1}, {"count":1}, {"count":1,"stderr":"    - [UNKNOWN] Message\n"},
                       {"extra":"unexpected stdout\n"}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(interpret_check(self.result(**kwargs), "erc", self.project)["outcome"], "indeterminate")

    def test_large_unicode_findings_remain_bounded_without_hiding_total(self):
        stderr = "".join("    - [WARNING] " + "\u96fb"*100 + f" {index}\n" for index in range(80))
        record = interpret_check(self.result(80, stderr), "erc", self.project)
        self.assertEqual((record["outcome"], record["unapproved_count"]), ("violations", 80))
        self.assertTrue(record["findings_truncated"])
        self.assertLess(len(json.dumps(record)), 8000)

    def test_capped_process_output_is_indeterminate(self):
        self.assertEqual(interpret_check(self.result(outcome="output_limit"), "erc", self.project)["outcome"], "indeterminate")

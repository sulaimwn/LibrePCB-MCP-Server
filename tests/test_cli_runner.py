"""Actual subprocess tests of the adapter, not LibrePCB integration tests."""

from pathlib import Path
import json
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from librepcb_mcp.adapters.cli import ProcessRunner


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def runner(self, **kwargs):
        return ProcessRunner(Path(sys.executable), self.root / "logs", **kwargs)

    def test_arguments_are_literal_and_nonzero_is_not_a_crash(self):
        value = 'path with spaces; $(echo unsafe) & "quoted"'
        result = self.runner().run(
            ["-c", "import json,sys; print(json.dumps(sys.argv[1])); sys.exit(1)", value],
            cwd=self.root,
        )
        self.assertEqual(result.outcome, "completed")
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(json.loads(result.stdout_excerpt), value)

    def test_diagnostics_bounded_but_raw_preserved_and_logs_do_not_collide(self):
        runner = self.runner()
        args = ["-c", "import sys; print('x'*10000); print('error', file=sys.stderr)"]
        first = runner.run(args, cwd=self.root)
        second = runner.run(args, cwd=self.root)
        self.assertEqual(len(first.stdout_excerpt), 4000)
        self.assertTrue(first.stdout_truncated)
        self.assertGreater(Path(first.stdout_path).stat().st_size, 10000)
        self.assertIn("error", first.stderr_excerpt)
        self.assertNotEqual(first.stdout_path, second.stdout_path)

    def test_timeout_kills_process_and_retains_partial_output(self):
        result = self.runner(timeout=1).run(
            ["-c", "import time; print('started', flush=True); time.sleep(60)"],
            cwd=self.root,
        )
        self.assertEqual(result.outcome, "timeout")
        self.assertIsNone(result.exit_code)
        self.assertIn("started", result.stdout_excerpt)
        self.assertLess(result.elapsed_seconds, 10)

    def test_missing_executable(self):
        result = ProcessRunner(self.root / "missing.exe", self.root).run([], cwd=self.root)
        self.assertEqual(result.outcome, "cli_missing")
        self.assertIsNone(result.exit_code)

    def test_large_diagnostics_are_capped_and_not_reported_as_completed(self):
        result = self.runner(max_log_bytes=4096).run(
            ["-c", "import sys; sys.stdout.write('x'*1000000); sys.stdout.flush()"], cwd=self.root)
        self.assertEqual(result.outcome, "output_limit")
        self.assertEqual(Path(result.stdout_path).stat().st_size, 4096)
        self.assertLessEqual(Path(result.stderr_path).stat().st_size, 4096)
        self.assertIn("incomplete", result.error)

    def test_launch_failure_is_not_a_missing_cli(self):
        result = self.runner().run([], cwd=self.root / "missing-directory")
        self.assertEqual(result.outcome, "process_failed")
        self.assertIsNone(result.exit_code)

    def test_invalid_timeouts_rejected(self):
        for timeout in (0, -1, 301, float("nan"), float("inf")):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                self.runner(timeout=timeout)


if __name__ == "__main__":
    unittest.main()

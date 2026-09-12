"""Fault injection and real subprocess reliability tests, not LibrePCB integration."""

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import threading
import time
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import anyio

from librepcb_mcp.adapters.cli import ProcessRunner, ProcessResult
from librepcb_mcp.adapters.files import capture, copy_capture
from librepcb_mcp.adapters.project import inspect_project
from librepcb_mcp.adapters.reports import write_json
from librepcb_mcp.errors import ProjectError
from librepcb_mcp.operations import checkpoint, operation_scope
from librepcb_mcp.service import ProjectService, Snapshot

ROOT = Path(__file__).resolve().parents[1]
R17 = "0f0fb70f-d2f9-4a08-83e2-47fae2ffc276"


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_budget_shared_by_sequential_subprocesses(self):
        runner = ProcessRunner(Path(sys.executable), self.root / 'logs', timeout=10)
        started = time.monotonic()
        with operation_scope(1.5):
            first = runner.run(['-c', "import time; time.sleep(.1); print('first')"], cwd=self.root)
            self.assertEqual(first.outcome, 'completed')
            second = runner.run(['-c', "import time; print('second', flush=True); time.sleep(60)"], cwd=self.root)
        self.assertEqual(second.outcome, 'operation_timeout')
        self.assertIn('second', Path(second.stdout_path).read_text())
        self.assertLess(time.monotonic() - started, 4)

    def test_anyio_cancellation_reaps_worker_process_before_returning(self):
        runner = ProcessRunner(Path(sys.executable), self.root / 'logs', timeout=10)
        records = []

        async def trial():
            cancelled = anyio.get_cancelled_exc_class()

            def cancel_check():
                try:
                    anyio.from_thread.check_cancelled()
                except cancelled as exc:
                    raise ProjectError('cancelled', 'test cancellation') from exc

            def worker():
                with operation_scope(10, cancel_check):
                    records.append(runner.run(['-c', "import time; print('started', flush=True); time.sleep(60)"], cwd=self.root))

            with anyio.move_on_after(.75):
                await anyio.to_thread.run_sync(worker)

        started = time.monotonic()
        anyio.run(trial)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].outcome, 'cancelled')
        self.assertIn('started', records[0].stdout_excerpt)
        self.assertLess(time.monotonic() - started, 4)

    def test_expired_budget_launches_no_process_and_resets_context(self):
        marker = self.root / 'executed.txt'
        with operation_scope(.01):
            time.sleep(.02)
            with self.assertRaises(ProjectError):
                ProcessRunner(Path(sys.executable), self.root / 'logs').run(
                    ['-c', "from pathlib import Path; import sys; Path(sys.argv[1]).write_text('bad')", str(marker)], cwd=self.root)
        self.assertFalse(marker.exists())
        self.assertFalse((self.root / 'logs').exists())
        checkpoint()  # completed request must not poison the next one

    def test_invalid_operation_limits(self):
        for value in (0, -1, 601, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                with operation_scope(value):
                    pass

    def test_log_storage_failure_terminates_the_running_process(self):
        original_open = Path.open

        class FailingLog:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.stream.close()

            def write(self, data):
                raise OSError(28, 'simulated log disk full')

        def open_log(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            return FailingLog(stream) if path.name.endswith('.stdout.txt') and args == ('xb',) else stream

        started = time.monotonic()
        with patch.object(Path, 'open', open_log):
            result = ProcessRunner(Path(sys.executable), self.root / 'logs', timeout=10).run(
                ['-c', "import time; print('output', flush=True); time.sleep(60)"], cwd=self.root)
        self.assertEqual(result.outcome, 'process_failed')
        self.assertLess(time.monotonic() - started, 4)


class ServiceReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix='lp-d5-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'p' / 'source'
        with ZipFile(ROOT / 'tests/fixtures/d0-reader.lppz') as archive:
            archive.extractall(self.source)
        self.original = capture(self.source)
        self.service = ProjectService(str(self.root / 'missing.exe'), [str(self.root / 'p')], str(self.root / 'd'), experimental_edits=True)
        copy = self.service.session_dir / 'p01'
        copy_capture(self.original, copy)
        snapshot = Snapshot('source', self.source / 'd0-reader.lpp', copy, self.original.revision,
                            datetime.now(timezone.utc).isoformat(), inspect_project(self.original, 'd0-reader.lpp'))
        self.service.snapshots['source'] = snapshot
        self.arguments = dict(project_id='source', component_id=R17, new_value='2.2', expected_revision=self.original.revision)
        # Fake CLI is deliberate: inject otherwise hard-to-reproduce storage faults.
        # Actual LibrePCB fault/recovery and MCP acceptance are separate scripts.
        self.out, self.err = self.root / 'stdout.txt', self.root / 'stderr.txt'
        self.out.write_text('SUCCESS\n')
        self.err.write_text('')
        self.result = ProcessResult(('fake-cli',), 'completed', 0, 0, str(self.out), str(self.err), 'SUCCESS\n', '', False, False)

    def simulated_edit(self):
        checks = {'outcome': 'passed', 'checks': []}
        with patch.object(self.service, 'run_checks', return_value=checks), patch.object(self.service.runner, 'run', return_value=self.result):
            return self.service.dispatch('create_value_edit', **self.arguments)

    def assert_original_and_handles(self):
        self.assertEqual(capture(self.source), self.original)
        self.assertEqual(set(self.service.snapshots), {'source'})

    def test_success_report_failure_removes_candidate_handle_and_retry_works(self):
        def storage(path, record):
            if path.name == 'edit.json':
                raise OSError(28, 'simulated disk full')
            write_json(path, record)

        with patch('librepcb_mcp.service.write_json', side_effect=storage):
            failed = self.simulated_edit()
        self.assertFalse(failed['ok'])
        self.assertEqual(failed['error'], 'io_error')
        record = json.loads(Path(failed['details']['report_artifact']).read_text())
        self.assertEqual(record['outcome'], 'failed')
        self.assertNotIn('candidate', record)
        self.assert_original_and_handles()
        retained = capture(self.service.session_dir / 'e01' / 'c')
        self.assertTrue(self.simulated_edit()['ok'])
        self.assertEqual(capture(self.service.session_dir / 'e01' / 'c'), retained)

    def test_failure_report_cannot_hide_original_check_error(self):
        def storage(path, record):
            if path.name == 'failure.json':
                raise OSError(28, 'simulated disk full')
            write_json(path, record)

        with patch('librepcb_mcp.service.write_json', side_effect=storage), patch.object(
                self.service, 'run_checks', side_effect=ProjectError('check_failed', 'original failure')):
            result = self.service.dispatch('create_value_edit', **self.arguments)
        self.assertEqual(result['error'], 'check_failed')
        self.assertEqual(result['message'], 'original failure')
        self.assertIn('report_write_error', result['details'])
        self.assertNotIn('report_artifact', result['details'])
        self.assert_original_and_handles()

    def test_pending_report_failure_starts_no_native_operation(self):
        with patch('librepcb_mcp.service.write_json', side_effect=OSError(28, 'full')), patch.object(self.service, 'run_checks') as checks:
            failed = self.service.dispatch('create_value_edit', **self.arguments)
        checks.assert_not_called()
        self.assertEqual(failed['error'], 'io_error')
        self.assert_original_and_handles()

    def test_check_report_storage_error_preserves_process_failure(self):
        with patch.object(self.service, '_cli_version', return_value={}), patch.object(
                self.service.runner, 'run', return_value=replace(self.result, outcome='timeout', exit_code=None)), patch(
                'librepcb_mcp.service.write_json', side_effect=OSError(28, 'full')):
            failed = self.service.dispatch('run_checks', project_id='source', checks='erc')
        self.assertEqual(failed['error'], 'timeout')
        self.assertIn('report_write_error', failed['details'])
        self.assertIn('timeout', failed['details']['checks'][0]['diagnostic_notes'])

    def test_interrupted_save_retains_copy_and_no_handle(self):
        bad = replace(self.result, outcome='timeout', exit_code=None, error='injected timeout')
        with patch.object(self.service, 'run_checks', return_value={'outcome': 'passed'}), patch.object(self.service.runner, 'run', return_value=bad):
            failed = self.service.dispatch('create_value_edit', **self.arguments)
        self.assertEqual(failed['error'], 'timeout')
        record = json.loads(Path(failed['details']['report_artifact']).read_text())
        self.assertEqual(record['cli_roundtrip'][0]['process_outcome'], 'timeout')
        self.assertTrue((self.service.session_dir / 'e01' / 'b').is_dir())
        self.assert_original_and_handles()

    def test_unexpected_error_diagnostic_write_failure_is_bounded(self):
        with patch.object(self.service, 'get_project_summary', side_effect=RuntimeError('internal')), patch.object(Path, 'open', side_effect=OSError(28, 'full')):
            result = self.service.dispatch('get_project_summary', project_id='source')
        self.assertEqual(result['error'], 'internal_error')
        self.assertIn('diagnostic_write_error', result['details'])
        self.assertLess(len(json.dumps(result)), 1000)

    def test_queue_timeout_does_not_enter_operation(self):
        self.service.operation_timeout = .1
        ready, release = threading.Event(), threading.Event()

        def holder():
            with self.service.lock:
                ready.set()
                release.wait(3)

        thread = threading.Thread(target=holder)
        thread.start()
        self.assertTrue(ready.wait(2))
        try:
            failed = self.service.dispatch('create_value_edit', **self.arguments)
            self.assertEqual(failed['error'], 'operation_timeout')
            self.assertEqual(self.service.edit_attempts, 0)
        finally:
            release.set()
            thread.join(3)
        self.assert_original_and_handles()

    def test_cancelled_queue_does_not_enter_operation(self):
        def cancelled():
            raise ProjectError('cancelled', 'cancelled before work')

        failed = self.service.dispatch('create_value_edit', _cancel_check=cancelled, **self.arguments)
        self.assertEqual(failed['error'], 'cancelled')
        self.assertEqual(self.service.edit_attempts, 0)
        self.assert_original_and_handles()

    def test_check_capacity_is_reserved_before_candidate_save(self):
        self.service.operation_count = 63
        failed = self.simulated_edit()
        self.assertEqual(failed['error'], 'resource_limit')
        self.assertEqual(self.service.edit_attempts, 0)
        self.assert_original_and_handles()

    def test_exclusive_report_does_not_overwrite_owner_file(self):
        path = self.root / 'owner.json'
        path.write_bytes(b'owner data')
        with self.assertRaises(FileExistsError):
            write_json(path, {'overwrite': True})
        self.assertEqual(path.read_bytes(), b'owner data')


if __name__ == '__main__':
    unittest.main()

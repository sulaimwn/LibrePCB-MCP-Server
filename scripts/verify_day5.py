"""Real LibrePCB interruption/retry and real STDIO MCP cancellation/recovery.

Fault injection is confined to this developer harness: shorten one actual CLI
save invocation and reject one final report write. No product fault switches or
arbitrary execution tools are exposed.
"""

import asyncio
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch
from uuid import uuid4

from mcp import Client, StdioServerParameters, stdio_client
from librepcb_mcp.adapters.reports import write_json
from librepcb_mcp.service import ProjectService
from verify_baseline import extract_fixture, manifest

ROOT = Path(__file__).resolve().parents[1]
R17 = '0f0fb70f-d2f9-4a08-83e2-47fae2ffc276'


async def verify():
    run = ROOT / 'work' / ('d5-' + uuid4().hex[:6])
    source = run / 'p' / 'source'
    pin = json.loads((ROOT / 'toolchain.json').read_text())
    fixture = ROOT / 'tests/fixtures/d0-reader.lppz'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin['fixture']['sha256']
    extract_fixture(fixture, source)
    before = manifest(source)
    checks, calls, native, domain = [], [], [], []
    passed, failure = False, None
    cli = ROOT / pin['librepcb']['relative_executable']

    def expect(name, condition, detail=None):
        checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
        if not condition:
            raise AssertionError(name)

    async def call(client, name, arguments=None):
        result = await client.call_tool(name, arguments or {}, read_timeout_seconds=300)
        data = result.structured_content
        expect('wire_' + str(len(calls)), len(result.model_dump_json(by_alias=True).encode()) <= 64000)
        expect('error_flag_' + str(len(calls)), data is not None and result.is_error == (not data['ok']))
        calls.append({'tool': name, 'arguments': arguments or {}, 'structured_content': data})
        return data

    def real_cli_faults():
        service = ProjectService(str(cli), [str(run / 'p')], str(run / 'ds'), experimental_edits=True)
        real_run = service.runner.run
        interrupt_next_save = True

        def observed(args, *, cwd):
            nonlocal interrupt_next_save
            old_timeout = service.runner.timeout
            if '--save' in args and interrupt_next_save:
                interrupt_next_save = False
                service.runner.timeout = .01
            try:
                result = real_run(args, cwd=cwd)
                native.append(result.to_dict())
                return result
            finally:
                service.runner.timeout = old_timeout

        with patch.object(service.runner, 'run', side_effect=observed):
            opened = service.dispatch('open_project', path=str(source / 'd0-reader.lpp'))
            expect('real_domain_source_open', opened['ok'], opened)
            handle, revision = opened['data']['project_id'], opened['data']['revision']
            args = dict(project_id=handle, component_id=R17, new_value='2.2', expected_revision=revision)
            stopped = service.dispatch('create_value_edit', **args)
            domain.append(stopped)
            expect('actual_cli_save_invocation_timed_out', stopped.get('error') == 'timeout', stopped)
            expect('stopped_save_has_real_timeout_log', any('--save' in r['argv'] and r['outcome'] == 'timeout' for r in native))
            expect('stopped_candidate_not_registered', set(service.snapshots) == {handle})
            directory = Path(stopped['details']['operation_directory'])
            expect('started_and_failure_records_retained', (directory / 'started.json').is_file() and Path(stopped['details']['report_artifact']).is_file())
            partial = manifest(directory)
            expect('source_unchanged_after_interruption', manifest(source) == before)

            def fail_success_report(path, record):
                if path.name == 'edit.json':
                    raise OSError(28, 'Injected final report storage failure after real LibrePCB validation')
                write_json(path, record)

            with patch('librepcb_mcp.service.write_json', side_effect=fail_success_report):
                storage = service.dispatch('create_value_edit', **args)
            domain.append(storage)
            expect('real_validation_then_report_failure', storage.get('error') == 'io_error', storage)
            failure_record = json.loads(Path(storage['details']['report_artifact']).read_text())
            expect('failed_report_followed_real_passed_candidate_checks', failure_record['candidate_checks']['outcome'] == 'passed')
            expect('failed_storage_publishes_no_candidate_handle', set(service.snapshots) == {handle})
            storage_copy = Path(storage['details']['operation_directory'])
            stored_before = manifest(storage_copy)
            retry = service.dispatch('create_value_edit', **args)
            domain.append(retry)
            expect('retry_after_timeout_and_storage_failure', retry['ok'] and retry['data']['outcome'] == 'validated_candidate', retry)
            expect('retry_preserves_previous_partial_outputs', manifest(directory) == partial and manifest(storage_copy) == stored_before)
            expect('source_unchanged_after_real_recovery', manifest(source) == before)

    log = None
    tasks = []
    try:
        await asyncio.to_thread(real_cli_faults)
        params = StdioServerParameters(command=sys.executable, args=['-m', 'librepcb_mcp.server', '--cli', str(cli),
            '--project-root', str(run / 'p'), '--data-root', str(run / 'd'), '--enable-experimental-edits'],
            cwd=ROOT, env={'PYTHONUNBUFFERED': '1', 'PYTHONIOENCODING': 'utf-8'})
        log = (run / 'server-stderr.txt').open('w', encoding='utf-8')
        async with Client(stdio_client(params, errlog=log), mode='legacy', read_timeout_seconds=300) as client:
            opened = await call(client, 'open_project', {'path': str(source / 'd0-reader.lpp')})
            expect('real_mcp_source_open', opened['ok'])
            handle, revision = opened['data']['project_id'], opened['data']['revision']
            session = Path(opened['data']['snapshot_project']).parent.parent
            args = dict(project_id=handle, component_id=R17, new_value='2.2', expected_revision=revision)
            active = asyncio.create_task(client.call_tool('create_value_edit', args, read_timeout_seconds=300))
            tasks.append(active)
            # Cancel during the candidate workflow after baseline checks: the
            # control copy has begun, so this is an active request, not setup.
            expires = time.monotonic() + 60
            while not (session / 'e01' / 'b').exists():
                if active.done():
                    raise AssertionError('Edit finished before controlled cancellation point')
                if time.monotonic() >= expires:
                    raise AssertionError('Control copy did not begin')
                await asyncio.sleep(.03)
            queued = asyncio.create_task(client.call_tool('create_value_edit', args, read_timeout_seconds=300))
            tasks.append(queued)
            await asyncio.sleep(.12)
            cancelled_at = time.monotonic()
            queued.cancel()
            active.cancel()
            for task in tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            # SDK cancellation is sent over the real wire. A fresh tool call
            # must wait for worker cleanup and then see the same usable source.
            summary = await call(client, 'get_project_summary', {'project_id': handle})
            elapsed = time.monotonic() - cancelled_at
            expect('cancelled_worker_releases_writer_and_server_recovers', summary['ok'] and elapsed < 10, {'seconds': round(elapsed, 3)})
            expect('cancelled_queued_edit_never_started', sorted(p.name for p in session.glob('e*')) == ['e01'])
            cancelled_record = json.loads((session / 'e01' / 'failure.json').read_text())
            expect('active_cancellation_recorded', cancelled_record['outcome'] == 'failed' and cancelled_record['error'] == 'cancelled')
            expect('cancelled_source_preserved', manifest(source) == before)
            retained = manifest(session / 'e01')
            retry = await call(client, 'create_value_edit', args)
            expect('same_session_mcp_retry_validates', retry['ok'] and retry['data']['outcome'] == 'validated_candidate', retry)
            expect('retry_keeps_cancelled_artifacts', manifest(session / 'e01') == retained)
            candidate_handle = retry['data']['candidate']['project_id']
            inspected = await call(client, 'get_project_summary', {'project_id': candidate_handle})
            expect('retried_candidate_handle_usable', inspected['ok'] and inspected['data']['is_edit_candidate'])
            status = await call(client, 'get_status')
            expect('whole_operation_budget_visible', status['data']['limits']['operation_timeout_seconds'] == 240)
            expect('all_source_files_preserved', manifest(source) == before)
        # Subprocess/server ended; a second session does not resurrect handles.
        async with Client(stdio_client(params, errlog=log), mode='legacy', read_timeout_seconds=300) as client:
            stale = await call(client, 'get_project_summary', {'project_id': candidate_handle})
            expect('restart_rejects_old_candidate_handle', stale.get('error') == 'invalid_argument')
            reopened = await call(client, 'open_project', {'path': str(source / 'd0-reader.lpp')})
            expect('restart_opens_original', reopened['ok'] and reopened['data']['revision'] == revision)
        passed = True
    except Exception as exc:
        def describe(error):
            return [describe(child) for child in error.exceptions] if isinstance(error, BaseExceptionGroup) else f'{type(error).__name__}: {error}'
        failure = describe(exc)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        if log is not None:
            log.close()
        report = {'kind': 'day5_real_cli_and_mcp_reliability', 'package': version('librepcb-mcp-server'),
            'passed': passed and all(c['passed'] for c in checks), 'failure': failure, 'checks': checks, 'calls': calls,
            'domain_calls': domain, 'native_calls': native, 'source_preserved': manifest(source) == before,
            'note': 'Actual LibrePCB save invocation interrupted with a 10ms timeout, not proof of a particular internal save phase. Final report-write failure is injected after actual successful native validation. MCP cancellation is sent by the SDK; general process-tree/forced-parent-kill behavior is not established.'}
        content = json.dumps(report, indent=2).replace(json.dumps(str(ROOT))[1:-1], '<REPO>')
        (run / 'report.json').write_text(content + '\n', encoding='utf-8', newline='\n')
        print(json.dumps({'passed': report['passed'], 'checks': len(checks), 'calls': len(calls), 'native_calls': len(native),
                          'failure': failure, 'report': str(run / 'report.json')}, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(asyncio.run(verify()))

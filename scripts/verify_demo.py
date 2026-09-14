"""Verify generated client configuration and leave real sample outputs for review."""

import argparse
import asyncio
import base64
import hashlib
import json
from pathlib import Path
import shutil
import tomllib
from uuid import uuid4

from mcp import Client, StdioServerParameters, stdio_client


def manifest(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


async def verify(demo):
    demo = demo.resolve(strict=True)
    config = tomllib.loads((demo / 'codex-config.toml').read_text(encoding='utf-8'))['mcp_servers']['librepcb']
    claude = json.loads((demo / 'claude-desktop-config.json').read_text(encoding='utf-8'))['mcpServers']['librepcb']
    if any(config[key] != claude[key] for key in ('command', 'args')):
        raise ValueError('The generated client snippets disagree about the server command.')
    source = demo / 'p'
    before = manifest(source)
    review = demo / ('review-' + uuid4().hex[:6])
    review.mkdir()
    checks, calls = [], []
    completed, failure, candidate_path = False, None, None
    edited = '--enable-experimental-edits' in config['args']

    def expect(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    async def call(client, name, arguments=None, *, picture=None):
        result = await client.call_tool(name, arguments or {}, read_timeout_seconds=config['tool_timeout_sec'])
        data = result.structured_content
        expect(name + '_successful_bounded_result', not result.is_error and data is not None and data['ok']
               and len(result.model_dump_json(by_alias=True).encode()) <= (1_500_000 if picture else 64_000))
        images = [item for item in result.content if item.type == 'image']
        saved = []
        if picture:
            expect(name + '_native_image', len(images) == 1 and images[0].mime_type == 'image/png')
            raw = base64.b64decode(images[0].data, validate=True)
            digest = hashlib.sha256(raw).hexdigest()
            expect(name + '_png_matches_artifact', raw.startswith(b'\x89PNG\r\n\x1a\n') and digest in {a['sha256'] for a in data['data']['artifacts']})
            (review / picture).write_bytes(raw)
            saved = [{'file': picture, 'bytes': len(raw), 'sha256': digest}]
        calls.append({'tool': name, 'arguments': arguments or {}, 'data': data, 'images': saved})
        return data['data']

    async def items(client, name, handle):
        result, cursor = [], None
        while True:
            page = await call(client, name, {'project_id': handle, 'cursor': cursor, 'limit': 100})
            result.extend(page['items'])
            cursor = page['next_cursor']
            if cursor is None:
                return result

    log = (review / 'server-stderr.txt').open('w', encoding='utf-8')
    try:
        # Literal generated argv, launched away from the checkout root.
        params = StdioServerParameters(command=config['command'], args=config['args'], cwd=review,
                                       env={'PYTHONIOENCODING': 'utf-8', 'PYTHONUNBUFFERED': '1'})
        async with Client(stdio_client(params, errlog=log), mode='legacy', read_timeout_seconds=config['tool_timeout_sec']) as client:
            tools = await client.list_tools()
            expect('configured_tool_count', len(tools.tools) == (9 if edited else 8))
            status = await call(client, 'get_status')
            expect('pinned_cli_ready', status['ready'] and status['librepcb']['version'] == '2.1.1')
            opened = await call(client, 'open_project', {'path': str(source / 'd0-reader.lpp')})
            handle = opened['project_id']
            summary = await call(client, 'get_project_summary', {'project_id': handle})
            expect('sample_summary', summary['component_count'] == 97 and summary['net_count'] == 48
                   and len(summary['boards']) == 1 and len(summary['schematics']) == 2)
            components = await items(client, 'list_components', handle)
            nets = await items(client, 'list_nets', handle)
            expect('all_sample_records', len(components) == 97 and len(nets) == 48)
            resistor = next(c for c in components if c['reference'] == 'R17')
            expect('original_resistance', resistor['attributes'] == [{'key': 'RESISTANCE', 'type': 'resistance', 'unit': 'kiloohm', 'value': '1.5'}])
            rules = await call(client, 'run_checks', {'project_id': handle})
            expect('baseline_findings_preserved', rules['outcome'] == 'passed' and rules['approved_count'] == 18 and rules['unapproved_count'] == 0)
            ethernet = next(s['id'] for s in summary['schematics'] if s['name'] == 'Ethernet')
            await call(client, 'export_preview', {'project_id': handle, 'schematic_id': ethernet}, picture='original-ethernet.png')
            pdf = await call(client, 'run_output_job', {'project_id': handle, 'job_name': 'schematic_pdf'})
            expect('pdf_export', len(pdf['artifacts']) == 1)
            shutil.copyfile(pdf['artifacts'][0]['path'], review / 'original-schematic.pdf')
            manufacturing = await call(client, 'run_output_job', {'project_id': handle, 'job_name': 'gerber_excellon'})
            expect('manufacturing_exports', len(manufacturing['artifacts']) == 11)
            if edited:
                candidate = await call(client, 'create_value_edit', {'project_id': handle, 'component_id': resistor['id'],
                    'expected_revision': opened['revision'], 'new_value': '2.2'})
                expect('candidate_validated', candidate['outcome'] == 'validated_candidate'
                       and candidate['invariants']['exact_expected_files'] and candidate['candidate_checks']['outcome'] == 'passed')
                candidate_path = candidate['candidate']['snapshot_project']
                await call(client, 'export_preview', {'project_id': candidate['candidate']['project_id'], 'schematic_id': ethernet}, picture='candidate-ethernet.png')
            expect('all_source_files_unchanged', manifest(source) == before)
            completed = True
    except Exception as exc:
        def describe(error):
            return [describe(child) for child in error.exceptions] if isinstance(error, BaseExceptionGroup) else f'{type(error).__name__}: {error}'
        failure = describe(exc)
    finally:
        log.close()
        record = {'passed': completed and all(c['passed'] for c in checks), 'failure': failure,
            'checks': checks, 'calls': calls, 'source_preserved': manifest(source) == before,
            'source_project': str(source / 'd0-reader.lpp'), 'candidate_project': candidate_path,
            'review_directory': str(review), 'configuration': str(demo / 'codex-config.toml'), 'experimental_edits': edited,
            'note': 'Real SDK/CLI workflow using generated config. Owner review and persistent UI connection are separate.'}
        (review / 'report.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
        if record['passed']:
            lines = ['# LibrePCB sample review', '', 'The sample workflow passed through the generated MCP configuration.', '',
                     '97 components, 48 nets, one board, two schematic sheets. Checks retain',
                     '2 approved ERC and 16 approved DRC findings; zero unapproved findings.', '',
                     '[Original schematic PDF](original-schematic.pdf)', '', '![Original Ethernet sheet](original-ethernet.png)', '']
            if edited:
                lines += ['R17 changed from 1.5 to 2.2 kiloohms in a separate validated candidate.', '',
                          '![Candidate Ethernet sheet](candidate-ethernet.png)', '', f'Candidate project: `{candidate_path}`', '']
            lines += ['The original remains unchanged. These are real LibrePCB outputs, not a',
                      'manufacturing approval. Review them before accepting this experiment.', '',
                      f'Original project: `{source / "d0-reader.lpp"}`', '',
                      'Generated configuration and sample prompt are in the parent folder.',
                      'They have not been installed into a client. See docs/OWNER_TRIAL.md in the repository.', '',
                      '[Full verification report](report.json)', '']
            (review / 'REVIEW.md').write_text('\n'.join(lines), encoding='utf-8')
        print(json.dumps({'passed': record['passed'], 'checks': len(checks), 'calls': len(calls),
                          'review_directory': str(review), 'failure': failure}, indent=2))
    return 0 if record['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', type=Path, required=True, help='Directory created by prepare_demo.py')
    raise SystemExit(asyncio.run(verify(parser.parse_args().demo)))

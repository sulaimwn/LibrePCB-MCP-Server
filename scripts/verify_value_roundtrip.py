import hashlib
import json
from pathlib import Path
import sys
from uuid import uuid4

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from verify_baseline import extract_fixture
from librepcb_mcp.adapters.files import capture, copy_capture
from librepcb_mcp.adapters.edits import resistance_edit, verify_edit, CIRCUIT_FILE
from librepcb_mcp.adapters.project import inspect_project
from librepcb_mcp.adapters.cli import ProcessRunner

run = root / 'work' / ('d4p-' + uuid4().hex[:5])
run.mkdir(parents=True)
pin = json.loads((root / 'toolchain.json').read_text())
fixture = root / 'tests/fixtures/d0-reader.lppz'
assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin['fixture']['sha256']
source, candidate = run / 'p' / 'source', run / 'p' / 'candidate'
extract_fixture(fixture, source)
original = capture(source)
runner = ProcessRunner(root / pin['librepcb']['relative_executable'], run / 'logs', timeout=30)
control = run / 'control'
copy_capture(original, control)
saved = runner.run(['open-project', '--save', str(control / 'd0-reader.lpp')], cwd=run)
assert saved.outcome == 'completed' and saved.exit_code == 0, saved.to_dict()
before = capture(control)
assert all(before.files[name] == content for name, content in original.files.items())
generated = set(before.files) - set(original.files)
assert generated == {'project/settings.user.lp', 'boards/default/settings.user.lp',
                     'schematics/main/settings.user.lp', 'schematics/ethernet/settings.user.lp'}
data = inspect_project(before, 'd0-reader.lpp')
resistor = next(c for c in data.components if c['reference'] == 'R17')
edit = resistance_edit(before, 'd0-reader.lpp', resistor['id'], '2.2')
copy_capture(before, candidate)
(candidate / CIRCUIT_FILE).write_bytes(edit.content)
verify_edit(before, capture(candidate), edit)
records = [saved.to_dict()]
for options in (['--strict'], ['--save'], ['--strict']):
    result = runner.run(['open-project', *options, str(candidate / 'd0-reader.lpp')], cwd=run)
    records.append(result.to_dict())
    assert result.outcome == 'completed' and result.exit_code == 0, result.to_dict()
    verify_edit(before, capture(candidate), edit)
assert capture(source) == original
record = {'passed': True, 'run': str(run), 'change': edit.change, 'cli': records,
          'source_preserved': True, 'exact_edit_after_save_and_reopen': True,
          'control_save_added_only_user_settings': sorted(generated),
          'note': 'Real CLI probe; GUI and MCP edit acceptance are not yet run.'}
(run / 'probe.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
(root / 'work/day4-probe-path.txt').write_text(str(run), encoding='utf-8')
print(json.dumps({'passed': True, 'run': str(run), 'change': edit.change}, indent=2))

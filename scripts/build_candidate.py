"""Build a local review bundle from clean committed source. Never publish it."""

import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import tomllib
from uuid import uuid4
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(*arguments):
    return subprocess.check_output(['git', '-c', f'safe.directory={ROOT.as_posix()}', *arguments],
        cwd=ROOT, text=True, encoding='utf-8', timeout=30, creationflags=subprocess.CREATE_NO_WINDOW).strip()


def build():
    if os.name != 'nt' or sys.version_info[:2] != (3, 12) or struct.calcsize('P') != 8:
        raise ValueError('Build with the documented Windows x64 / Python 3.12 environment.')
    if git('status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Commit or preserve and resolve existing changes before building; the source revision must be exact.')
    commit = git('rev-parse', 'HEAD')
    commit_time = git('show', '-s', '--format=%ct', 'HEAD')
    metadata = tomllib.loads(git('show', f'{commit}:pyproject.toml'))
    pin = json.loads(git('show', f'{commit}:toolchain.json'))
    package_version = metadata['project']['version']
    if package_version != pin['tested_environment']['server_package']:
        raise ValueError('Package metadata and toolchain versions disagree.')
    dependencies = {}
    for line in git('show', f'{commit}:requirements.lock').splitlines():
        if not line or line.startswith('#'):
            continue
        name, expected = line.split()[0].split('==')
        actual = version(name)
        if actual != expected:
            raise ValueError(f'Installed {name} differs from the pinned dependency lock.')
        dependencies[name] = actual

    output = ROOT / 'work/candidates' / f'{package_version}-{commit[:7]}-{uuid4().hex[:6]}'
    output.mkdir(parents=True, exist_ok=False)
    source_zip = output / 'source.zip'
    git('archive', '--format=zip', f'--output={source_zip}', commit)
    # The short temporary root also avoids deeply nested Windows build paths.
    staging = Path(tempfile.mkdtemp(prefix='lp-rc-')) / 'source'
    staging.mkdir()
    with zipfile.ZipFile(source_zip) as archive:
        seen = set()
        for info in archive.infolist():
            relative = PurePosixPath(info.filename)
            if (relative.is_absolute() or '..' in relative.parts or '\\' in info.filename
                    or ':' in info.filename or info.filename in seen
                    or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError('Source archive contains an unsupported path or link.')
            seen.add(info.filename)
            target = staging.joinpath(*relative.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(archive.read(info))
    environment = os.environ.copy()
    environment['SOURCE_DATE_EPOCH'] = commit_time
    with (output / 'build-log.txt').open('x', encoding='utf-8') as stream:
        result = subprocess.run([sys.executable, '-m', 'hatchling', 'build', '-t', 'wheel', '-d', str(output)],
            cwd=staging, env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=120,
            creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise ValueError(f'Wheel build failed; retained build log: {output / "build-log.txt"}')
    wheel = output / f'librepcb_mcp_server-{package_version}-py3-none-any.whl'
    if not wheel.is_file():
        raise ValueError('The expected wheel was not produced.')
    with zipfile.ZipFile(wheel) as archive:
        for path in (staging / 'src/librepcb_mcp').rglob('*'):
            if path.is_file() and path.suffix in ('.py', '.lp'):
                if archive.read(path.relative_to(staging / 'src').as_posix()) != path.read_bytes():
                    raise ValueError('Wheel contents differ from the committed source.')

    for name in ('requirements.lock', 'toolchain.json', 'CHANGELOG.md', 'RELEASE_NOTES.md'):
        shutil.copyfile(staging / name, output / name)
    install = f'''# Local LibrePCB MCP candidate {package_version}

WIP, for local review. No public release has been made. See RELEASE_NOTES.md
for supported versions, known limits and outstanding decisions.

Source commit: {commit}

Verify file hashes against manifest.json. Extract source.zip into a reasonably
short folder, such as C:/Projects/LibrePCB-MCP-Server. From that source folder,
follow docs/WINDOWS_SETUP.md to install Python 3.12 x64 and the pinned LibrePCB.
The bootstrap downloads external prerequisites; they are not bundled here.

To test this wheel, after bootstrap run (adjust the wheel path):

```powershell
.\\.venv\\Scripts\\python.exe -m pip install --no-deps --force-reinstall '..\\{wheel.name}'
.\\.venv\\Scripts\\python.exe -m pip check
.\\.venv\\Scripts\\python.exe scripts\\prepare_demo.py --verify
```

Add --experimental-edits to the demo command only for the separate resistor
candidate experiment. Generated client configuration is not installed
automatically. Keep wanted candidates and logs; cleanup is manual after exit.
'''
    (output / 'INSTALL.md').write_text(install, encoding='utf-8', newline='\n')
    names = ['source.zip', wheel.name, 'requirements.lock', 'toolchain.json', 'CHANGELOG.md', 'RELEASE_NOTES.md', 'INSTALL.md']
    manifest = {'package': 'librepcb-mcp-server', 'version': package_version, 'source_commit': commit,
        'source_commit_time': int(commit_time), 'build_python': platform.python_version(),
        'build_backend': f'hatchling {version("hatchling")}', 'dependencies': dependencies,
        'status': 'Local candidate assembled; runtime acceptance is a separate recorded step.',
        'publication': 'None. This script does not upload, tag, publish or edit client settings.',
        'artifacts': [{'path': name, 'bytes': (output / name).stat().st_size, 'sha256': digest(output / name)} for name in names]}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    bundle = output / f'librepcb-mcp-server-{package_version}-local.zip'
    with zipfile.ZipFile(bundle, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in [*names, 'manifest.json']:
            archive.write(output / name, arcname=name)
    (output / (bundle.name + '.sha256')).write_text(f'{digest(bundle)}  {bundle.name}\n', encoding='ascii')
    (output / 'build-context.json').write_text(json.dumps({'source_staging': str(staging),
        'note': 'Build source and logs are retained locally; not part of the review ZIP.'}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'bundle': str(bundle), 'sha256': digest(bundle), 'wheel': str(wheel),
                      'source_commit': commit, 'manifest': str(output / 'manifest.json')}, indent=2))


if __name__ == '__main__':
    try:
        build()
    except (ValueError, OSError, PackageNotFoundError, subprocess.SubprocessError) as exc:
        print(f'Candidate build failed: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc

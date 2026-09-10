param([string]$PythonExe = 'python')

# Run from PowerShell. Files stay under this repository; no PATH/registry edits.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
# Native Qt is required by the tested Windows CLI; no persistent environment edit.
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$toolchain = Get-Content -LiteralPath (Join-Path $repoRoot 'toolchain.json') -Raw | ConvertFrom-Json
$downloadDir = Join-Path $repoRoot 'work/downloads'
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null
$archivePath = Join-Path $downloadDir 'librepcb-2.1.1-windows-x86_64.zip'
if (-not (Test-Path -LiteralPath $archivePath)) {
    Invoke-WebRequest -Uri $toolchain.librepcb.url -OutFile $archivePath -TimeoutSec 300
}
$actualHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $toolchain.librepcb.sha256) {
    throw 'LibrePCB archive hash mismatch. Inspect the existing file before retrying.'
}
$toolDir = Join-Path $repoRoot 'work/tools/librepcb-2.1.1'
if (-not (Test-Path -LiteralPath $toolDir)) {
    Expand-Archive -LiteralPath $archivePath -DestinationPath $toolDir
}
$cli = Join-Path $repoRoot $toolchain.librepcb.relative_executable
$signature = Get-AuthenticodeSignature -LiteralPath $cli
if ($signature.Status -ne 'Valid') {
    throw "LibrePCB executable signature verification failed: $($signature.Status)"
}
& $cli --version
if ($LASTEXITCODE -ne 0) { throw 'LibrePCB CLI could not start.' }
$venvPython = Join-Path $repoRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $PythonExe -c 'import sys; assert sys.version_info[:2] == (3,12), "Python 3.12 required"'
    if ($LASTEXITCODE -ne 0) { throw 'A usable Python 3.12 interpreter is required.' }
    & $PythonExe -m venv (Join-Path $repoRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Creating the local Python environment failed.' }
}
& $venvPython --version
if ($LASTEXITCODE -ne 0) { throw 'The local Python environment could not start.' }
& $venvPython -c 'import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize("P") == 8, "Python 3.12 x64 required"'
if ($LASTEXITCODE -ne 0) { throw 'The pinned dependency lock requires Python 3.12 x64.' }
& $venvPython -m pip --disable-pip-version-check install --require-hashes -r (Join-Path $repoRoot 'requirements.lock')
if ($LASTEXITCODE -ne 0) { throw 'Installing the pinned dependencies failed.' }
& $venvPython -m pip --disable-pip-version-check install --no-deps --no-build-isolation -e $repoRoot
if ($LASTEXITCODE -ne 0) { throw 'Installing the local MCP package failed.' }
& $venvPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency validation failed.' }
Write-Output 'Local MCP prerequisites ready. Follow docs/WINDOWS_SETUP.md to connect a client.'

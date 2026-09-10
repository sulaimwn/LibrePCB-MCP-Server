param([string]$PythonExe = 'python')

# Run from PowerShell. Files stay under this repository; no PATH/registry edits.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
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
    & $PythonExe -c 'import sys; assert sys.version_info >= (3,12), "Python 3.12+ required"'
    if ($LASTEXITCODE -ne 0) { throw 'A usable Python 3.12+ interpreter is required.' }
    & $PythonExe -m venv (Join-Path $repoRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Creating the local Python environment failed.' }
}
& $venvPython --version
if ($LASTEXITCODE -ne 0) { throw 'The local Python environment could not start.' }
Write-Output 'Local prerequisites ready. No third-party Python dependencies at this milestone.'

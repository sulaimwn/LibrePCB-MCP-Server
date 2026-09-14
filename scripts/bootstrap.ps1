param([string]$PythonExe = 'python')

# Run from PowerShell. Files stay under this repository; no PATH/registry edits.
$ErrorActionPreference = 'Stop'
# Use this PowerShell's built-in modules even when a launcher inherited another
# PowerShell edition's PSModulePath (for example Python launched from PowerShell 7).
foreach ($moduleName in @('Microsoft.PowerShell.Utility', 'Microsoft.PowerShell.Security', 'Microsoft.PowerShell.Archive')) {
    Import-Module (Join-Path $PSHOME ('Modules/' + $moduleName)) -ErrorAction Stop
}
$repoRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $repoRoot '.venv/Scripts/python.exe'
$checkPython = Join-Path $PSScriptRoot 'check_python.py'
$prerequisitePython = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { $PythonExe }
$resolvedPython = Get-Command $prerequisitePython -CommandType Application -ErrorAction Stop
if ($resolvedPython.Source -like '*\Microsoft\WindowsApps\python*.exe') {
    throw 'Pass a real Python 3.12 x64 executable with -PythonExe; the WindowsApps alias is not sufficient.'
}
& $prerequisitePython $checkPython
if ($LASTEXITCODE -ne 0) { throw 'A usable Python 3.12 x64 interpreter is required before setup.' }
$toolchain = Get-Content -LiteralPath (Join-Path $repoRoot 'toolchain.json') -Raw | ConvertFrom-Json
$downloadDir = Join-Path $repoRoot 'work/downloads'
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null
$archivePath = Join-Path $downloadDir 'librepcb-2.1.1-windows-x86_64.zip'
if (-not (Test-Path -LiteralPath $archivePath)) {
    Write-Output 'Downloading the pinned LibrePCB portable archive...'
    $partialPath = Join-Path $downloadDir ('download-' + [guid]::NewGuid().ToString('N') + '.partial')
    $previousProgress = $ProgressPreference
    try {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -UseBasicParsing -Uri $toolchain.librepcb.url -OutFile $partialPath -TimeoutSec 300
        if ((Get-FileHash -LiteralPath $partialPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $toolchain.librepcb.sha256) {
            throw "Downloaded archive hash mismatch; partial file retained at $partialPath"
        }
        # Publish only a verified download; interrupted partials cannot poison retries.
        Move-Item -LiteralPath $partialPath -Destination $archivePath
    } finally {
        $ProgressPreference = $previousProgress
    }
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
if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) {
    throw "Portable installation is incomplete at $toolDir. Preserve/inspect that folder before retrying setup."
}
$signature = Get-AuthenticodeSignature -LiteralPath $cli
if ($signature.Status -ne 'Valid') {
    throw "LibrePCB executable signature verification failed: $($signature.Status)"
}
# Native Qt is required; restore the caller's process environment afterwards.
$previousQt = [Environment]::GetEnvironmentVariable('QT_QPA_PLATFORM', 'Process')
try {
    Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
    $cliVersion = & $cli --version
    if ($LASTEXITCODE -ne 0) { throw 'LibrePCB CLI could not start.' }
    if ($cliVersion -notcontains 'LibrePCB CLI Version 2.1.1' -or $cliVersion -notcontains 'File Format 2 (stable)') {
        throw 'The portable CLI must be LibrePCB 2.1.1 with stable file format 2.'
    }
    Write-Output $cliVersion
} finally {
    [Environment]::SetEnvironmentVariable('QT_QPA_PLATFORM', $previousQt, 'Process')
}
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Output 'Creating the local Python environment...'
    & $PythonExe -m venv (Join-Path $repoRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Creating the local Python environment failed.' }
}
& $venvPython --version
if ($LASTEXITCODE -ne 0) { throw 'The local Python environment could not start.' }
& $venvPython $checkPython
if ($LASTEXITCODE -ne 0) { throw 'The pinned dependency lock requires Python 3.12 x64.' }
& $venvPython -m pip --disable-pip-version-check install --require-hashes -r (Join-Path $repoRoot 'requirements.lock')
if ($LASTEXITCODE -ne 0) { throw 'Installing the pinned dependencies failed.' }
& $venvPython -m pip --disable-pip-version-check install --no-deps --no-build-isolation -e $repoRoot
if ($LASTEXITCODE -ne 0) { throw 'Installing the local MCP package failed.' }
& $venvPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency validation failed.' }
Write-Output 'Local MCP prerequisites ready. Follow docs/WINDOWS_SETUP.md to connect a client.'

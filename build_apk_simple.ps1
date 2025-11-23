# Simple APK builder script (ASCII-safe)
param(
    [switch]$NoInstall,
    [switch]$SkipDeps
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host 'Starting simple APK build script...'

# Check python 3.11 availability
try {
    & py -3.11 --version > $null 2>&1
    $pythonCmd = 'py -3.11'
} catch {
    Write-Host 'Python 3.11 not found. Please install Python 3.11 and retry.' -ForegroundColor Red
    exit 1
}

# Create venv if missing
$venvDir = Join-Path $ProjectRoot 'venv_android'
if (-not (Test-Path $venvDir)) {
    Write-Host 'Creating virtual environment...'
    & $pythonCmd -m venv $venvDir
} else {
    Write-Host 'Virtual environment already exists.'
}

# Activate venv and install deps
$activate = Join-Path $venvDir 'Scripts\Activate.ps1'
if (-not (Test-Path $activate)) {
    Write-Host 'Activate script not found in venv. Aborting.' -ForegroundColor Red
    exit 1
}

Write-Host 'Activating virtualenv...'
& $activate

if (-not $SkipDeps) {
    Write-Host 'Upgrading pip and installing build dependencies...'
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install buildozer cython kivy kivymd pillow jnius
} else {
    Write-Host 'Skipping dependency installation.'
}

Write-Host 'Starting Buildozer build (android debug). This may take a while...'
python -m buildozer android debug

Write-Host 'Buildozer finished. Check bin/ for the APK.'

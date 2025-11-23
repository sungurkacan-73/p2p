# P2P Paylaş - Android APK Builder (PowerShell)
# This script automates the APK build process using Python 3.11

param(
    [switch]$NoInstall,
    [switch]$SkipDeps,
    [string]$Python311Path
)

$ErrorActionPreference = "Stop"

# Color codes
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }

# Get script directory
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvName = "venv_android"
$VenvPath = Join-Path $ProjectRoot $VenvName

Write-Host (''.PadLeft(60,'='))
Write-Host "🔧 P2P Paylaş - Android APK Builder (PowerShell)"
Write-Host (''.PadLeft(60,'='))

# Step 1: Check Python 3.11
Write-Host "`n[1/6] Checking Python 3.11..."

$PythonCmd = "py"
if ($Python311Path) {
    $PythonCmd = $Python311Path
}

try {
    $Version = & $PythonCmd -3.11 --version 2>&1
    Write-Success "Python found: $Version"
} catch {
    Write-Error "Python 3.11 not found"
    Write-Info "Install Python 3.11 from: https://www.python.org/downloads/"
    Write-Info "Or use: py -3.11 --version"
    exit 1
}

# Step 2: Create Virtual Environment
Write-Host "`n[2/6] Creating virtual environment..."

if (Test-Path $VenvPath) {
    Write-Success "Virtual environment already exists"
} else {
    try {
        & $PythonCmd -3.11 -m venv $VenvName
        Write-Success "Virtual environment created"
    } catch {
        Write-Error "Failed to create virtual environment: $_"
        exit 1
    }
}

# Step 3: Activate Virtual Environment
Write-Host "`n[3/6] Activating virtual environment..."

$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $ActivateScript)) {
    Write-Error "Activate script not found at: $ActivateScript"
    exit 1
}

& $ActivateScript
Write-Success "Virtual environment activated"

# Step 4: Install Dependencies
if (-not $SkipDeps) {
    Write-Host "`n[4/6] Installing dependencies..."
    
    Write-Info "Updating pip..."
    python -m pip install --upgrade pip setuptools wheel -q
    
    $Packages = @(
        "buildozer",
        "cython",
        "kivy",
        "kivymd",
        "pillow",
        "jnius"
    )
    
    foreach ($pkg in $Packages) {
        Write-Info "Installing $pkg..."
        python -m pip install $pkg -q
    }
    
    Write-Success "All dependencies installed"
} else {
    Write-Info "Skipping dependency installation"
}

# Step 5: Build APK
Write-Host "`n[5/6] Building Android APK..."
Write-Info "This may take 5-15 minutes..."

Set-Location $ProjectRoot

try {
    & python -m buildozer android debug
    Write-Success "APK build completed"
} catch {
    Write-Error "APK build failed: $_"
    Write-Info "Check .buildozer/android/platform/build-*/build/logs/ for details"
    exit 1
}

# Step 6: Find and Install APK
Write-Host "`n[6/6] Finalizing build..."

$BinDir = Join-Path $ProjectRoot "bin"
$ApkFile = Get-ChildItem $BinDir -Filter "*.apk" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($ApkFile) {
    $SizeMB = [math]::Round($ApkFile.Length / 1MB, 2)
    Write-Success "APK generated: $($ApkFile.Name)"
    Write-Info "Size: $SizeMB MB"
    Write-Info "Location: $($ApkFile.FullName)"
    
    if (-not $NoInstall) {
        Write-Info "Attempting to install via ADB..."
        try {
            & adb install -r $ApkFile.FullName 2>&1 | Out-Null
            Write-Success "APK installed on device"
        } catch {
            Write-Info "ADB not available - manual installation required"
            Write-Info "Transfer file to device and tap to install"
        }
    }
} else {
    Write-Error "APK file not found in $BinDir"
    exit 1
}

# Summary
Write-Host "`n" + "="*60
Write-Host "P2P Paylaş - Android APK Build Complete"
Write-Host "="*60

if ($ApkFile) {
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Transfer APK to Android device"
    Write-Host "  2. Tap the APK file on your device to install"
    Write-Host "  3. Grant requested permissions when prompted"
    Write-Host "  4. Launch the app from your app drawer"
    Write-Host ""
    Write-Host "App Name: P2P Paylas"
    Write-Host "Package: org.p2p.p2share"
    Write-Host "Version: 1.0"
    Write-Host "Min Android: 5.0 (API 21)"
    Write-Host "Target Android: 12 (API 31)"
}

Write-Host "`n"

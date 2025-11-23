<#
Build helper for Inno Setup installer.
Usage: run from project root. Requires Inno Setup 6 installed (ISCC.exe).
#>
Param()

$projectRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location -Path $projectRoot

Write-Host "Checking for Inno Setup (ISCC.exe)..."
$possiblePaths = @(
    "$Env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
    "$Env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$iscc = $null
foreach ($p in $possiblePaths) {
    if (Test-Path $p) { $iscc = $p; break }
}
if (-not $iscc) {
    try { $which = (Get-Command ISCC.exe -ErrorAction Stop).Source; $iscc = $which } catch { }
}

if (-not $iscc) {
    Write-Host "Inno Setup compiler (ISCC.exe) not found.\nInstall Inno Setup (https://jrsoftware.org/) or add ISCC.exe to PATH." -ForegroundColor Yellow
    Write-Host "Falling back: creating ZIP of dist/ as a simple installer alternative..." -ForegroundColor Yellow
    $zipName = "p2p_windows_portable.zip"
    if (Test-Path dist) {
        if (Test-Path $zipName) { Remove-Item $zipName }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [IO.Compression.ZipFile]::CreateFromDirectory((Resolve-Path dist), (Join-Path $projectRoot $zipName))
        Write-Host "Created portable ZIP: $zipName" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "dist/ not found. Build the executable first (PyInstaller)." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Using ISCC at: $iscc" -ForegroundColor Green
$iss = Join-Path $projectRoot 'installer.iss'
if (-not (Test-Path $iss)) { Write-Host "installer.iss not found in project root" -ForegroundColor Red; exit 1 }

$env:Src = $projectRoot

& "$iscc" /Qp "$iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Installer built. Check output folder next to the script (Output) or the Inno Setup output location." -ForegroundColor Green
} else {
    Write-Host "ISCC failed with exit code $LASTEXITCODE" -ForegroundColor Red
}

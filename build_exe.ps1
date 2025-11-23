Param(
    [switch]$WithInstaller
)

$projectRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location $projectRoot

Write-Host "[+] PyInstaller kontrol ediliyor..." -ForegroundColor Cyan
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "[!] PyInstaller bulunamadı. 'pip install pyinstaller' komutunu çalıştırın." -ForegroundColor Red
    exit 1
}

$spec = Join-Path $projectRoot 'p2p_gui_onefile.spec'
if (Test-Path $spec) {
    Write-Host "[+] Spec dosyası bulundu: $spec" -ForegroundColor Cyan
    pyinstaller --clean --noconfirm $spec
} else {
    $spec = Join-Path $projectRoot 'p2p_gui.spec'
    if (Test-Path $spec) {
        Write-Host "[+] Spec dosyası bulundu: $spec" -ForegroundColor Cyan
        pyinstaller --clean --noconfirm $spec
    } else {
        Write-Host "[+] Spec bulunamadı, doğrudan komut kullanılacak." -ForegroundColor Yellow
        pyinstaller --clean --noconfirm --windowed --name p2p_gui p2p_gui.py
    }
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] PyInstaller derlemesi başarısız." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[✓] EXE oluşturuldu: dist\\p2p_gui.exe" -ForegroundColor Green

if ($WithInstaller) {
    Write-Host "[+] Inno Setup installer derlemesi tetikleniyor..." -ForegroundColor Cyan
    & "$projectRoot/build_installer.ps1"
    exit $LASTEXITCODE
}

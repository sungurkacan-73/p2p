#!/usr/bin/env powershell
<#
.SYNOPSIS
P2P Dosya Aktarımı - Windows EXE Hızlı Başlangıç Scripti

.DESCRIPTION
Bu script p2p_gui.exe dosyasını başlatır ve temel ayarları yapar.

.EXAMPLE
.\run_p2p.ps1
#>

# Renk tanımlamaları
$Green = 'Green'
$Yellow = 'Yellow'
$Red = 'Red'

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor $Green
Write-Host "║     P2P Dosya Aktarımı - Windows EXE Başlatıcısı         ║" -ForegroundColor $Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor $Green
Write-Host ""

# EXE dosya yolunu belirle
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExePath = Join-Path $ScriptDir "dist\p2p_gui.exe"

# EXE kontrolü
if (-not (Test-Path $ExePath)) {
    Write-Host "[!] Hata: p2p_gui.exe bulunamadı!" -ForegroundColor $Red
    Write-Host "    Beklenen konum: $ExePath"
    Write-Host ""
    Write-Host "Çözüm: Projeyi pyinstaller ile derleyin:" -ForegroundColor $Yellow
    Write-Host "    pyinstaller p2p_gui.py --onefile --windowed -y"
    exit 1
}

Write-Host "[✓] p2p_gui.exe bulundu" -ForegroundColor $Green
Write-Host "    Konum: $ExePath"
Write-Host ""

# Sistem kontrolü
$OSVersion = [System.Environment]::OSVersion.VersionString
Write-Host "[✓] İşletim Sistemi: $OSVersion" -ForegroundColor $Green

# Ağ bağlantısı kontrolü
Write-Host ""
Write-Host "🌐 Ağ Bilgileri:" -ForegroundColor $Yellow
$NetworkAdapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}
$NetworkAdapters | ForEach-Object {
    Write-Host "    • $($_.Name) ($($_.InterfaceDescription))"
}

Write-Host ""
Write-Host "🚀 Uygulama başlatılıyor..." -ForegroundColor $Yellow
Write-Host ""

# EXE'yi başlat
try {
    Start-Process -FilePath $ExePath -WorkingDirectory $ScriptDir
    Write-Host "[✓] Uygulama başlatıldı!" -ForegroundColor $Green
    Write-Host ""
    Write-Host "📌 İpuçları:" -ForegroundColor $Yellow
    Write-Host "   1. PIN: Gönderici ve alıcının aynı PIN kullanması gerekir"
    Write-Host "   2. Port: Varsayılan port 5000, değiştirebilirsiniz"
    Write-Host "   3. Mode: 'Gönder' için sender, 'Al' için receiver"
    Write-Host "   4. Dosya: Klasör de seçebilirsiniz (otomatik zip yapılır)"
    Write-Host ""
}
catch {
    Write-Host "[!] Hata: Uygulama başlatılamadı" -ForegroundColor $Red
    Write-Host "    Hata: $_"
    exit 1
}

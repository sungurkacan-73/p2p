#!/usr/bin/env python3
"""
Package Manager: Automated serialization of P2P project files.

This script packages all three main source files (p2p.py, p2p_gui.py, main.py)
into a single distribute-ready .zip file, streamlining deployment.

Usage:
    python package_manager.py [--output-dir OUTPUT_DIR]
    
    By default, creates 'p2p_package.zip' in the current working directory.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile


class PackageManager:
    """Manages packaging of P2P project files."""
    
    # Files required for distribution
    REQUIRED_FILES = [
        "p2p.py",
        "p2p_gui.py",
        "main.py",
        "README.md",
    ]
    
    # Optional files to include if present
    OPTIONAL_FILES = [
        "requirements.txt",
        "buildozer.spec",
        "p2p.spec",
    ]
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def validate_files(self) -> bool:
        """Check if all required files exist in the project root."""
        missing = []
        for filename in self.REQUIRED_FILES:
            if not (self.project_root / filename).exists():
                missing.append(filename)
        
        if missing:
            print(f"[!] Eksik dosyalar: {', '.join(missing)}")
            return False
        return True
    
    def create_package(self, output_path: Path) -> bool:
        """Create a .zip package with all necessary files."""
        try:
            print(f"[+] Paket oluşturuluyor: {output_path}")
            
            with ZipFile(output_path, 'w', compression=8) as zf:
                # Add required files
                for filename in self.REQUIRED_FILES:
                    file_path = self.project_root / filename
                    if file_path.exists():
                        arcname = filename
                        zf.write(file_path, arcname=arcname)
                        print(f"    ✓ {filename}")
                
                # Add optional files if they exist
                for filename in self.OPTIONAL_FILES:
                    file_path = self.project_root / filename
                    if file_path.exists():
                        arcname = filename
                        zf.write(file_path, arcname=arcname)
                        print(f"    ✓ {filename}")
                
                # Add metadata file
                metadata = self._create_metadata()
                zf.writestr("MANIFEST.txt", metadata)
                print(f"    ✓ MANIFEST.txt")
            
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"[✓] Paket başarıyla oluşturuldu: {output_path}")
            print(f"    Boyut: {size_mb:.2f} MB")
            return True
            
        except Exception as e:
            print(f"[!] Hata: {e}")
            return False
    
    def _create_metadata(self) -> str:
        """Generate metadata for the package."""
        return f"""
=== P2P File Transfer Package ===
Paketleme Tarihi: {datetime.now().isoformat()}
Proje Kökü: {self.project_root}

İçindekiler:
- p2p.py: Temel P2P mantığı (HMAC-SHA256, dinamik buffer, dizin zipleme)
- p2p_gui.py: Windows Tkinter arayüzü
- main.py: Android KivyMD arayüzü (Samsung One UI stili, pyjnius entegrasyonu)
- README.md: Proje belgeleri

Özellikler:
- Dinamik TCP buffer optimizasyonu
- Otomatik dizin zipleme
- Android WakeLock/WifiLock desteği
- Samsung One UI tasarımı
- Turkish localization

Gereksinimler:
  Windows: tkinter (dahil), python 3.8+
  Android: kivy, kivymd, pyjnius, buildozer
""".strip()
    
    def build_distribution(self, output_dir: Path = None) -> bool:
        """Complete distribution build process."""
        if not self.validate_files():
            return False
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_path = output_dir / f"p2p_package_{self.timestamp}.zip"
        return self.create_package(output_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="P2P Proje Paketleyicisi - Tüm dosyaları distribute-ready .zip formatına seri hale getir"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Proje kök dizini (varsayılan: geçerli dizin)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Çıkış dizini (varsayılan: geçerli dizin)"
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default=None,
        help="Özel çıkış dosya adı (.zip uzantısı olmadan)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    
    args = parse_args(argv)
    
    print("[+] P2P Paketleyici başlatılıyor...")
    print(f"    Proje Kökü: {args.project_root}")
    print(f"    Çıkış Dizini: {args.output_dir}")
    
    manager = PackageManager(args.project_root)
    
    if args.output_name:
        output_path = args.output_dir / f"{args.output_name}.zip"
        result = manager.create_package(output_path)
    else:
        result = manager.build_distribution(args.output_dir)
    
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())

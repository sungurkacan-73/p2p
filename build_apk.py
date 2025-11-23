#!/usr/bin/env python3
"""
APK Build Helper Script for P2P Paylaş
Configures and builds Android APK with proper Python 3.11+ environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class APKBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_name = "venv_android"
        self.venv_path = self.project_root / self.venv_name
        self.is_windows = platform.system() == "Windows"
        
    def run_command(self, cmd, shell=False):
        """Run command and return success status"""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=False,
                text=True,
                cwd=self.project_root
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error running command: {e}")
            return False
    
    def check_python_version(self):
        """Check if Python 3.11+ is available"""
        version = sys.version_info
        print(f"✓ Current Python: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print("\n⚠ Warning: Python 3.11+ recommended for buildozer")
            print("  Current version may not be compatible")
            print("\n  Solutions:")
            print("  1. Install Python 3.11: https://www.python.org/downloads/")
            print("  2. Create virtual environment: py -3.11 -m venv venv_android")
            print("  3. Activate: .\\venv_android\\Scripts\\Activate.ps1")
            return False
        return True
    
    def create_venv(self):
        """Create Python virtual environment"""
        print(f"\n📦 Creating virtual environment: {self.venv_name}")
        
        if self.venv_path.exists():
            print(f"  ✓ Virtual environment already exists")
            return True
        
        if self.is_windows:
            cmd = f"py -3.11 -m venv {self.venv_name}"
        else:
            cmd = f"python3.11 -m venv {self.venv_name}"
        
        if not self.run_command(cmd, shell=True):
            print("  ✗ Failed to create virtual environment")
            return False
        
        print(f"  ✓ Virtual environment created")
        return True
    
    def get_pip_command(self):
        """Get pip command for current environment"""
        if self.is_windows:
            return str(self.venv_path / "Scripts" / "pip.exe")
        return str(self.venv_path / "bin" / "pip")
    
    def get_python_command(self):
        """Get python command for current environment"""
        if self.is_windows:
            return str(self.venv_path / "Scripts" / "python.exe")
        return str(self.venv_path / "bin" / "python")
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("\n📚 Installing dependencies...")
        
        pip_cmd = self.get_pip_command()
        
        # Update pip
        print("  • Updating pip...")
        self.run_command(f"{pip_cmd} install --upgrade pip setuptools wheel", shell=True)
        
        # Install buildozer and dependencies
        packages = [
            "buildozer",
            "cython",
            "kivy",
            "kivymd",
            "pillow",
            "jnius"
        ]
        
        for pkg in packages:
            print(f"  • Installing {pkg}...")
            if not self.run_command(f"{pip_cmd} install {pkg}", shell=True):
                print(f"  ✗ Failed to install {pkg}")
                return False
        
        print("  ✓ All dependencies installed")
        return True
    
    def check_java(self):
        """Check if Java is installed"""
        print("\n☕ Checking Java installation...")
        
        try:
            result = subprocess.run(
                "java -version",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("  ✓ Java found")
                return True
        except:
            pass
        
        print("  ✗ Java not found")
        print("\n  Install Java Development Kit (JDK):")
        if self.is_windows:
            print("    - Download from: https://www.oracle.com/java/technologies/downloads/")
            print("    - Or use: choco install openjdk11")
        else:
            print("    - Ubuntu/Debian: sudo apt-get install openjdk-11-jdk")
            print("    - macOS: brew install openjdk@11")
        return False
    
    def build_apk(self):
        """Build Android APK"""
        print("\n🔨 Building Android APK...")
        print("  This may take 5-15 minutes depending on your system")
        
        python_cmd = self.get_python_command()
        
        # Run buildozer
        cmd = f"{python_cmd} -m buildozer android debug"
        
        if not self.run_command(cmd, shell=True):
            print("\n  ✗ Build failed")
            print("\n  Troubleshooting:")
            print("    - Check logs in .buildozer/android/platform/build-*/build/logs/")
            print("    - Run with verbose: buildozer android debug -v")
            print("    - Clean and retry: buildozer android debug --clean")
            return False
        
        print("  ✓ APK build successful")
        return True
    
    def find_apk(self):
        """Find generated APK file"""
        bin_dir = self.project_root / "bin"
        
        if not bin_dir.exists():
            return None
        
        apk_files = list(bin_dir.glob("*.apk"))
        if apk_files:
            return apk_files[-1]  # Return newest APK
        
        return None
    
    def install_apk(self):
        """Install APK on connected Android device"""
        print("\n📱 Installing on Android device...")
        
        apk_file = self.find_apk()
        if not apk_file:
            print("  ✗ APK file not found in bin/ directory")
            return False
        
        print(f"  Found: {apk_file.name}")
        
        # Try to install with ADB
        try:
            result = subprocess.run(
                f"adb install -r \"{apk_file}\"",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✓ APK installed successfully")
                return True
            else:
                print("  ℹ ADB not available or device not connected")
                print(f"  Manual install: {apk_file}")
                return True
        except:
            print("  ℹ ADB not available")
            print(f"  Manual install: {apk_file}")
            return True
    
    def show_summary(self):
        """Show build summary"""
        print("\n" + "="*60)
        print("🎉 P2P Paylaş - Android APK Build Summary")
        print("="*60)
        
        apk_file = self.find_apk()
        if apk_file:
            size_mb = apk_file.stat().st_size / (1024 * 1024)
            print(f"\n✓ APK Generated: {apk_file.name}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Location: {apk_file}")
            print("\nNext steps:")
            print("  1. Transfer APK to Android device")
            print("  2. Tap APK file to install")
            print("  3. Grant permissions when prompted")
            print("  4. Launch 'P2P Paylaş' from app drawer")
        else:
            print("\n✗ APK not found")
            print("  Check build logs for errors")
    
    def run(self, skip_install=False):
        """Execute full build process"""
        print("="*60)
        print("🔧 P2P Paylaş - Android APK Builder")
        print("="*60)
        
        steps = [
            ("Check Python", self.check_python_version),
            ("Check Java", self.check_java),
            ("Create Virtual Environment", self.create_venv),
            ("Install Dependencies", self.install_dependencies),
            ("Build APK", self.build_apk),
        ]
        
        for step_name, step_func in steps:
            print(f"\n[{steps.index((step_name, step_func))+1}/{len(steps)}] {step_name}...")
            if not step_func():
                print(f"\n✗ Build failed at: {step_name}")
                return False
        
        if not skip_install:
            print(f"\n[{len(steps)+1}/{len(steps)+1}] Install APK...")
            self.install_apk()
        
        self.show_summary()
        return True


def main():
    """Main entry point"""
    builder = APKBuilder()
    
    # Parse arguments
    skip_install = "--no-install" in sys.argv
    
    try:
        if builder.run(skip_install=skip_install):
            print("\n✓ Build process completed")
            sys.exit(0)
        else:
            print("\n✗ Build process failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠ Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

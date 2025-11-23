#!/usr/bin/env python3
"""
DEBUG VERIFICATION REPORT
Samsung One UI P2P File Transfer - Project Status Check
Generated: 2025-01-22
"""

import ast
import sys
from pathlib import Path
from zipfile import ZipFile

def verify_python_syntax():
    """Verify all Python files have valid syntax."""
    print("\n=== PYTHON SYNTAX VERIFICATION ===\n")
    files = ['p2p.py', 'p2p_gui.py', 'package_manager.py', 'main.py']
    all_ok = True
    
    for fname in files:
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            print(f"[✓] {fname}: Valid syntax")
        except SyntaxError as e:
            print(f"[!] {fname}: SYNTAX ERROR - {e}")
            all_ok = False
        except Exception as e:
            print(f"[!] {fname}: ERROR - {e}")
            all_ok = False
    
    return all_ok

def verify_functions():
    """Verify critical functions exist."""
    print("\n=== FUNCTION VERIFICATION ===\n")
    try:
        from p2p import (
            get_optimal_chunk_size,
            send_file,
            receive_file,
            derive_key,
            handshake,
            ensure_local,
            recv_exact
        )
        print("[✓] All critical functions imported successfully:")
        print("    • get_optimal_chunk_size()")
        print("    • send_file()")
        print("    • receive_file()")
        print("    • derive_key()")
        print("    • handshake()")
        print("    • ensure_local()")
        print("    • recv_exact()")
        return True
    except ImportError as e:
        print(f"[!] Import error: {e}")
        return False

def verify_buffer_optimization():
    """Test buffer optimization algorithm."""
    print("\n=== BUFFER OPTIMIZATION TESTS ===\n")
    from p2p import get_optimal_chunk_size
    
    tests = [
        (5 * 1024 * 1024, 64 * 1024, "5 MB file"),
        (50 * 1024 * 1024, 1024 * 1024, "50 MB file"),
        (500 * 1024 * 1024, 4 * 1024 * 1024, "500 MB file"),
        (2 * 1024 * 1024 * 1024, 8 * 1024 * 1024, "2 GB file"),
    ]
    
    all_ok = True
    for file_size, expected, description in tests:
        result = get_optimal_chunk_size(file_size)
        status = "✓" if result == expected else "!"
        print(f"[{status}] {description}: {result} bytes (expected {expected})")
        if result != expected:
            all_ok = False
    
    return all_ok

def verify_documentation():
    """Verify documentation files exist."""
    print("\n=== DOCUMENTATION VERIFICATION ===\n")
    docs = [
        ('IMPLEMENTATION.md', 'Technical specifications'),
        ('QUICKSTART.md', 'Quick reference guide'),
        ('CODE_CHANGES.md', 'Code change details'),
        ('COMPLETION_REPORT.md', 'Project completion summary'),
        ('INDEX.md', 'File navigation index'),
    ]
    
    all_ok = True
    for fname, description in docs:
        path = Path(fname)
        if path.exists():
            size = path.stat().st_size
            print(f"[✓] {fname}: {size} bytes ({description})")
        else:
            print(f"[!] {fname}: MISSING")
            all_ok = False
    
    return all_ok

def verify_package_manager():
    """Verify package manager creates valid packages."""
    print("\n=== PACKAGE MANAGER VERIFICATION ===\n")
    try:
        # Import without requiring Kivy
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("package_manager", "package_manager.py")
        pm_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pm_module)
        
        PackageManager = pm_module.PackageManager
        
        pm = PackageManager()
        
        # Check validation
        if pm.validate_files():
            print("[✓] All required files validated")
        else:
            print("[!] File validation failed")
            return False
        
        # Check package creation
        test_zip = Path("debug_test_package.zip")
        if pm.create_package(test_zip):
            print(f"[✓] Package created: {test_zip}")
            
            # Verify contents
            with ZipFile(test_zip, 'r') as z:
                contents = z.namelist()
                print(f"[✓] Package contains {len(contents)} files:")
                for name in contents:
                    print(f"    • {name}")
            
            # Cleanup
            test_zip.unlink()
            print("[✓] Test package cleaned up")
            return True
        else:
            print("[!] Package creation failed")
            return False
            
    except Exception as e:
        print(f"[!] Package manager error: {e}")
        return False

def verify_file_structure():
    """Verify project file structure."""
    print("\n=== PROJECT FILE STRUCTURE ===\n")
    
    files = {
        'Core': ['p2p.py', 'p2p_gui.py', 'main.py'],
        'Tools': ['package_manager.py'],
        'Config': ['buildozer_template.spec'],
        'Docs': ['IMPLEMENTATION.md', 'QUICKSTART.md', 'CODE_CHANGES.md', 
                 'COMPLETION_REPORT.md', 'INDEX.md', 'README.md']
    }
    
    all_ok = True
    for category, file_list in files.items():
        print(f"\n{category}:")
        for fname in file_list:
            path = Path(fname)
            if path.exists():
                size = path.stat().st_size
                print(f"  [✓] {fname}: {size} bytes")
            else:
                print(f"  [!] {fname}: MISSING")
                all_ok = False
    
    return all_ok

def verify_features():
    """Verify key features are implemented."""
    print("\n=== FEATURE VERIFICATION ===\n")

    features = {
        'Dynamic Buffer Optimization': ('get_optimal_chunk_size', 'p2p.py'),
        'Directory Zipping': ('tempfile.TemporaryDirectory', 'p2p.py'),
        'Tabbed Send/Receive UI': ('class SendTab', 'main.py'),
        'Automatic LAN/WAN Scope': ('_determine_scope', 'main.py'),
        'Turkish Localization': ('P2P Paylaş - PIN Korumalı', 'main.py'),
        'Primary Accent Color': ('0, 122/255, 254/255, 1', 'main.py'),
        'Distribution Automation': ('PackageManager', 'package_manager.py'),
    }
    
    all_ok = True
    for feature, (marker, filename) in features.items():
        found = False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if marker in content:
                    found = True
        except Exception as e:
            print(f"[!] Error reading {filename}: {e}")
            all_ok = False
            continue
        
        status = "✓" if found else "!"
        print(f"[{status}] {feature}")
        if not found:
            all_ok = False
    
    return all_ok

def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("DEBUG VERIFICATION REPORT")
    print("Samsung One UI P2P File Transfer")
    print("="*60)
    
    results = {
        'Python Syntax': verify_python_syntax(),
        'Functions': verify_functions(),
        'Buffer Optimization': verify_buffer_optimization(),
        'File Structure': verify_file_structure(),
        'Documentation': verify_documentation(),
        'Features': verify_features(),
        'Package Manager': verify_package_manager(),
    }
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"[{status}] {test_name}")
    
    overall = all(results.values())
    print("\n" + "="*60)
    if overall:
        print("✓ ALL CHECKS PASSED - PROJECT IS READY")
    else:
        print("✗ SOME CHECKS FAILED - REVIEW NEEDED")
    print("="*60 + "\n")
    
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())

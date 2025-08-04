#!/usr/bin/env python3
"""
Test script to verify the EMG Plotter build
"""

import os
import sys
import subprocess

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    modules = [
        'PyQt6.QtWidgets',
        'PyQt6.QtCore', 
        'PyQt6.QtGui',
        'matplotlib',
        'pandas',
        'numpy',
        'plot_emg',
        'emg_plotter_gui'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_files():
    """Test that required files exist"""
    print("\nTesting files...")
    
    required_files = [
        'emg_plotter_gui.py',
        'plot_emg.py',
        'launcher.py',
        'emg_plotter.spec',
        'requirements_build.txt'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            missing.append(file)
    
    return len(missing) == 0

def test_pyinstaller():
    """Test PyInstaller availability"""
    print("\nTesting PyInstaller...")
    
    try:
        result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ PyInstaller {version}")
            return True
        else:
            print("✗ PyInstaller not working")
            return False
    except Exception as e:
        print(f"✗ PyInstaller error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("EMG Plotter Build Test")
    print("=" * 50)
    
    tests = [
        ("Import test", test_imports),
        ("File test", test_files), 
        ("PyInstaller test", test_pyinstaller)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Ready to build executable.")
        print("\nRun one of these commands to build:")
        print("  .\\build_exe.ps1    (PowerShell)")
        print("  build_exe.bat      (Command Prompt)")
    else:
        print("❌ Some tests failed. Please fix issues before building.")
        print("\nTo install missing dependencies:")
        print("  python -m pip install -r requirements_build.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

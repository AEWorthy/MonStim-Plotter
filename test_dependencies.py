#!/usr/bin/env python3
"""
Test script to verify dependencies are working correctly
This can be run before building to ensure all imports work
"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    errors = []
    
    print("Testing critical imports...")
    
    # Test PyQt6
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow
        from PyQt6.QtCore import QThread, pyqtSignal, Qt
        from PyQt6.QtGui import QFont, QIcon, QColor
        print("✓ PyQt6 imports successful")
    except ImportError as e:
        errors.append(f"PyQt6 import failed: {e}")
        print(f"✗ PyQt6 import failed: {e}")
    
    # Test matplotlib
    try:
        import matplotlib
        matplotlib.use('Qt5Agg')  # Set backend
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.colors import Normalize
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        print("✓ Matplotlib imports successful")
    except ImportError as e:
        errors.append(f"Matplotlib import failed: {e}")
        print(f"✗ Matplotlib import failed: {e}")
    
    # Test PIL/Pillow
    try:
        import PIL
        from PIL import Image
        print("✓ PIL/Pillow imports successful")
    except ImportError as e:
        errors.append(f"PIL/Pillow import failed: {e}")
        print(f"✗ PIL/Pillow import failed: {e}")
    
    # Test pandas and numpy
    try:
        import pandas as pd
        import numpy as np
        print("✓ Pandas and NumPy imports successful")
    except ImportError as e:
        errors.append(f"Pandas/NumPy import failed: {e}")
        print(f"✗ Pandas/NumPy import failed: {e}")
    
    # Test our local module
    try:
        from plot_emg import plot_emg_trace
        print("✓ plot_emg module import successful")
    except ImportError as e:
        errors.append(f"plot_emg import failed: {e}")
        print(f"✗ plot_emg import failed: {e}")
    
    # Test GUI main import
    try:
        from emg_plotter_gui import main as gui_main
        print("✓ emg_plotter_gui import successful")
    except ImportError as e:
        errors.append(f"emg_plotter_gui import failed: {e}")
        print(f"✗ emg_plotter_gui import failed: {e}")
    
    return errors

def main():
    """Run all tests"""
    print("=" * 50)
    print("EMG Plotter Dependency Test")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print("")
    
    errors = test_imports()
    
    print("")
    print("=" * 50)
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
        print("")
        print("Please install missing dependencies before building.")
        return 1
    else:
        print("All imports successful! Ready to build.")
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Test script failed: {e}")
        print(traceback.format_exc())
        sys.exit(1)

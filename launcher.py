#!/usr/bin/env python3
"""
EMG Plotter GUI Launcher
Simple launcher script for the standalone executable
"""

import sys

def main():
    """Launch the EMG Plotter GUI"""
    try:
        # Import and run the GUI
        from emg_plotter_gui import main as gui_main
        return gui_main()
    except ImportError as e:
        print(f"Error importing GUI: {e}")
        input("Press Enter to exit...")
        return 1
    except Exception as e:
        print(f"Error running GUI: {e}")
        input("Press Enter to exit...")
        return 1

if __name__ == '__main__':
    sys.exit(main())

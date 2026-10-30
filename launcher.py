#!/usr/bin/env python3
"""
EMG Plotter GUI Launcher
Simple launcher script for the standalone executable
"""

import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

logger = logging.getLogger(__name__)


def show_error_dialog(title, message):
    """Show an error dialog if possible, otherwise print to stderr"""
    try:
        # Try to create a minimal QApplication for the error dialog
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception:  # noqa: BLE001
        # If GUI fails, try stderr
        try:
            print(f"ERROR: {title}\n{message}", file=sys.stderr)
        except Exception:  # noqa: BLE001
            logger.error(f"ERROR: {title}\n{message}")
            # Complete failure, nothing we can do


def main():
    """Launch the EMG Plotter GUI"""
    try:
        # Import and run the GUI
        from emg_plotter_gui import main as gui_main

        return gui_main()
    except ImportError as e:
        error_msg = f"Error importing GUI modules: {e}\n\nThis may indicate a missing dependency in the packaged executable."
        show_error_dialog("Import Error", error_msg)
        return 1
    except Exception as e:  # noqa: BLE001
        error_msg = (
            f"Error running GUI: {e}\n\nFull traceback:\n{traceback.format_exc()}"
        )
        show_error_dialog("Runtime Error", error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(main())

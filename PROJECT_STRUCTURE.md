# Project Files Overview

This document provides a quick reference for all files in the MonStim Plotter project.

## Core Application Files

| File | Purpose |
|------|---------|
| `plot_emg.py` | Core plotting functions and command-line interface |
| `emg_plotter_gui.py` | PyQt6 graphical user interface |
| `launcher.py` | Entry point for standalone executable builds |
| `example_usage.py` | Code examples and tutorials |

## Build and Distribution

| File | Purpose |
|------|---------|
| `build_exe.ps1` | PowerShell script to build Windows executable |
| `emg_plotter.spec` | PyInstaller configuration for executable building |
| `package_distribution.bat` | Script to package executable for distribution |

## Dependencies and Configuration

| File | Purpose |
|------|---------|
| `requirements_gui.txt` | Python packages needed for GUI |
| `requirements_build.txt` | Additional packages needed for building executable |
| `.gitignore` | Git version control exclusions |

## Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation and usage guide |
| `README_GUI.md` | Detailed GUI user guide |
| `README_BUILD.md` | Instructions for building standalone executable |
| `CONTRIBUTING.md` | Guidelines for contributing to the project |
| `CHANGELOG.md` | Version history and changes |
| `LICENSE` | BSD 2-Clause license terms |

## Sample Data

| File | Purpose |
|------|---------|
| `Example Data 1.csv` | Sample EMG data for testing and demonstrations |
| `Example Data 2.csv` | Additional sample EMG data |
| `Example Data 3.csv` | More sample EMG data |

## Assets and Resources

| Directory/File | Purpose |
|----------------|---------|
| `src/` | Application resources and assets |
| `src/icon.ico` | Windows application icon |
| `src/icon.png` | Application icon (PNG format) |
| `src/logo.png` | Project logo |
| `src/info.png` | Information/help icon |

## GitHub Integration

| Directory/File | Purpose |
|----------------|---------|
| `.github/workflows/ci.yml` | Automated testing configuration |
| `.github/ISSUE_TEMPLATE/` | Issue reporting templates |
| `.github/pull_request_template.md` | Pull request template |

## Generated Directories (not in version control)

| Directory | Purpose |
|-----------|---------|
| `build/` | Temporary files created during executable building |
| `dist/` | Final executable and distribution files |
| `__pycache__/` | Python bytecode cache |
| `*.egg-info/` | Python package metadata |

## Quick Start for Developers

1. **Clone the repository**
2. **Install dependencies:** `pip install -r requirements_gui.txt`
3. **Run the GUI:** `python emg_plotter_gui.py`
4. **Try the CLI:** `python plot_emg.py "Example Data 1.csv" --overlay`
5. **Build executable:** `.\build_exe.ps1` (Windows)

## File Dependencies

```
emg_plotter_gui.py → plot_emg.py (core functions)
launcher.py → emg_plotter_gui.py (for executable)
build_exe.ps1 → emg_plotter.spec → launcher.py
```

For more detailed information, see the main [README.md](README.md).

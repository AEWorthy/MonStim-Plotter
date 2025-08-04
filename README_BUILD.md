# Building EMG Plotter Executable

This guide explains how to create a standalone Windows executable for the EMG Plotter GUI that can be distributed to users without requiring Python installation.

## Prerequisites

- Python 3.8 or later installed on your Windows system
- All project files in the current directory

## Quick Build (Recommended)

### Using PowerShell (Recommended)
1. Open PowerShell in the project directory
2. Run: `.\build_exe.ps1`
3. Follow the prompts


## Manual Build Steps

If you prefer to build manually or the scripts don't work:

1. **Install build dependencies:**
   ```
   python -m pip install -r requirements_build.txt
   ```

2. **Clean previous builds:**
   ```
   rmdir /s build dist __pycache__ 2>nul
   ```

3. **Build the executable:**
   ```
   python -m PyInstaller emg_plotter.spec --clean
   ```

4. **Find your executable:**
   The finished executable will be at `dist\EMG_Plotter.exe`

## Build Configuration

The build is configured through `emg_plotter.spec` with these settings:

- **Main script**: `launcher.py` (simple entry point)
- **Name**: `EMG_Plotter.exe`
- **Mode**: Windowed application (no console)
- **Includes**: All CSV sample data files
- **Size optimization**: UPX compression enabled

## What Gets Included

The executable automatically includes:
- All Python dependencies (PyQt6, matplotlib, pandas, numpy)
- Sample CSV files (`pretty waveform 1.csv`, `pretty waveform 2.csv`)
- CA26 Project CSV files (if present)
- README files

## Distribution

The resulting `EMG_Plotter.exe` file can be:
- Copied to any Windows 10/11 computer
- Run without installing Python or any dependencies
- Distributed via email, USB drive, network share, etc.

## Troubleshooting

**Build fails with "PyInstaller not found":**
- Run: `python -m pip install pyinstaller`

**Executable won't start:**
- Try building with `console=True` in the spec file for debugging
- Check that all required files are in the same directory structure

**Large file size:**
- The exe will be 100-200MB due to included libraries
- This is normal for PyInstaller builds with GUI frameworks

**Missing data files:**
- Sample CSV files are embedded in the executable
- Users can still load their own CSV files through the GUI

## File Sizes

Typical file sizes:
- Source code: ~50KB
- Built executable: ~150-200MB (includes Python runtime + all libraries)

## Support

The executable includes the same functionality as the Python version:
- GUI interface for EMG plotting
- CSV file loading and processing  
- Plot customization options
- Export capabilities

For technical issues with the executable, users should contact the developer.

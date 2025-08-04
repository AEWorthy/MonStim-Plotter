# Building EMG Plotter Executable

This guide explains how to create a standalone Windows executable for the EMG Plotter GUI. The resulting executable can be distributed to users without requiring them to install Python or any dependencies.

## Prerequisites

- Windows 10 or later
- Python 3.8 or later installed and accessible from command line
- All project files in the current directory

## Quick Build (Recommended)

### Using PowerShell
1. Open PowerShell in the project directory
2. Run the build script:
   ```powershell
   .\build_exe.ps1
   ```
3. Follow any prompts that appear
4. Find your executable at `dist\MonStim Plotter.exe`


## Manual Build Process

If you prefer to build manually or need to troubleshoot:

1. **Install build dependencies:**
   ```powershell
   python -m pip install -r requirements_build.txt
   ```

2. **Clean previous builds:**
   ```powershell
   if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
   if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
   ```

3. **Build the executable:**
   ```powershell
   python -m PyInstaller emg_plotter.spec --clean
   ```

4. **Locate your executable:**
   The finished executable will be at `dist\MonStim Plotter.exe`

## Build Configuration Details

The build process is configured through `emg_plotter.spec` with these settings:

- **Entry Point**: `launcher.py` (lightweight startup script)
- **Output Name**: `MonStim Plotter.exe`
- **Window Mode**: GUI application (no console window)
- **Included Data**: All sample CSV files and documentation
- **Optimization**: UPX compression for smaller file size
- **Icon**: Custom application icon from `src/icon.ico`

## What Gets Packaged

The executable automatically includes:
- **Python Runtime**: Complete Python environment
- **Required Libraries**: PyQt6, matplotlib, pandas, numpy, and dependencies
- **Sample Data**: Example CSV files for immediate testing
- **Documentation**: README files converted to text format
- **Resources**: Application icons and images

## Distribution Information

The resulting `MonStim Plotter.exe` file:
- **Size**: Approximately 150-200MB (includes full Python runtime)
- **Compatibility**: Windows 10/11 (64-bit)
- **Dependencies**: None - completely standalone
- **Installation**: Simply copy the executable to any Windows computer

## Troubleshooting Build Issues

**"PyInstaller not found" error:**
- Solution: `python -m pip install pyinstaller`

**Build fails with import errors:**
- Ensure all dependencies are installed: `pip install -r requirements_build.txt`
- Try clearing Python cache: `python -m pip cache purge`

**Executable won't start:**
- For debugging, temporarily change `console=False` to `console=True` in `emg_plotter.spec`
- Check Windows Event Viewer for detailed error information

**Antivirus software blocks executable:**
- This is common with PyInstaller executables
- Add the `dist` folder to your antivirus exclusions during development
- Users may need to mark the executable as safe

**Large file size concerns:**
- The 150-200MB size is normal for PyInstaller builds with GUI frameworks
- Size includes complete Python runtime and all scientific computing libraries
- Cannot be significantly reduced without removing functionality

## Performance Notes

**Startup Time:**
- First launch may be slower (2-5 seconds) as Windows prepares the executable
- Subsequent launches are typically faster

**Memory Usage:**
- Expect 50-100MB RAM usage when running
- Memory usage scales with data file size

**Compatibility:**
- Built on Windows 10/11 for maximum compatibility
- Should work on Windows 7 SP1 with platform updates, but not officially supported

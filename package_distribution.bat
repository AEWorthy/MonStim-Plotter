
@echo off
REM Distribution packaging script for EMG Plotter
REM Creates a zip file with the executable and documentation

echo ================================================
echo Creating EMG Plotter Distribution Package
echo ================================================

REM Check if executable exists
if not exist "dist\MonStim Plotter.exe" (
    echo ERROR: Executable not found at 'dist\MonStim Plotter.exe'
    echo Please run build_exe.bat first to create the executable
    pause
    exit /b 1
)

REM Create distribution directory
set DIST_NAME="dist\MonStim_Plotter_v1.0_Windows"
if exist "%DIST_NAME%" rmdir /s /q "%DIST_NAME%"
mkdir "%DIST_NAME%"

REM Copy executable
echo Copying executable...
copy "dist\MonStim Plotter.exe" "%DIST_NAME%\"

REM Copy documentation
echo Copying documentation...
copy "README.md" "%DIST_NAME%\README.txt"
copy "README_GUI.md" "%DIST_NAME%\GUI_Guide.txt"
copy "LICENSE" "%DIST_NAME%\LICENSE.txt"
if exist "CONTRIBUTING.md" copy "CONTRIBUTING.md" "%DIST_NAME%\CONTRIBUTING.txt"

REM Copy sample data
echo Copying sample data...
if exist "Example Data 1.csv" copy "Example Data 1.csv" "%DIST_NAME%\"
if exist "Example Data 2.csv" copy "Example Data 2.csv" "%DIST_NAME%\"
if exist "Example Data 3.csv" copy "Example Data 3.csv" "%DIST_NAME%\"

REM Create a simple instructions file
echo Creating user instructions...
(
echo MonStim Plotter - Standalone Windows Application
echo ===============================================
echo.
echo Created by: Andrew Worthy
echo Version: 1.0
echo License: BSD 2-Clause License ^(see LICENSE.txt^)
echo.
echo This is a standalone version of MonStim Plotter that doesn't require Python installation.
echo.
echo TO GET STARTED:
echo   1. Double-click 'MonStim Plotter.exe' to launch the application
echo   2. Click "Browse CSV File..." to load your EMG data
echo   3. Use the sample data files to test the application
echo.
echo SAMPLE DATA FILES:
echo   - Example Data 1.csv
echo   - Example Data 2.csv
echo   - Example Data 3.csv
echo.
echo DOCUMENTATION:
echo   - GUI_Guide.txt - Step-by-step user guide for the interface
echo   - README.txt - Complete project documentation and features
echo   - LICENSE.txt - Software license terms and conditions
echo   - CONTRIBUTING.txt - Guidelines for contributing to the project
echo.
echo SYSTEM REQUIREMENTS:
echo   - Windows 10 or later ^(64-bit^)
echo   - No Python or additional software installation required
echo   - Minimum 4GB RAM recommended for large datasets
echo.
echo GETTING HELP:
echo   - For user questions: Check GUI_Guide.txt and README.txt
echo   - For bug reports: Visit https://github.com/AEWorthy/Monstim-Plotter/issues
echo   - For feature requests: Open an issue on GitHub
echo   - Source code: https://github.com/AEWorthy/Monstim-Plotter
echo.
echo TROUBLESHOOTING:
echo   - If the program won't start, check Windows Event Viewer
echo   - Antivirus software may flag the executable - add it to exclusions
echo   - For CSV loading issues, ensure your file matches MonStim Analysis format

echo.
echo Thank you for using MonStim Plotter!

) > "%DIST_NAME%\START_HERE.txt"

REM Create zip file if possible
where powershell >nul 2>&1
if %errorlevel% equ 0 (
    echo Creating zip file...
    powershell -Command "Compress-Archive -Path '%DIST_NAME%' -DestinationPath '%DIST_NAME%.zip' -Force"
    if exist "%DIST_NAME%.zip" (
        echo ✓ Created %DIST_NAME%.zip
    )
) else (
    echo PowerShell not available - zip file not created
    echo You can manually zip the %DIST_NAME% folder
)

echo ================================================
echo Distribution package created successfully!
echo ================================================
echo.
echo Files created:
echo   - %DIST_NAME%\ (folder with all files)
if exist "%DIST_NAME%.zip" (
echo   - %DIST_NAME%.zip (ready to distribute)
)
echo.
echo The package contains:
echo   - MonStim Plotter.exe (main application)
echo   - Sample CSV files for testing
echo   - Complete documentation and license
echo   - User instructions and troubleshooting guide
echo.
echo This package can be distributed to Windows users who want to use
echo MonStim Plotter without installing Python or any dependencies.
echo.
echo Users will have access to:
echo   ✓ Complete standalone application
echo   ✓ Sample data for immediate testing
echo   ✓ Comprehensive documentation
echo   ✓ License information and terms
echo   ✓ Direct links for support and bug reporting
echo.
pause

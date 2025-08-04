
@echo off
REM Distribution packaging script for EMG Plotter
REM Creates a zip file with the executable and documentation

echo ================================================
echo Creating EMG Plotter Distribution Package
echo ================================================

REM Check if executable exists
if not exist "dist\EMG_Plotter.exe" (
    echo ERROR: Executable not found at dist\EMG_Plotter.exe
    echo Please run build_exe.bat first to create the executable
    pause
    exit /b 1
)

REM Create distribution directory
set DIST_NAME="dist\EMG_Plotter_v1.0_Windows"
if exist "%DIST_NAME%" rmdir /s /q "%DIST_NAME%"
mkdir "%DIST_NAME%"

REM Copy executable
echo Copying executable...
copy "dist\EMG_Plotter.exe" "%DIST_NAME%\"

REM Copy documentation
echo Copying documentation...
copy "README.md" "%DIST_NAME%\README.txt"
copy "README_GUI.md" "%DIST_NAME%\GUI_Guide.txt"

REM Copy sample data
echo Copying sample data...
if exist "Example Data 1.csv" copy "Example Data 1.csv" "%DIST_NAME%\"
if exist "Example Data 2.csv" copy "Example Data 2.csv" "%DIST_NAME%\"
if exist "Example Data 3.csv" copy "Example Data 3.csv" "%DIST_NAME%\"

REM Create a simple instructions file
echo Creating user instructions...
(
echo EMG Plotter - Standalone Windows Application
echo ============================================
echo.
echo This is a standalone version of EMG Plotter that doesn't require Python installation.
echo.
echo TO RUN:
echo   Double-click EMG_Plotter.exe
echo.
echo SAMPLE DATA:
echo   - Example Data 1.csv
echo   - Example Data 2.csv
echo   - Example Data 3.csv
echo.
echo HELP:
echo   - See GUI_Guide.txt for detailed instructions
echo   - See README.txt for general information about the project
echo.
echo SYSTEM REQUIREMENTS:
echo   - Windows 10 or later
echo   - No additional software required
echo.
echo For support or source code, visit:
echo https://github.com/AEWorthy/Pretty-EMG
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
echo   - EMG_Plotter.exe (main application)
echo   - Sample CSV files
echo   - Documentation and instructions
echo.
echo This package can be distributed to Windows users who want to use
echo EMG Plotter without installing Python.
echo.
pause

# Build script for EMG Plotter GUI executable (PowerShell version)
# This script builds a standalone Windows executable using PyInstaller

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Building EMG Plotter GUI Executable" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or later" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Checking and installing dependencies..." -ForegroundColor Yellow

# Install/upgrade PyInstaller and dependencies
try {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install -r requirements_build.txt
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean up previous builds
Write-Host "Cleaning up previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow
try {
    python -m PyInstaller emg_plotter.spec --clean
    
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed"
    }
} catch {
    Write-Host "✗ ERROR: Build failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "================================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your executable is located at: dist\MonStim Plotter.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now distribute this executable to other Windows users." -ForegroundColor White
Write-Host "They don't need Python or any other dependencies installed." -ForegroundColor White
Write-Host ""

# Check if executable was created
if (Test-Path "dist\MonStim Plotter.exe") {
    $fileInfo = Get-Item "dist\MonStim Plotter.exe"
    Write-Host "✓ Executable created successfully" -ForegroundColor Green
    Write-Host "File size: $([Math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "⚠ WARNING: Executable was not found at expected location" -ForegroundColor Yellow
}
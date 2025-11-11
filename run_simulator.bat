@echo off
REM Launcher script for Enhanced Economic Dispatch Simulator (Windows)

echo ========================================================================
echo       Enhanced Economic Dispatch Simulator - Launcher (Windows)
echo ========================================================================
echo.
echo Checking dependencies...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)
echo [OK] Python found

REM Check and install numpy if needed
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [INFO] NumPy not found. Installing...
    pip install numpy
)
echo [OK] NumPy installed

REM Check and install matplotlib if needed
python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Matplotlib not found. Installing...
    pip install matplotlib
)
echo [OK] Matplotlib installed

echo.
echo Starting Enhanced Economic Dispatch Simulator...
echo ========================================================================
echo.

REM Run the enhanced simulator
python economic_dispatch_simulator_enhanced.py

echo.
echo Simulator closed.
pause

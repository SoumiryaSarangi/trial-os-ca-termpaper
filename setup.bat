@echo off
REM Setup script for Deadlock Detective on Windows

echo ========================================
echo Deadlock Detective - Setup Script
echo ========================================
echo.

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

echo Step 2: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

echo Step 3: Running tests...
pytest tests/ -v
if errorlevel 1 (
    echo WARNING: Some tests failed. Check output above.
    echo Application may still work, but verify functionality.
) else (
    echo All tests passed!
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo   python app.py
echo.
echo Or double-click: run.bat
echo.
pause

@echo off
REM Quick launcher for Deadlock Detective

echo Starting Deadlock Detective...
python app.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application!
    echo.
    echo Troubleshooting:
    echo 1. Make sure dependencies are installed: setup.bat
    echo 2. Check Python installation: python --version
    echo 3. Try: python app.py
    echo.
    pause
)

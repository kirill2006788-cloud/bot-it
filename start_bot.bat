@echo off
chcp 65001 >nul
echo ========================================
echo    IT Helper Bot - Auto Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python from https://python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Go to bot directory
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM Check bot file
if not exist "run_bot.py" (
    echo ERROR: run_bot.py not found!
    echo Make sure you are in the correct directory
    pause
    exit /b 1
)

echo Starting bot...
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Start bot
python run_bot.py

REM If bot ended with error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Bot ended with error!
    echo Check logs above for diagnostics
    echo ========================================
    pause
) else (
    echo.
    echo ========================================
    echo Bot ended normally
    echo ========================================
    pause
)

@echo off
chcp 65001 >nul
echo ========================================
echo    IT Helper Bot - Stop
echo ========================================
echo.

echo Stopping all Python processes...
taskkill /f /im python.exe >nul 2>&1

if errorlevel 1 (
    echo Python processes not found or already stopped
) else (
    echo All Python processes stopped
)

echo.
echo ========================================
echo Stop completed
echo ========================================
pause

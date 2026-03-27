@echo off
chcp 65001 >nul
echo ========================================
echo    IT Helper Bot - Restart
echo ========================================
echo.

echo Stopping bot...
taskkill /f /im python.exe >nul 2>&1

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo Starting bot again...
echo.

REM Go to bot directory
cd /d "%~dp0"

REM Start bot
python run_bot.py

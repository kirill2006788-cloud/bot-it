@echo off
chcp 65001 >nul
cls
echo ========================================
echo    IT Helper Bot - Zapusk
echo ========================================
echo.
echo Zapuskaem bota...
echo Dlya ostanovki nazhmite Ctrl+C
echo.
echo ========================================
echo.
cd /d "%~dp0"
python run_bot.py
pause

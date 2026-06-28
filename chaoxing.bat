@echo off
cd /d D:\Code\Python\ChaoXingLibrarySeatReservation-main
"D:\Users\CY\anaconda3\python.exe" main.py >> run_log.txt 2>&1
taskkill /f /im python.exe >nul 2>&1
shutdown /s /t 0
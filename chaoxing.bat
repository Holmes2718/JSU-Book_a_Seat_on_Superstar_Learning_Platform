@echo off
cd 你的\ChaoXingLibrarySeatReservation-main路径
"改为你的python.exe路径" main.py >> run_log.txt 2>&1
taskkill /f /im python.exe >nul 2>&1
shutdown /s /t 0  # 我这里是自动关机了，需要什么自己修改
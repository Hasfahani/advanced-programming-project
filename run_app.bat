@echo off
echo Starting Media Library...
cd /d "C:\final advanced programming"
start /min "" python backend\app.py
timeout /t 2 >nul
python frontend\main_advanced.py

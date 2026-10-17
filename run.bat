@echo off
title discord-server-cloner
color 0f

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet --disable-pip-version-check
python main.py

pause

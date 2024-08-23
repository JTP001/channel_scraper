@echo off
cd /d %~dp0

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
python channel_scraper.py

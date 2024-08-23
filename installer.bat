@echo off
cd /d %~dp0

REM Create the virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install the required packages
pip install --upgrade google-api-python-client
pip install --upgrade google-auth
pip install --upgrade google-auth-oauthlib

REM Check if api_key.json exists
if not exist api_key.json (
    echo The file api_key.json does not exist. 
    echo Please copy your API key from your Google API project and create api_key.json in the format {"api_key":"your_api_key"} in this directory.
    exit /b 1
)

REM Check if client_secret.json exists
if not exist client_secret.json (
    echo The file client_secret.json does not exist. 
    echo Please download it from your Google API project and insert it in this directory.
    exit /b 1
)

REM call run.bat
call run.bat

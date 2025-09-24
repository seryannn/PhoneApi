@echo off
title PhoneApi Setup
echo ===============================
echo   PhoneApi Setup Script
echo ===============================
echo.


python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b
)


echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat


echo Upgrading pip...
python -m pip install --upgrade pip


echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ===============================
echo   Setup complete!
echo   To activate your environment later:
echo   call .venv\Scripts\activate.bat
echo   Then run PhoneApi: python phoneapi.py
echo ===============================
pause

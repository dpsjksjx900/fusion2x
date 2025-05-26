@echo off
REM =============================
REM Fusion2X One-Click Launcher (with isolated venv)
REM =============================

SET VENV_DIR=.venv

REM 1. Check if venv exists, if not, create it
IF NOT EXIST %VENV_DIR%\Scripts\python.exe (
    echo Creating new Python virtual environment in %VENV_DIR%
    python -m venv %VENV_DIR%
)

REM 2. Upgrade pip
call %VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip

REM 3. Install requirements
call %VENV_DIR%\Scripts\python.exe -m pip install -r requirements.txt

REM 4. Install models and FFmpeg using the venv Python
call %VENV_DIR%\Scripts\python.exe setup_models_windows.py

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Model setup failed. Please check logs\install.log and fix any issues.
    pause
    exit /b %ERRORLEVEL%
)

REM 5. Start the GUI using the venv Python
call %VENV_DIR%\Scripts\python.exe gui.py

pause

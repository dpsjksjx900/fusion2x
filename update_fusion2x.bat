@echo off
REM Ensure git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo git is not installed. Please install git and try again.
    exit /b 1
)


REM Pull latest code or clone if missing
set REPO_URL=https://github.com/dpsjksjx900/fusion2x.git
if not exist .git (
    echo Cloning Fusion2X repository...
    git init
    git remote add origin %REPO_URL%
    git fetch origin
    git checkout -f origin/main
) else (
    git pull --ff-only origin main
    if %ERRORLEVEL% NEQ 0 git pull --ff-only
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to pull latest code.
        exit /b %ERRORLEVEL%
    )

)

REM Update Python dependencies
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo Fusion2X is up to date.

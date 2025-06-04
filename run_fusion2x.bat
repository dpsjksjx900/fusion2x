@echo off
REM 1. Create or activate virtualenv
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

REM 2. Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM 3. Ensure logs folder exists
if not exist logs (
    mkdir logs
)

REM 4. Run the Python entrypoint
python gui.py

REM 5. Pause so you can read any errors
pause

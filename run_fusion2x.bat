@echo off
REM 1. Create or activate virtualenv
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

REM 2. Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM 3. Install models if missing
if not exist models (
    echo Models not found. Running model setup...
    python setup_models_windows.py
)

REM 4. Ensure logs folder exists
if not exist logs (
    mkdir logs
)

REM 5. Run the Python entrypoint
python gui.py

REM 6. Pause so you can read any errors
pause

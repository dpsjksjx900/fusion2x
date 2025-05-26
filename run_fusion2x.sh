#!/bin/bash
VENV_DIR=".venv"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Creating new Python virtual environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt
"$VENV_DIR/bin/python" setup_models_windows.py  # Replace if you have a cross-platform installer
"$VENV_DIR/bin/python" gui.py

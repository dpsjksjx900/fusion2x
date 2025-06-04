#!/usr/bin/env bash
set -e

# 1. Create or activate virtualenv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Ensure logs folder exists
mkdir -p logs

# 4. Run the Python entrypoint
python gui.py


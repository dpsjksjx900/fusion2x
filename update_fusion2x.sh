#!/usr/bin/env bash
set -e

# Ensure git is installed
if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed. Please install git and try again."
  exit 1
fi

# Pull latest code from the configured remote
git pull

# Update Python dependencies
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Fusion2X is up to date."

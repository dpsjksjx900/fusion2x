#!/usr/bin/env bash
set -e

# Ensure git is installed
if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed. Please install git and try again."
  exit 1
fi


# Pull latest code from the configured remote or clone if missing
REPO_URL="https://github.com/dpsjksjx900/fusion2x.git"
if [ ! -d ".git" ]; then
  echo "Cloning Fusion2X repository..."
  git init
  git remote add origin "$REPO_URL"
  git fetch origin
  git checkout -f origin/main
else
  git pull --ff-only origin main || git pull --ff-only
fi


# Update Python dependencies
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Fusion2X is up to date."

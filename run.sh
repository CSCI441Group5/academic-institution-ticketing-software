#!/usr/bin/env bash
set -e

# Resolve repository root (this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  echo "Missing .venv. Create it first: python3 -m venv .venv"
  exit 1
fi

# Activate the virtual environment and run the app
source .venv/bin/activate
python run.py

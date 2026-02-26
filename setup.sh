#!/usr/bin/env bash
set -e

# Resolve repository root (this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment once if it does not exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Install project dependencies into the local virtual environment
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Setup complete. Run the app with: ./run.sh"

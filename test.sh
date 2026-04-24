#!/usr/bin/env bash
set -e

# Resolve repository root (this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  echo "Missing .venv. Create it first: ./setup.sh"
  exit 1
fi

# Run the pytest tests using the project's virtual environment
.venv/bin/python -m pytest "$@"

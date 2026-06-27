#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-backup-passwords"
REQ_FILE="$SCRIPT_DIR/requirements.txt"
PY_SCRIPT="$SCRIPT_DIR/backup_apple_passwords.py"

if [ ! -f "$PY_SCRIPT" ]; then
  echo "Missing: $PY_SCRIPT" >&2
  exit 1
fi

if [ ! -f "$REQ_FILE" ]; then
  echo "Missing: $REQ_FILE" >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r "$REQ_FILE"

python3 "$PY_SCRIPT"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/backup_apple_contacts.py"

if [ ! -f "$PY_SCRIPT" ]; then
  echo "Missing: $PY_SCRIPT" >&2
  exit 1
fi

python3 "$PY_SCRIPT"

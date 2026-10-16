#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-backup-passwords"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

ensure_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
  fi
  source "$VENV_DIR/bin/activate"
  python -m pip install --quiet --upgrade pip
  python -m pip install --quiet -r "$REQ_FILE"
}

run_contacts() {
  echo ""
  echo "--- Apple Contacts Backup ---"
  python3 "$SCRIPT_DIR/backup_apple_contacts.py"
}

run_passwords() {
  echo ""
  echo "--- Apple Passwords Backup ---"
  echo "Prerequisite: export your passwords from Apple Passwords first."
  echo "  Apple Passwords > File > Export Passwords..."
  echo "  Save as: ~/Downloads/Passwords.csv"
  echo ""
  read -r -p "Ready to continue? [y/N] " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Skipping passwords backup."
    return
  fi
  ensure_venv
  python3 "$SCRIPT_DIR/backup_apple_passwords.py"
}

run_rmpp() {
  echo ""
  echo "--- reMarkable Paper Pro Backup ---"
  echo "Prerequisites:"
  echo "  1. Connect the reMarkable Paper Pro to this computer via USB."
  echo "  2. Passwordless 'ssh rmpp' must work."
  echo ""
  read -r -p "Ready to continue? [y/N] " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Skipping reMarkable backup."
    return
  fi
  python3 "$SCRIPT_DIR/backup_rmpp.py"
}

print_menu() {
  echo ""
  echo "Backups"
  echo "  1) Apple Contacts"
  echo "  2) Apple Passwords  (requires manual CSV export first)"
  echo "  3) reMarkable Paper Pro  (requires USB + SSH access)"
  echo "  4) All of the above"
  echo "  q) Quit"
  echo ""
}

print_menu
read -r -p "Choice: " choice

case "$choice" in
  1) run_contacts ;;
  2) run_passwords ;;
  3) run_rmpp ;;
  4)
    run_contacts
    run_passwords
    run_rmpp
    ;;
  q|Q)
    echo "Bye."
    exit 0
    ;;
  *)
    echo "Invalid choice: $choice" >&2
    exit 1
    ;;
esac

echo ""
echo "Done."

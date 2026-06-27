#!/usr/bin/env python3
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from backup_utils import cleanup_old_backups
from backup_utils import cleanup_tmp_dir
from backup_utils import create_zip_archive

FINAL_DIR = Path("/Volumes/external/Backups/Contacts")
TMP_DIR = Path("backup_tmp")


def export_contacts(out_dir):
    """Execute AppleScript to export contacts to specified directory."""
    script_path = Path(__file__).parent / "export-contacts.applescript"

    try:
        result = subprocess.run(
            ["osascript", str(script_path), out_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Contacts exported to {out_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def backup():
    """Backup contacts from macOS Address Book to zip archive."""
    stamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = Path.cwd() / f"contacts-{stamp}.zip"

    cleanup_tmp_dir(TMP_DIR)
    TMP_DIR.mkdir()

    try:
        if export_contacts(TMP_DIR):
            create_zip_archive(TMP_DIR, zip_path)
            shutil.move(str(zip_path), str(FINAL_DIR / zip_path.name))
            print(f"Created {zip_path.name}")
    finally:
        cleanup_tmp_dir(TMP_DIR)


if __name__ == "__main__":
    backup()
    cleanup_old_backups(backup_dir=FINAL_DIR)

#!/usr/bin/env python3
import subprocess, shutil, os
from pathlib import Path
from datetime import datetime

from backup_utils import create_zip_archive, cleanup_old_backups

FINAL_DIR = Path("/Volumes/external/Backups/Contacts")


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
    stamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = Path.cwd() / f"contacts-{stamp}.zip"

    out_dir = Path("backup_tmp")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    if export_contacts(out_dir):
        create_zip_archive(out_dir, zip_path)

        shutil.move(zip_path, FINAL_DIR / zip_path.name)

        shutil.rmtree(out_dir)
        print(f"Created {zip_path.name}")


if __name__ == "__main__":
    backup()
    cleanup_old_backups(FINAL_DIR)

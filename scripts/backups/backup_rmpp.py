#!/usr/bin/env python3
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from backup_utils import cleanup_old_backups
from backup_utils import cleanup_tmp_dir
from backup_utils import create_zip_archive

HOST = "rmpp"  # ssh config alias
REMOTE_DIR = "/home/root/.local/share/remarkable/xochitl"
FINAL_DIR = Path("/Volumes/Transient Backups - 2026/reMarkable")
TMP_DIR = Path("backup_tmp")

# Make sure the reMarkable Paper Pro is connected to the computer via USB.
# Requires `ssh rmpp` to work without a password (SSH key + ~/.ssh/config alias).
# To restore: unzip, then scp the contents back into REMOTE_DIR and restart xochitl.


def backup():
    """Copy the raw xochitl document directory from the device and zip it."""
    stamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = Path.cwd() / f"rmpp-{stamp}.zip"

    cleanup_tmp_dir(TMP_DIR)
    TMP_DIR.mkdir()

    try:
        print(f"Copying {HOST}:{REMOTE_DIR}")
        # -O forces the legacy scp protocol, which the device's SSH server supports.
        subprocess.run(
            ["scp", "-O", "-r", f"{HOST}:{REMOTE_DIR}", str(TMP_DIR)],
            check=True,
        )

        create_zip_archive(TMP_DIR, zip_path)
        shutil.move(str(zip_path), str(FINAL_DIR / zip_path.name))
        print(f"Created {zip_path.name}")
    finally:
        cleanup_tmp_dir(TMP_DIR)


if __name__ == "__main__":
    backup()
    cleanup_old_backups(backup_dir=FINAL_DIR)

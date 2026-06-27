#!/usr/bin/env python3
import json
import shutil
import urllib.request
from datetime import datetime
from pathlib import Path

from backup_utils import cleanup_old_backups
from backup_utils import cleanup_tmp_dir
from backup_utils import create_zip_archive

HOST = "http://10.11.99.1"
HDR = {"Accept": "*/*"}
FINAL_DIR = Path("/Volumes/external/Backups/reMarkable")
TMP_DIR = Path("backup_tmp")

# Make sure the reMarkable Paper Pro is connected to the computer via USB.
# Go to Settings > Storage > Enable USB web interface.


def get(url):
    """Fetch JSON from the reMarkable device."""
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def walk_docs(base_id=""):
    """Recursively yield document IDs, names, and folder status."""
    for item in get(f"{HOST}/documents/{base_id}"):
        yield item["ID"], item["VissibleName"], item["Type"] == "CollectionType"
        if item["Type"] == "CollectionType":
            yield from walk_docs(item["ID"])


def backup(target_names=("Personal", "Work")):
    """Backup documents from reMarkable device."""
    stamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = Path.cwd() / f"rmpp-{stamp}.zip"

    cleanup_tmp_dir(TMP_DIR)
    TMP_DIR.mkdir()

    try:
        folders = {name: None for name in target_names}
        for uid, name, is_folder in walk_docs():
            if is_folder and name in folders:
                folders[name] = uid

        for folder_name, folder_id in folders.items():
            if folder_id is None:
                print(f"Folder '{folder_name}' not found")
                continue
            for uid, name, is_folder in walk_docs(folder_id):
                if is_folder:
                    continue
                dest = TMP_DIR / folder_name / f"{name}.rmdoc"
                dest.parent.mkdir(parents=True, exist_ok=True)
                print(f"Downloading {dest}")
                urllib.request.urlretrieve(f"{HOST}/download/{uid}/rmdoc", str(dest))

        create_zip_archive(TMP_DIR, zip_path)
        shutil.move(str(zip_path), str(FINAL_DIR / zip_path.name))
        print(f"Created {zip_path.name}")
    finally:
        cleanup_tmp_dir(TMP_DIR)


if __name__ == "__main__":
    backup()
    cleanup_old_backups(backup_dir=FINAL_DIR)

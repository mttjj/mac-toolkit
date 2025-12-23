#!/usr/bin/env python3
import urllib.request, json, shutil
from pathlib import Path
from datetime import datetime

from backup_utils import create_zip_archive, cleanup_old_backups

HOST = "http://10.11.99.1"
HDR = {"Accept": "*/*"}

"""
Make sure the reMarkable Paper Pro is connected to the computer via USB. Go to Settings > Storage > Enable USB web interface.
"""


def get(url):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def walk_docs(base_id=""):
    for item in get(f"{HOST}/documents/{base_id}"):
        yield item["ID"], item["VissibleName"], item["Type"] == "CollectionType"
        if item["Type"] == "CollectionType":
            yield from walk_docs(item["ID"])


def backup(target_names=("Personal", "Work")):
    stamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = Path(__file__).resolve().parent / f"rmpp backup {stamp}.zip"
    out_dir = Path("backup_tmp")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

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
            dest = out_dir / folder_name / f"{name}.rmdoc"
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"Downloading {dest}")
            urllib.request.urlretrieve(f"{HOST}/download/{uid}/rmdoc", str(dest))

    create_zip_archive(out_dir, zip_path)

    # Clean up temporary directory
    shutil.rmtree(out_dir)
    print(f"Created {zip_path.name}")


if __name__ == "__main__":
    backup()
    cleanup_old_backups()

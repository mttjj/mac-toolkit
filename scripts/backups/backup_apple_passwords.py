#!/usr/bin/env python3
import csv
import getpass
import os
import shutil
from datetime import datetime
from pathlib import Path

from pykeepass import create_database
from backup_utils import cleanup_old_backups


CSV_PATH = Path("~/Downloads/Passwords.csv").expanduser()
FINAL_DIR = Path("/Volumes/external/Backups/Passwords")

KDBX_PASSWORD_ENV = "KDBX_PASSWORD"


def norm(x):
    return "" if x is None else str(x).strip()


def load_rows(csv_file: Path):
    with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        expected = ["Title", "URL", "Username", "Password", "Notes"]
        missing = [c for c in expected if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"CSV missing columns {missing}. Found: {reader.fieldnames}")

        rows = []
        for row in reader:
            title = norm(row.get("Title"))
            url = norm(row.get("URL"))
            username = norm(row.get("Username"))
            if not username:
                username = '<no username>'
            password = norm(row.get("Password"))
            notes = norm(row.get("Notes"))

            if not (title or url or username or password or notes):
                continue

            rows.append((title, url, username, password, notes))

    title_counts = {}
    for title, _, _, _, _ in rows:
        if title:
            title_counts[title] = title_counts.get(title, 0) + 1

    title_indices = {}
    for title, url, username, password, notes in rows:
        if title and title_counts[title] > 1:
            title_indices[title] = title_indices.get(title, 0) + 1
            unique_title = f"{title}_{title_indices[title]}"
        else:
            unique_title = title
        yield unique_title, url, username, password, notes


def backup():
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        raise SystemExit(f"Apple Passwords CSV not found: {CSV_PATH}")

    kdbx_password = os.environ.get(KDBX_PASSWORD_ENV, "").strip()
    if not kdbx_password:
        kdbx_password = getpass.getpass("KDBX database password: ")

    stamp = datetime.now().strftime("%Y-%m-%d")

    out_dir = Path("backup_tmp")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    try:
        out_kdbx = out_dir / "apple-passwords.kdbx"

        kp = create_database(filename=str(out_kdbx), password=kdbx_password)
        root = kp.root_group

        for title, url, username, password, notes in load_rows(CSV_PATH):
            kp.add_entry(
                destination_group=root,
                title=(title or url or username or "Imported entry"),
                username=username or None,
                password=password or None,
                url=url or None,
                notes=notes or None,
            )

        kp.save()

        final_kdbx = FINAL_DIR / f"apple-passwords_{stamp}.kdbx"
        shutil.move(str(out_kdbx), str(final_kdbx))
        print(f"Created {final_kdbx.name}")

        # Always delete plaintext CSV
        CSV_PATH.unlink()
        print("Deleted exported CSV.")

    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


if __name__ == "__main__":
    backup()
    cleanup_old_backups(backup_dir=FINAL_DIR, file_ext=".kdbx")

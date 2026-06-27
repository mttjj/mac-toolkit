import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path


def cleanup_tmp_dir(tmp_dir=None):
    """Remove temporary backup directory."""
    if tmp_dir is None:
        tmp_dir = Path("backup_tmp")
    else:
        tmp_dir = Path(tmp_dir)

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)


def create_zip_archive(source_dir, zip_path):
    """Create a zip archive from the given source directory."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(source_dir):
            for f in files:
                full = Path(root) / f
                zf.write(full, full.relative_to(source_dir))


def cleanup_old_backups(backup_dir=None, max_age_days=30, file_ext=".zip"):
    """Delete backup files older than max_age_days."""
    if backup_dir is None:
        backup_dir = Path(__file__).resolve().parent
    else:
        backup_dir = Path(backup_dir)

    if not file_ext.startswith("."):
        file_ext = "." + file_ext

    cutoff = datetime.now() - timedelta(days=max_age_days)
    for file_path in backup_dir.glob(f"*{file_ext}"):
        if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff:
            file_path.unlink()
            print(f"Deleted {file_path.name}")

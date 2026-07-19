#!/usr/bin/env python3
"""
jpegs_to_cbz.py — Pack folders of original JPG images into CBZ files.
No re-encoding — images are stored as-is.

Usage:
    python3 jpegs_to_cbz.py /Volumes/external/Books/Comics --dry-run
    python3 jpegs_to_cbz.py /Volumes/external/Books/Comics
"""

import argparse
import zipfile
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg"}


def find_image_folders(root: Path) -> list[Path]:
    """
    Find folders that contain image files directly.
    Each such folder becomes one CBZ.
    """
    image_folders = []
    for p in sorted(root.rglob("*")):
        if not p.is_dir():
            continue
        # Does this folder contain images directly (not just subfolders)?
        has_images = any(
            child.is_file() and child.suffix.lower() in IMAGE_EXTS
            for child in p.iterdir()
        )
        if has_images:
            image_folders.append(p)
    return image_folders


def images_to_cbz(folder: Path, root: Path, delete_original: bool = True) -> bool:
    """Pack all images in a folder into a CBZ. Returns True on success."""
    # CBZ name = folder name, placed alongside the folder
    cbz_path = folder.with_suffix(".cbz")

    if cbz_path.exists():
        print(f"  ⚠ {cbz_path.name} already exists — skipping")
        return False

    # Gather and sort images for correct page order
    images = sorted(
        [f for f in folder.iterdir()
         if f.is_file() and f.suffix.lower() in IMAGE_EXTS],
        key=lambda f: f.name,
    )

    if not images:
        print(f"  ⚠ No images found in {folder.relative_to(root)} — skipping")
        return False

    print(f"Packing: {folder.relative_to(root)} → {cbz_path.name} ({len(images)} pages)")

    try:
        with zipfile.ZipFile(cbz_path, "w", zipfile.ZIP_STORED) as zf:
            for img in images:
                # Use just the filename — flat structure inside the CBZ
                zf.write(img, arcname=img.name)
    except Exception as e:
        print(f"  ✗ Error writing CBZ: {e}")
        return False

    print(f"  ✓ {cbz_path.name}")

    if delete_original:
        for img in images:
            img.unlink()
        folder.rmdir()  # Removes folder only if empty
        print(f"  🗑 Cleaned up original folder")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Pack folders of original images into CBZ files."
    )
    parser.add_argument("root", type=str,
                        help="Root directory to scan for image folders")
    parser.add_argument("--dry-run", action="store_true",
                        help="List folders that would be packed without packing")
    parser.add_argument("--delete", action="store_true",
                        help="Delete original images and folder after packing")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"Error: directory not found: {root}")
        raise SystemExit(1)

    folders = find_image_folders(root)
    if not folders:
        print("No folders containing images found.")
        return

    print(f"Found {len(folders)} image folder(s)\n")

    if args.dry_run:
        for folder in folders:
            cbz = folder.with_suffix(".cbz")
            images = [f for f in folder.iterdir()
                      if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
            status = "exists" if cbz.exists() else "would pack"
            print(f"  [{status}] {folder.relative_to(root)} ({len(images)} images)")
        print(f"\nDry run complete. {len(folders)} folder(s) found.")
        return

    packed = 0
    skipped = 0
    errors = 0

    for folder in folders:
        try:
            if images_to_cbz(folder, root, delete_original=args.delete):
                packed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗ Unexpected error with {folder}: {e}")
            errors += 1

    print(f"\nDone. Packed: {packed}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()

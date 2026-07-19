#!/usr/bin/env python3
"""
pdfs_to_cbz.py — Convert comic PDFs to CBZ using cbconvert.
Quality is set to 80 (cbconvert default is 75).

Requires cbconvert on PATH:
    brew install gen2brain/tap/cbconvert

Usage:
    python3 pdfs_to_cbz.py /Volumes/external/Books/Comics --dry-run
    python3 pdfs_to_cbz.py /Volumes/external/Books/Comics
    python3 pdfs_to_cbz.py /Volumes/external/Books/Comics --delete
"""

import argparse
import shutil
import subprocess
from pathlib import Path


def find_pdfs(root: Path) -> list[Path]:
    """Find all PDF files recursively under root."""
    return sorted(root.rglob("*.pdf"))


def convert_pdf_to_cbz(pdf_path: Path, root: Path, quality: int = 80,
                       delete_original: bool = True) -> bool:
    """Convert a single PDF to CBZ using cbconvert. Returns True on success."""
    cbz_path = pdf_path.with_suffix(".cbz")

    if cbz_path.exists():
        print(f"  ⚠ {cbz_path.name} already exists — skipping")
        return False

    # cbconvert writes the output archive to --outdir with the same
    # base name as the input. We output to the same directory as the PDF.
    outdir = pdf_path.parent

    print(f"Converting: {pdf_path.relative_to(root)}")

    cmd = [
        "/Users/matthew/Downloads/cbconvert-1.2.0/cbconvert",
        "convert",
        "--format", "jpeg",
        "--archive", "zip",
        "--quality", str(quality),
        "--outdir", str(outdir),
        str(pdf_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min per file — large PDFs can take a while
        )
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timed out after 10 minutes")
        return False
    except FileNotFoundError:
        print("  ✗ cbconvert not found. Install with: brew install gen2brain/tap/cbconvert")
        raise SystemExit(1)

    if result.returncode != 0:
        print(f"  ✗ cbconvert failed (exit {result.returncode})")
        if result.stderr:
            print(f"    {result.stderr.strip()}")
        return False

    if not cbz_path.exists():
        # cbconvert may produce .cbz or .zip — check for .zip as fallback
        zip_path = pdf_path.with_suffix(".zip")
        if zip_path.exists():
            zip_path.rename(cbz_path)
        else:
            print(f"  ✗ Expected output not found: {cbz_path.name}")
            return False

    print(f"  ✓ {cbz_path.name}")

    if delete_original:
        pdf_path.unlink()
        print(f"  🗑 Deleted original: {pdf_path.name}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert comic PDFs to CBZ using cbconvert (quality 80)."
    )
    parser.add_argument("root", type=str,
                        help="Root directory to scan for PDFs")
    parser.add_argument("--dry-run", action="store_true",
                        help="List PDFs that would be converted without converting")
    parser.add_argument("--delete", action="store_true",
                        help="Delete original PDF after successful conversion")
    parser.add_argument("--quality", type=int, default=80,
                        help="JPEG quality (default: 80, cbconvert default is 75)")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"Error: directory not found: {root}")
        raise SystemExit(1)

    pdfs = find_pdfs(root)
    if not pdfs:
        print("No PDF files found.")
        return

    print(f"Found {len(pdfs)} PDF file(s)\n")

    if args.dry_run:
        for pdf in pdfs:
            cbz = pdf.with_suffix(".cbz")
            status = "exists" if cbz.exists() else "would convert"
            print(f"  [{status}] {pdf.relative_to(root)}")
        print(f"\nDry run complete. {len(pdfs)} file(s) found.")
        return

    converted = 0
    skipped = 0
    errors = 0

    for pdf in pdfs:
        try:
            if convert_pdf_to_cbz(pdf, root, quality=args.quality,
                                  delete_original=args.delete):
                converted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗ Unexpected error with {pdf.name}: {e}")
            errors += 1

    print(f"\nDone. Converted: {converted}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()

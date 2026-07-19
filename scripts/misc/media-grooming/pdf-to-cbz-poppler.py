#!/usr/bin/env python3
"""
pdfs_to_cbz_poppler.py — Convert comic PDFs to CBZ using pdf2image (poppler).
Use this for PDFs that cbconvert/MuPDF can't handle.

Requirements:
    pip install pdf2image
    brew install poppler

Usage:
    python3 pdfs_to_cbz_poppler.py /Volumes/external/Books/Comics --dry-run
    python3 pdfs_to_cbz_poppler.py /Volumes/external/Books/Comics
    python3 pdfs_to_cbz_poppler.py /Volumes/external/Books/Comics --delete
"""

import argparse
import io
import zipfile
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    print("Install pdf2image first:  pip install pdf2image")
    print("Also requires poppler:    brew install poppler")
    raise SystemExit(1)


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def find_pdfs_without_cbz(root: Path) -> list[Path]:
    """Find PDFs that don't have a matching CBZ (i.e., cbconvert failed)."""
    pdfs = []
    for pdf in sorted(root.rglob("*.pdf")):
        cbz = pdf.with_suffix(".cbz")
        if not cbz.exists():
            pdfs.append(pdf)
    return pdfs


def convert_pdf_to_cbz(pdf_path: Path, root: Path, dpi: int = 300,
                       quality: int = 80,
                       delete_original: bool = False) -> bool:
    """Convert a single PDF to CBZ using pdf2image. Returns True on success."""
    cbz_path = pdf_path.with_suffix(".cbz")

    if cbz_path.exists():
        print(f"  ⚠ {cbz_path.name} already exists — skipping")
        return False

    print(f"Converting: {pdf_path.relative_to(root)}")

    try:
        images = convert_from_path(
            str(pdf_path),
            dpi=dpi,
            fmt="jpeg",
            thread_count=4,
        )
    except Exception as e:
        print(f"  ✗ pdf2image error: {e}")
        return False

    if not images:
        print(f"  ✗ No pages extracted from PDF")
        return False

    try:
        with zipfile.ZipFile(cbz_path, "w", zipfile.ZIP_STORED) as zf:
            for i, img in enumerate(images, start=1):
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=quality)
                zf.writestr(f"{i:04d}.jpg", buf.getvalue())
    except Exception as e:
        print(f"  ✗ Error writing CBZ: {e}")
        # Clean up partial CBZ
        if cbz_path.exists():
            cbz_path.unlink()
        return False

    print(f"  ✓ {len(images)} pages → {cbz_path.name}")

    if delete_original:
        pdf_path.unlink()
        print(f"  🗑 Deleted original: {pdf_path.name}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert comic PDFs to CBZ using pdf2image/poppler."
    )
    parser.add_argument("root", type=str,
                        help="Root directory to scan for PDFs")
    parser.add_argument("--dry-run", action="store_true",
                        help="List PDFs that would be converted without converting")
    parser.add_argument("--delete", action="store_true",
                        help="Delete original PDF after successful conversion")
    parser.add_argument("--dpi", type=int, default=300,
                        help="Render DPI (default: 300)")
    parser.add_argument("--quality", type=int, default=80,
                        help="JPEG quality (default: 80)")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"Error: directory not found: {root}")
        raise SystemExit(1)

    # Only find PDFs that don't already have a matching CBZ
    pdfs = find_pdfs_without_cbz(root)

    if not pdfs:
        print("No PDFs without a matching CBZ found.")
        print("(All PDFs may have already been converted.)")
        return

    print(f"Found {len(pdfs)} PDF(s) without a matching CBZ\n")

    if args.dry_run:
        for pdf in pdfs:
            print(f"  [would convert] {pdf.relative_to(root)}")
        print(f"\nDry run complete. {len(pdfs)} file(s) to convert.")
        return

    converted = 0
    skipped = 0
    errors = 0

    for pdf in pdfs:
        try:
            if convert_pdf_to_cbz(pdf, root, dpi=args.dpi,
                                  quality=args.quality,
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

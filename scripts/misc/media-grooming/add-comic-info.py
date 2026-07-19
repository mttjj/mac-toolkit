#!/usr/bin/env python3
"""
add_comicinfo.py — Generate ComicInfo.xml and inject into CBZ files
without extracting or re-compressing the archive.

Usage:
    python3 add_comicinfo.py metadata.csv /Volumes/external/Books/Comics

CSV columns (all optional except filepath):
    filepath, series, title, number, summary,
    year, month, writer, artist, publisher, format

filepath is relative to the library root (second argument).
Use a blank cell to omit a field from the XML.
Multiple creators in writer/artist are comma-separated.
"""

import csv
import sys
import zipfile
import xml.sax.saxutils as su
from pathlib import Path


# Kept fields in schema order.
# "artist" in the CSV maps to <Penciller> in the XML.
TEXT_FIELDS = [
    ("Title", "title"),
    ("Series", "series"),
    ("Number", "number"),
    ("Summary", "summary"),
    ("Year", "year"),
    ("Month", "month"),
    ("Writer", "writer"),
    ("Penciller", "artist"),
    ("Publisher", "publisher"),
    ("Format", "format"),
]


def escape(value: str) -> str:
    """XML-escape a text value."""
    return su.escape(str(value))


def build_comicinfo(row: dict, page_count: int | None = None) -> str:
    """Build a ComicInfo.xml string from a CSV row."""

    def get(csv_key: str) -> str:
        return (row.get(csv_key, "") or "").strip()

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<ComicInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '          xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
    ]

    for xml_name, csv_key in TEXT_FIELDS:
        val = get(csv_key)
        if val:
            lines.append(f"  <{xml_name}>{escape(val)}</{xml_name}>")

    # PageCount — use CSV value if provided, otherwise auto-detect.
    pc = get("PageCount")
    if pc:
        lines.append(f"  <PageCount>{escape(pc)}</PageCount>")
    elif page_count is not None:
        lines.append(f"  <PageCount>{page_count}</PageCount>")

    lines.append("</ComicInfo>")
    return "\n".join(lines) + "\n"


def count_images_in_cbz(cbz_path: Path) -> int:
    """Count image entries in a CBZ without extracting."""
    count = 0
    with zipfile.ZipFile(cbz_path, "r") as zf:
        for name in zf.namelist():
            lower = name.lower()
            if lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")):
                count += 1
    return count


def inject_comicinfo(cbz_path: Path, xml_content: str) -> bool:
    """
    Append ComicInfo.xml to a CBZ archive.
    Returns True if injected, False if skipped (already present).
    """
    with zipfile.ZipFile(cbz_path, "r") as zf:
        existing = zf.namelist()

    if "ComicInfo.xml" in existing:
        print(f"  ⚠ ComicInfo.xml already exists in {cbz_path.name} — skipping. "
              f"Remove it first if you want to replace it.")
        return False

    with zipfile.ZipFile(cbz_path, "a", zipfile.ZIP_STORED) as zf:
        zf.writestr("ComicInfo.xml", xml_content)

    return True


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    library_root = Path(sys.argv[2])

    if not csv_path.is_file():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    if not library_root.is_dir():
        print(f"Error: library root not found: {library_root}")
        sys.exit(1)

    injected = 0
    skipped = 0
    errors = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_path = (row.get("filepath", "") or "").strip()
            if not rel_path:
                continue

            cbz_path = library_root / rel_path
            if not cbz_path.exists():
                print(f"✗ File not found: {cbz_path}")
                errors += 1
                continue

            print(f"Processing: {cbz_path.name}")

            # Auto-detect page count if not in CSV.
            page_count = None
            try:
                page_count = count_images_in_cbz(cbz_path)
            except Exception as e:
                print(f"  ⚠ Could not read archive: {e}")

            xml = build_comicinfo(row, page_count)

            try:
                if inject_comicinfo(cbz_path, xml):
                    injected += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"  ✗ Error injecting: {e}")
                errors += 1

    print(f"\nDone. Injected: {injected}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()

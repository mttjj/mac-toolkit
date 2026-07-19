#!/usr/bin/env python3
"""generate_csv_skeleton.py — Scan comics folder and create a CSV pre-filled
with filepath, series, title, and number parsed from folder/filename."""

import csv
import re
from pathlib import Path

LIBRARY_ROOT = Path("/Volumes/external/Books/Comics")

COLUMNS = [
    "filepath",
    "series",
    "title",
    "number",
    "summary",
    "year",
    "month",
    "writer",
    "artist",
    "publisher",
    "format",
]


def normalize_name(name: str) -> str:
    """
    Replace hyphens that should be colons.
    Rule: a hyphen with no space before it but a space after it
    (e.g., "Panther- Epic") is a colon.
    A hyphen with a space before it or no space after it stays a hyphen.
    """
    name = re.sub(r"(\w)-(\s)", r"\1:\2", name)
    name = re.sub(r"(\w)–(\s)", r"\1:\2", name)
    return name


def parse_filename(name: str) -> tuple[str, str]:
    """
    Extract (number, title) from a CBZ filename.
    Handles these patterns:
        Volume #01              -> number="1", title="Volume #01"
        Volume #03 - Title      -> number="3", title="Title"
        Series (1964) #165      -> number="165", title="Series (1964) #165"
        Series (2016) #101 - T  -> number="101", title="T"
        Title                   -> number="", title="Title"
    """
    stem = Path(name).stem

    m = re.search(r"#(\d+(?:\.\d+)?)", stem)
    if not m:
        return "", normalize_name(stem)

    number = m.group(1)

    sep_match = re.search(r"#\d+(?:\.\d+)?\s*[-–]\s*(.+)", stem)
    if sep_match:
        title = sep_match.group(1).strip()
    else:
        title = stem

    title = normalize_name(title)
    return number, title


rows = []
for cbz in sorted(LIBRARY_ROOT.rglob("*.cbz")):
    rel = cbz.relative_to(LIBRARY_ROOT)
    folder = rel.parts[0] if len(rel.parts) > 1 else ""
    is_one_shot = folder.lower() in ("one-shots", "one shots", "one_shots")

    number, title = parse_filename(cbz.name)

    row = {col: "" for col in COLUMNS}
    row["filepath"] = str(rel)
    row["series"] = "" if is_one_shot else normalize_name(folder)
    row["title"] = title
    row["number"] = number
    rows.append(row)

with open("metadata.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to metadata.csv")

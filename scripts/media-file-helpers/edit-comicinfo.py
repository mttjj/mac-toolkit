#!/usr/bin/env python3
"""
edit-comicinfo.py — Extract ComicInfo.xml from a CBZ, edit in VS Code, push back.

Usage:
    python3 edit-comicinfo.py "path/to/comic.cbz"
"""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


BLANK_XML = """<?xml version="1.0" encoding="utf-8"?>
<ComicInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Title></Title>
  <Series></Series>
  <Number></Number>
  <Summary></Summary>
  <Year></Year>
  <Month></Month>
  <Writer></Writer>
  <Penciller></Penciller>
  <Publisher></Publisher>
  <Format></Format>
</ComicInfo>
"""


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    cbz_path = Path(sys.argv[1]).expanduser().resolve()
    if not cbz_path.exists():
        print(f"Error: file not found: {cbz_path}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        xml_path = tmpdir / "ComicInfo.xml"

        # Extract existing ComicInfo.xml, or create blank template
        try:
            with zipfile.ZipFile(cbz_path, "r") as zf:
                zf.extract("ComicInfo.xml", tmpdir)
            print(f"Extracted ComicInfo.xml from {cbz_path.name}")
        except KeyError:
            xml_path.write_text(BLANK_XML, encoding="utf-8")
            print(f"No ComicInfo.xml found — created blank template")
        except zipfile.BadZipFile:
            print(f"Error: {cbz_path} is not a valid CBZ file.")
            sys.exit(1)

        # Open in VS Code and wait for the editor to close
        print("Opening in VS Code... (close the tab when done editing)")
        subprocess.run(["code", "--wait", str(xml_path)])

        # Push the edited XML back into the archive
        print(f"Updating {cbz_path.name}...")
        result = subprocess.run(
            ["zip", "-j", str(cbz_path), str(xml_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"Error updating archive: {result.stderr}")
            sys.exit(1)

        print("Done.")


if __name__ == "__main__":
    main()

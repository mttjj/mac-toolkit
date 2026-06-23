#!/usr/bin/env python3
from datetime import date, timedelta
import os

"""
Generates markdown files that can be imported into Bear.app for a year's worth of media diet entries.
Generated with ChatGPT on 22 Dec 2025.
"""

year = 2027

ROOT = str(year)
os.makedirs(ROOT, exist_ok=True)

start = date(year, 1, 1)
end = date(year, 12, 31)
d = start
while d <= end:
    month_dir = os.path.join(ROOT, f"{d.month:02d}")
    os.makedirs(month_dir, exist_ok=True)
    filename = f"{d:%Y-%m-%d}.md"
    path = os.path.join(month_dir, filename)
    content = f"# {d:%Y-%m-%d}: {d:%A}\n#media-diet/{year}/{d:%m}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    d += timedelta(days=1)

print(f"Created folder '{ROOT}' with monthly subfolders and daily markdown files.")

import os
import shutil
import subprocess
import re

# Configuration
# The folder containing the show (e.g., '/Volumes/Media/TV Shows/The Twilight Zone')
SHOW_ROOT = '/Volumes/external/~inbox/TV Shows/Special Cases/Arthur (1996)'
# The new parent directory where the show folder should be moved (e.g., '/Volumes/Media/TV Shows2')
DEST_ROOT = '/Volumes/external/~inbox/TV Shows/Unprocessed'

EXTENSIONS = ('.mp4', '.m4v')

def migrate_tv_show():
    # 1. Setup show name and target show folder
    show_name = os.path.basename(SHOW_ROOT.strip('/'))
    target_show_dir = os.path.join(DEST_ROOT, show_name)

    print(f"Migrating: {show_name} -> {target_show_dir}")

    # pattern = re.compile(r'(\d+)[xX](\d+)')

    try:
        # Walk through the original show directory
        for root, dirs, files in os.walk(SHOW_ROOT):
            for filename in files:
                if filename.lower().endswith(EXTENSIONS):
                    # 2. Extract season/episode
                    # match = pattern.search(filename)
                    # if not match:
                    #     print(f"Skipping: {filename} (No SXEX pattern)")
                    #     continue

                    # season_num = match.group(1).zfill(2)
                    # episode_num = match.group(2).zfill(2)
                    # extension = os.path.splitext(filename)[1]
                    # new_filename = f"{show_name} S{season_num}E{episode_num}{extension}"

                    # 3. Calculate target path
                    # Get path relative to SHOW_ROOT (e.g., 'Season 1')
                    rel_path = os.path.relpath(root, SHOW_ROOT)
                    # Combine: DEST_ROOT + Show Name + Relative Path (Season folder)
                    target_dir = os.path.join(target_show_dir, rel_path)

                    os.makedirs(target_dir, exist_ok=True)

                    old_file_path = os.path.join(root, filename)
                    new_file_path = os.path.join(target_dir, filename)

                    # 4. FFmpeg Wipe and Move to NEW location
                    cmd = [
                        'ffmpeg', '-i', old_file_path,
                        '-map_metadata', '-1',
                        '-c', 'copy',
                        new_file_path,
                        '-y'
                    ]

                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        # Now that the cleaned version exists in TV Shows2, delete the original
                        os.remove(old_file_path)
                        print(f"Migrated: {filename} -> {filename}")
                    else:
                        print(f"Error processing {filename}: {result.stderr}")

        print(f"\nMigration of {show_name} complete.")
        print("Note: Empty season folders may remain in the original root.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    migrate_tv_show()

import os
import shutil
import subprocess

# Configuration
SOURCE_DIR = '/Volumes/external/~inbox/Movies/Unprocessed/Short Films'
EXTENSIONS = ('.mp4', '.m4v')
IGNORE_LIST = ['movie_source_metadata.csv', 'organize_wipe.py']

def wipe_and_organize():
    print(f"Wiping metadata and organizing files in {SOURCE_DIR}...")

    try:
        files = [f for f in os.listdir(SOURCE_DIR)
                 if os.path.isfile(os.path.join(SOURCE_DIR, f))
                 and f not in IGNORE_LIST]

        count = 0
        for filename in files:
            if filename.lower().endswith(EXTENSIONS):
                # 1. Setup paths
                folder_name = os.path.splitext(filename)[0]
                folder_path = os.path.join(SOURCE_DIR, folder_name)

                old_path = os.path.join(SOURCE_DIR, filename)
                # We'll create the cleaned file directly in the new folder
                new_path = os.path.join(folder_path, filename)

                # Create folder first
                os.makedirs(folder_path, exist_ok=True)

                # 2. Run FFmpeg to strip metadata and save directly to the new folder
                # -map_metadata -1 strips all global metadata
                # -c copy ensures no re-encoding (instant process)
                cmd = [
                    'ffmpeg', '-i', old_path,
                    '-map_metadata', '-1',
                    '-c', 'copy',
                    new_path,
                    '-y' # Overwrite if exists
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    # 3. Remove the original file from root after successful wipe/move
                    os.remove(old_path)
                    count += 1
                    print(f"Processed: {filename} -> {folder_name}/")
                else:
                    print(f"Error processing {filename}: {result.stderr}")

        print(f"\nFinished. {count} movies stripped and organized.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    wipe_and_organize()

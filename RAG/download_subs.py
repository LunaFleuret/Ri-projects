import os
import subprocess
import re
import shutil
import sys
from datetime import datetime
import rebuild_db

# Configuration
DATA_DIR = r'd:/薫衣りぃ/RAG/字幕データ'

def sanitize_filename(name):
    """
    Sanitize the filename by removing or replacing illegal characters.
    """
    # Remove invalid characters for Windows filenames
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name.strip()

def download_subtitle(url):
    """
    Downloads the subtitle for the given YouTube URL.
    Returns the path to the downloaded file or None if failed.
    """
    print(f"Processing URL: {url}")
    
    try:
        # 1. Get Metadata (Title, Upload Date, ID)
        # We use --print to get specific fields
        cmd_meta = [
            'yt-dlp',
            '--print', '%(upload_date)s\t%(title)s\t%(id)s',
            url
        ]
        
        print("Fetching metadata...")
        # Don't specify encoding here, decode manually
        result = subprocess.run(cmd_meta, capture_output=True)
        
        if result.returncode != 0:
            # Try to decode stderr for logging
            try:
                err_msg = result.stderr.decode('utf-8')
            except:
                err_msg = result.stderr.decode('cp932', errors='replace')
            print(f"Error fetching metadata: {err_msg}")
            return None
            
        # Try decoding stdout with utf-8, then cp932
        try:
            output = result.stdout.decode('utf-8').strip()
        except UnicodeDecodeError:
            output = result.stdout.decode('cp932', errors='replace').strip()

        if not output:
            print("No metadata found.")
            return None
            
        upload_date, title, video_id = output.split('\t')
        print(f"Found video: {title} ({upload_date}) [ID: {video_id}]")
        
        # 2. Download Subtitle
        # We want Japanese subtitles (.ja.vtt)
        # We will download it to the current directory first with a temporary name
        temp_filename_template = f"temp_{video_id}"
        
        cmd_download = [
            'yt-dlp',
            '--write-sub', '--write-auto-sub', '--sub-lang', 'ja',
            '--skip-download',  # Don't download video
            '--output', temp_filename_template,
            url
        ]
        
        print("Downloading subtitle...")
        subprocess.run(cmd_download, check=True)
        
        # yt-dlp appends the language code and extension, e.g., temp_VIDEOID.ja.vtt
        downloaded_file = f"{temp_filename_template}.ja.vtt"
        
        if not os.path.exists(downloaded_file):
            print("Subtitle file was not downloaded. It might not be available in Japanese.")
            return None
            
        # 3. Rename and Move
        sanitized_title = sanitize_filename(title)
        new_filename = f"{upload_date}_{sanitized_title}_{video_id}.ja.vtt"
        destination_path = os.path.join(DATA_DIR, new_filename)
        
        # Move file
        shutil.move(downloaded_file, destination_path)
        print(f"Saved subtitle to: {destination_path}")
        
        return destination_path

    except FileNotFoundError:
        print("Error: yt-dlp not found. Please ensure yt-dlp is installed and in your PATH.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("YouTube URLを入力してください: ").strip()
    
    if not url:
        print("URLが入力されませんでした。")
        return

    file_path = download_subtitle(url)
    
    if file_path:
        print("\nUpdating database...")
        try:
            rebuild_db.rebuild_database()
            print("Success! Database updated.")
        except Exception as e:
            print(f"Error updating database: {e}")
    else:
        print("\nFailed to download subtitle.")

if __name__ == "__main__":
    main()

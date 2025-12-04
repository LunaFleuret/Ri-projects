import os
import sqlite3
import re
import glob

# Configuration
DATA_DIR = r'd:/薫衣りぃ/RAG/字幕データ'
DB_FILE = 'kunue_rii.db'

def parse_timestamp(timestamp_str):
    """Converts HH:MM:SS.mmm to seconds."""
    try:
        parts = timestamp_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0

def clean_text(text):
    """Removes WebVTT tags and extra whitespace."""
    # Remove tags like <00:00:00.199><c>...</c>
    text = re.sub(r'<[^>]+>', '', text)
    # Remove &nbsp; and other entities if any (though usually raw text)
    text = text.replace('&nbsp;', ' ')
    return text.strip()

def parse_vtt(file_path):
    """Parses a VTT file and returns a list of (start_time, text) tuples."""
    captions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_start = None
    current_text = []
    
    # Regex for timestamp line: 00:00:00.080 --> 00:00:02.430
    timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) -->')

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue

        match = timestamp_pattern.match(line)
        if match:
            # If we have previous text, save it
            if current_start is not None and current_text:
                full_text = clean_text(" ".join(current_text))
                if full_text:
                    captions.append((current_start, full_text))
            
            current_start = parse_timestamp(match.group(1))
            current_text = []
        else:
            # Append text line if we are inside a caption block
            if current_start is not None:
                # Skip lines that are just metadata or empty
                if 'align:start' in line: # Sometimes metadata is on the same line or next
                    continue
                current_text.append(line)

    # Add the last caption
    if current_start is not None and current_text:
        full_text = clean_text(" ".join(current_text))
        if full_text:
            captions.append((current_start, full_text))
            
    return captions

def rebuild_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Existing database {DB_FILE} removed.")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create FTS5 table with trigram tokenizer for better Japanese support
    c.execute('''
    CREATE VIRTUAL TABLE subtitles USING fts5(
        video_id,
        date,
        title,
        text,
        timestamp,
        url,
        tokenize='trigram'
    )
    ''')

    files = glob.glob(os.path.join(DATA_DIR, '*.vtt'))
    print(f"Found {len(files)} VTT files.")

    batch_data = []
    count = 0

    for file_path in files:
        filename = os.path.basename(file_path)
        
        try:
            # Parse filename: YYYYMMDD_TITLE_VIDEOID.ja.vtt
            # Use regex to extract Video ID (11 chars) from the end
            match = re.search(r'_([a-zA-Z0-9_-]{11})\.ja(?:-orig)?\.vtt$', filename)
            if match:
                video_id = match.group(1)
                # Date is the first 8 chars
                date = filename[:8]
                # Title is everything between Date_ and _VideoID
                video_id_start_index = match.start(1)
                title = filename[9:video_id_start_index-1]
            else:
                print(f"Skipping malformed filename: {filename}")
                continue
            
            captions = parse_vtt(file_path)
            
            for start_seconds, text in captions:
                # Format timestamp for display (HH:MM:SS)
                m, s = divmod(int(start_seconds), 60)
                h, m = divmod(m, 60)
                timestamp_display = f"{h:02d}:{m:02d}:{s:02d}"
                
                # Create URL with timestamp
                url = f"https://www.youtube.com/watch?v={video_id}&t={int(start_seconds)}s"
                
                batch_data.append((
                    video_id,
                    date,
                    title,
                    text,
                    timestamp_display,
                    url
                ))
                count += 1
                
                if len(batch_data) >= 10000:
                    c.executemany('INSERT INTO subtitles VALUES (?,?,?,?,?,?)', batch_data)
                    conn.commit()
                    batch_data = []
                    print(f"Processed {count} lines...")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue

    if batch_data:
        c.executemany('INSERT INTO subtitles VALUES (?,?,?,?,?,?)', batch_data)
        conn.commit()

    print(f"Database rebuild complete. Total {count} lines indexed.")
    conn.close()

if __name__ == "__main__":
    rebuild_database()

import sqlite3
import json
import os

# 設定
JSONL_FILE = 'kunue_rii_db.jsonl' 
DB_FILE = 'kunue_rii.db'

def create_database():
    if not os.path.exists(JSONL_FILE):
        print(f"エラー: {JSONL_FILE} が見つかりません。")
        return

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 高速検索（FTS5）用のテーブルを作成
    c.execute('''
    CREATE VIRTUAL TABLE subtitles USING fts5(
        video_id,
        date,
        title,
        text,
        timestamp,
        url
    )
    ''')

    print("データを変換中...（数分かかる場合があります）")
    
    count = 0
    batch_data = []
    
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                batch_data.append((
                    data['video_id'],
                    data.get('date', 'Unknown'),
                    data.get('title', 'No Title'),
                    data['text'],
                    data['timestamp'],
                    data['url']
                ))
                count += 1
            except json.JSONDecodeError:
                continue

            if count % 10000 == 0:
                c.executemany('INSERT INTO subtitles VALUES (?,?,?,?,?,?)', batch_data)
                conn.commit()
                batch_data = []
                print(f"{count} 行処理完了...")

    if batch_data:
        c.executemany('INSERT INTO subtitles VALUES (?,?,?,?,?,?)', batch_data)
        conn.commit()

    print(f"完了！合計 {count} 行のデータをデータベース化しました。")
    conn.close()

if __name__ == "__main__":
    create_database()
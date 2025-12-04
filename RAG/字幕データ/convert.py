import os
import json
import re
import glob

# 設定
SOURCE_DIR = '.'
OUTPUT_FILE = 'kunue_rii_db.jsonl'

def parse_vtt_time(time_str):
    """ VTTの時間を秒数に変換 """
    parts = time_str.replace('.', ':').split(':')
    try:
        if len(parts) >= 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(float(parts[2]))
    except:
        return 0
    return 0

def clean_text(text):
    """ タグ除去・整形 """
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ')
    text = text.strip()
    return text

def main():
    files = glob.glob(os.path.join(SOURCE_DIR, "*.vtt"))
    print(f"フォルダ内のファイル数: {len(files)}")

    # 重複防止用の記録セット
    processed_video_ids = set()
    total_records = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        for file_path in files:
            filename = os.path.basename(file_path)
            
            # --- 動画IDの抽出処理 ---
            try:
                base = filename.replace('.ja.vtt', '').replace('.vtt', '')
                parts = base.split('_')
                
                # ファイル名末尾が動画IDと仮定
                video_id = parts[-1]
                
                # 動画IDが11桁（YouTubeの標準）かチェック。違うならスキップ
                if len(video_id) != 11:
                    # IDが上手く取れない場合の予備処理
                    # もしIDが含まれていそうな場所があれば調整（基本は末尾）
                    pass 

                date = parts[0] if len(parts) > 0 else "Unknown"
                title = "_".join(parts[1:-1]) if len(parts) > 2 else "No Title"

            except Exception as e:
                print(f"スキップ（ファイル名解析不可）: {filename}")
                continue

            # --- 【重要】動画レベルの重複チェック ---
            if video_id in processed_video_ids:
                # 既に処理したIDなら何もしない（スキップ）
                continue
            
            # 処理済みリストに登録
            processed_video_ids.add(video_id)

            # --- VTTの中身を解析 ---
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_start_time = None
            previous_text = ""  # 【重要】直前のセリフを記憶
            
            for line in lines:
                line = line.strip()
                
                if '-->' in line:
                    current_start_time = line.split('-->')[0].strip()
                    continue
                
                if not line or line == 'WEBVTT' or line.startswith('NOTE'):
                    continue
                
                text = clean_text(line)
                
                # --- 【重要】セリフレベルの重複チェック ---
                # テキストがあり、かつ「直前のセリフ」と違う場合のみ保存
                if text and current_start_time and text != previous_text:
                    
                    seconds = parse_vtt_time(current_start_time)
                    
                    record = {
                        "date": date,
                        "title": title,
                        "video_id": video_id,
                        "text": text,
                        "timestamp": current_start_time,
                        "url": f"https://www.youtube.com/watch?v={video_id}&t={seconds}s"
                    }
                    
                    json.dump(record, out_f, ensure_ascii=False)
                    out_f.write('\n')
                    
                    total_records += 1
                    previous_text = text # 今回のセリフを「直前」として記憶

    print("-" * 30)
    print(f"処理した動画数（ユニーク）: {len(processed_video_ids)}")
    print(f"保存した字幕行数: {total_records}")
    print(f"完了！重複を取り除いて '{OUTPUT_FILE}' を作成しました。")

if __name__ == "__main__":
    main()
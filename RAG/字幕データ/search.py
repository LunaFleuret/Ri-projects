import json

FILE_PATH = "kunue_rii_db.jsonl"   # ← ダウンロードした JSONL を置く場所

keyword = input("検索ワード: ")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        text = data.get("text", "")
        if keyword in text:
            print(data)

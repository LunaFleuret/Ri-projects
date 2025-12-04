import streamlit as st
import sqlite3
from collections import defaultdict
import datetime

# データベース設定
DB_FILE = 'kunue_rii.db'

def format_date(date_str):
    """YYYYMMDD -> YYYY年MM月DD日"""
    if len(date_str) == 8 and date_str.isdigit():
        return f"{date_str[:4]}年{date_str[4:6]}月{date_str[6:]}日"
    return date_str

def search_db(query):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        # 全文検索
        c.execute('''
            SELECT date, title, text, timestamp, url 
            FROM subtitles 
            WHERE subtitles MATCH ? 
            LIMIT 200
        ''', (query,))
        results = c.fetchall()
    except Exception as e:
        st.error(f"検索エラー: {e}")
        return []
    finally:
        conn.close()
    return results

def group_results(results):
    """
    検索結果を動画（タイトル・日付）ごとにグループ化する
    Returns:
        Dict[str, Dict]: {
            'date_title_key': {
                'date': str,
                'title': str,
                'matches': List[Dict]
            }
        }
    """
    grouped = defaultdict(lambda: {'date': '', 'title': '', 'matches': []})
    
    # Sort results by date desc first (though we removed ORDER BY in SQL, we can sort here if needed, 
    # but for grouping we just need to aggregate)
    # Let's sort by date desc for display order
    sorted_results = sorted(results, key=lambda x: x[0], reverse=True)

    for date, title, text, timestamp, url in sorted_results:
        key = f"{date}_{title}"
        grouped[key]['date'] = date
        grouped[key]['title'] = title
        grouped[key]['matches'].append({
            'text': text,
            'timestamp': timestamp,
            'url': url
        })
    
    return grouped

# ページ設定
st.set_page_config(page_title="薫衣りぃ配信検索", layout="wide")

# CSS for Back to Top button and styling
st.markdown("""
    <style>
        .floating-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #888888;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            text-align: center;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            opacity: 0.6;
            transition: opacity 0.3s, background-color 0.3s;
        }
        .floating-button:hover {
            background-color: #666666;
            opacity: 1.0;
            color: white;
        }
        .match-box {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 5px solid #FF4B4B;
        }
        .stApp {
            scroll-behavior: smooth;
        }
    </style>
    <a href="#" class="floating-button" title="トップへ戻る">⬆</a>
""", unsafe_allow_html=True)

st.title("📺 薫衣りぃ db検索")
st.markdown("キーワードを入力すると、その発言をしたシーンを検索してURLを表示します。")
st.markdown("※ 複数のキーワードはスペースで区切ってください（例: `原神 スターレイル`）")

query = st.text_input("検索キーワード", "")

if query:
    with st.spinner('検索中...'):
        raw_results = search_db(query)
    
    if raw_results:
        grouped_data = group_results(raw_results)
        total_matches = len(raw_results)
        total_videos = len(grouped_data)
        
        st.success(f"{total_videos} 本の動画で {total_matches} 件の発言が見つかりました")
        
        for key, data in grouped_data.items():
            formatted_date = format_date(data['date'])
            title = data['title']
            matches = data['matches']
            
            with st.container():
                st.subheader(f"📅 {formatted_date}")
                st.markdown(f"**{title}**")
                
                # Show matches in an expander if there are many, or just list them
                # Default open if it's a small number of matches
                with st.expander(f"💬 発言箇所 ({len(matches)}件)", expanded=True):
                    for match in matches:
                        # Use columns for better layout: Timestamp/Link | Text
                        c1, c2 = st.columns([1, 4])
                        with c1:
                            st.markdown(f"[▶️ {match['timestamp']}]({match['url']})")
                        with c2:
                            st.markdown(f"「{match['text']}」")
                st.divider()
    else:
        st.warning("見つかりませんでした。別の言葉で試してみてください。")
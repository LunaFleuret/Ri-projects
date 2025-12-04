import sqlite3

DB_FILE = 'kunue_rii.db'

def test_search(query):
    print(f"Searching for: {query}")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute('''
            SELECT date, title, text, timestamp, url 
            FROM subtitles 
            WHERE subtitles MATCH ? 
            LIMIT 5
        ''', (query,))
        results = c.fetchall()
        print(f"Found {len(results)} results.")
        for row in results:
            print(f"Date: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Text: {row[2]}")
            print(f"Timestamp: {row[3]}")
            print(f"URL: {row[4]}")
            print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_search("リンゴ")
    test_search("原神")

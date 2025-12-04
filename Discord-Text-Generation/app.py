from flask import Flask, render_template, request, jsonify
import requests
import os
import datetime
import re

app = Flask(__name__)

# Ensure download directory exists
DOWNLOAD_FOLDER = 'downloaded_thumbnails'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

def extract_video_id(url):
    # Regex to extract video ID from various YouTube URL formats
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

@app.route('/api/process', methods=['POST'])
def process_url():
    data = request.json
    url = data.get('url')
    api_key = data.get('apiKey')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    if not api_key:
        return jsonify({'error': 'API Key is required'}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        # YouTube Data API v3
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,liveStreamingDetails',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            return jsonify({'error': f'YouTube API Error: {response.status_code}'}), 500
            
        result = response.json()
        if not result['items']:
            return jsonify({'error': 'Video not found'}), 404
            
        item = result['items'][0]
        snippet = item['snippet']
        live_details = item.get('liveStreamingDetails')
        
        title = snippet['title']
        
        # Thumbnail: Try maxres, then standard, then high, then medium, then default
        thumbnails = snippet['thumbnails']
        thumbnail_url = (thumbnails.get('maxres') or 
                         thumbnails.get('standard') or 
                         thumbnails.get('high') or 
                         thumbnails.get('medium') or 
                         thumbnails.get('default'))['url']

        # Date handling
        if live_details and 'scheduledStartTime' in live_details:
            # Live stream scheduled
            dt_str = live_details['scheduledStartTime']
            # ISO 8601 format: 2023-11-28T15:00:00Z
            # We need to handle timezone. Assuming input is UTC, convert to JST (+9)
            dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            dt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        elif live_details and 'actualStartTime' in live_details:
             # Live stream started
            dt_str = live_details['actualStartTime']
            dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            dt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        else:
            # Regular video upload date
            dt_str = snippet['publishedAt']
            dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            dt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))

        # Format: MM月DD日(曜日) HH時MM分～
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday_str = weekdays[dt.weekday()]
        formatted_date = dt.strftime(f'%m月%d日({weekday_str}) %H時%M分～')
        file_date = dt.strftime('%Y%m%d')
        
        message = f"```python\n'{title}'\n```\n### {formatted_date}\n<{url}>"
        
        return jsonify({
            'thumbnail_url': thumbnail_url,
            'message': message,
            'video_id': video_id,
            'title': title,
            'file_date': file_date,
            'formatted_date': formatted_date
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_thumbnail', methods=['POST'])
def save_thumbnail():
    data = request.json
    thumbnail_url = data.get('thumbnailUrl')
    title = data.get('title')
    file_date = data.get('fileDate')
    
    if not thumbnail_url or not title or not file_date:
        return jsonify({'error': 'Missing data'}), 400
        
    try:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            # Sanitize title for filename
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
            filename = f"{file_date}_{safe_title}.jpg"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return jsonify({'message': 'Thumbnail saved', 'path': filepath})
        else:
            return jsonify({'error': 'Failed to download image'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

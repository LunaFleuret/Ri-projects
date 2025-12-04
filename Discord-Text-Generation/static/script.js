let currentVideoId = null;
let currentThumbnailUrl = null;
let currentTitle = null;
let currentFileDate = null;
let currentFormattedDate = null;
let currentUrl = null;
let currentColor = 'blue';

// Load API Key from localStorage
document.addEventListener('DOMContentLoaded', () => {
    const savedApiKey = localStorage.getItem('youtube_api_key');
    if (savedApiKey) {
        document.getElementById('apiKeyInput').value = savedApiKey;
    }

    // Set initial color selection listener
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', (e) => {
            currentColor = e.target.dataset.color;
            updateColorSelection(currentColor);
            updateMessage();
        });
    });
});

function updateColorSelection(color) {
    document.querySelectorAll('.color-option').forEach(opt => {
        opt.classList.remove('selected');
        if (opt.dataset.color === color) {
            opt.classList.add('selected');
        }
    });
}

function updateMessage() {
    if (!currentTitle || !currentFormattedDate || !currentUrl) return;

    let message = '';
    const title = currentTitle;
    const date = currentFormattedDate;
    const url = currentUrl;

    switch (currentColor) {
        case 'blue':
            message = "```python\n'" + title + "'\n```\n### " + date + "\n<" + url + ">";
            break;
        case 'red':
            message = "```diff\n- " + title + "\n```\n### " + date + "\n<" + url + ">";
            break;
        case 'green':
            message = "```diff\n+ " + title + "\n```\n### " + date + "\n<" + url + ">";
            break;
        case 'yellow':
            message = "```fix\n" + title + "\n```\n### " + date + "\n<" + url + ">";
            break;
        default:
            message = "```python\n'" + title + "'\n```\n### " + date + "\n<" + url + ">";
    }

    document.getElementById('messageOutput').value = message;
}

document.getElementById('generateBtn').addEventListener('click', async () => {
    const url = document.getElementById('urlInput').value;
    const apiKey = document.getElementById('apiKeyInput').value;

    if (!url) {
        alert('URLを入力してください');
        return;
    }
    if (!apiKey) {
        alert('API Keyを入力してください');
        return;
    }

    // Save API Key to localStorage
    localStorage.setItem('youtube_api_key', apiKey);

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, apiKey })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Update UI with result
        const resultArea = document.getElementById('resultArea');
        const thumbnailImg = document.getElementById('thumbnailImg');

        thumbnailImg.src = data.thumbnail_url;

        // Store data
        currentVideoId = data.video_id;
        currentThumbnailUrl = data.thumbnail_url;
        currentTitle = data.title;
        currentFileDate = data.file_date;
        currentFormattedDate = data.formatted_date;
        currentUrl = url;

        // Generate message with current color
        updateMessage();

        resultArea.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
});

document.getElementById('saveThumbnailBtn').addEventListener('click', async () => {
    if (!currentThumbnailUrl || !currentTitle || !currentFileDate) return;

    const btn = document.getElementById('saveThumbnailBtn');
    const originalText = btn.textContent;
    btn.textContent = '保存中...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/save_thumbnail', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                thumbnailUrl: currentThumbnailUrl,
                title: currentTitle,
                fileDate: currentFileDate
            })
        });

        const data = await response.json();
        if (data.error) {
            alert('保存に失敗しました: ' + data.error);
            btn.textContent = originalText;
            btn.disabled = false;
        } else {
            // No alert, just visual feedback
            btn.textContent = '保存完了';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
            }, 2000);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('保存エラーが発生しました');
        btn.textContent = originalText;
        btn.disabled = false;
    }
});

document.getElementById('copyBtn').addEventListener('click', () => {
    const textarea = document.getElementById('messageOutput');
    textarea.select();
    document.execCommand('copy');

    // No alert, just visual feedback
    const btn = document.getElementById('copyBtn');
    const originalText = btn.textContent;
    btn.textContent = 'コピー完了';
    setTimeout(() => {
        btn.textContent = originalText;
    }, 2000);
});

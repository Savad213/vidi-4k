import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
sample_url = 'https://www.fsiblogxx.com/big-boobs/boobs-show-in-saree-sleeve-moved/'
req = urllib.request.Request(sample_url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    
    # Search for video player divs, data-src, or embed links
    print('Search for video / embed / stream keywords:')
    for line in html.split('\n'):
        if any(k in line.lower() for k in ['video', 'player', 'embed', 'watch', 'stream', 'jwplayer', 'dood', 'filemoon', 'streamtape', 'oneplay', 'ltdcdn']):
            print('Line:', line.strip()[:200])
except Exception as e:
    print('Error:', e)

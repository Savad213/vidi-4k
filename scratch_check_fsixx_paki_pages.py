import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.fsiblogxx.com/'
}

for tag in ['pakistani', 'pakistani-girl', 'lahore', 'karachi']:
    url = f'https://www.fsiblogxx.com/tag/{tag}/'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
        pages = [int(p) for p in re.findall(rf'/tag/{tag}/page/(\d+)/', html)]
        max_p = max(pages) if pages else 1
        print(f'Tag: {tag} -> Max pages: {max_p}')
    except Exception as e:
        print(f'Tag: {tag} -> Error: {e}')

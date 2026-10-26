import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for page in range(1, 5):
    url = f'https://www.fsiblogxx.com/porn-videos/page/{page}/' if page > 1 else 'https://www.fsiblogxx.com/porn-videos/'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
        vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit', 'privacy', 'terms', 'dmca'])]
        print(f'Page {page}: {len(vids)} videos found')
    except Exception as e:
        print(f'Page {page} error: {e}')

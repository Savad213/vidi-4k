import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.fsiblogxx.com/'
}

# Check fsiblogxx category / tag for pakistani
urls_to_try = [
    'https://www.fsiblogxx.com/category/pakistani/',
    'https://www.fsiblogxx.com/category/pakistani-sex-video/',
    'https://www.fsiblogxx.com/tag/pakistani/',
    'https://www.fsiblogxx.com/tag/pakistani-mms/',
    'https://www.fsiblogxx.com/tag/pakistani-girl/',
]

for u in urls_to_try:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode('utf-8', errors='ignore')
            title = re.search(r'<title>(.*?)</title>', html)
            links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
            vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit'])]
            print(f'{u} -> {r.status} | Title: {title.group(1) if title else ""} | Videos: {len(vids)}')
    except Exception as e:
        print(f'{u} -> Err: {e}')

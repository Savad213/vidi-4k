import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://mastiraja.tv/'
}

url = 'https://mastiraja.tv/category/pakistani-sex/'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    
    title = re.search(r'<title>(.*?)</title>', html)
    print('Category title:', title.group(1) if title else 'None')
    
    # Check max pages
    pages = [int(p) for p in re.findall(r'/category/pakistani-sex/page/(\d+)/', html)]
    print('Max Pakistani pages on Mastiraja:', max(pages) if pages else 'None')
    
    # Extract video links
    links = set(re.findall(r'href="(https://mastiraja\.tv/[^"]+)"', html))
    vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'privacy', 'dmca', 'terms', 'contact'])]
    print(f'Page 1 Pakistani video links: {len(vids)}')
    for v in sorted(vids)[:5]:
        print('  *', v)
except Exception as e:
    print('Error:', e)

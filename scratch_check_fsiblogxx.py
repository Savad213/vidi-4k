import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.fsiblogxx.com/'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        print('Status:', r.status)
        title = re.search(r'<title>(.*?)</title>', html)
        print('Title:', title.group(1) if title else 'No title')
        
        all_links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
        print(f'Total links on homepage: {len(all_links)}')
        
        cats = [l for l in all_links if '/category/' in l or '/tag/' in l]
        print(f'Categories / Tags: {len(cats)}')
        for c in sorted(cats)[:10]:
            print('  ->', c)
            
        posts = [l for l in all_links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'about', 'contact', 'dmca', 'terms', 'privacy'])]
        print(f'\nSample post links: {len(posts)}')
        for p in sorted(posts)[:10]:
            print('  *', p)
except Exception as e:
    print('Error accessing fsiblogxx:', e)

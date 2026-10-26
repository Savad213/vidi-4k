import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("=== 1. Checking FSIBlog ===")
try:
    req = urllib.request.Request('https://fsiblog.co.im/', headers=headers)
    with urllib.request.urlopen(req, timeout=8) as r:
        html = r.read().decode('utf-8', errors='ignore')
    links = set(re.findall(r'href="(https://fsiblog\.co\.im/[^"]+)"', html))
    for l in sorted(links):
        if '/category/' in l or '/tag/' in l:
            print('  FSI Link:', l)
except Exception as e:
    print('FSI Error:', e)

print("\n=== 2. Checking Mastiraja ===")
try:
    req = urllib.request.Request('https://mastiraja.tv/', headers=headers)
    with urllib.request.urlopen(req, timeout=8) as r:
        html = r.read().decode('utf-8', errors='ignore')
    links = set(re.findall(r'href="(https://mastiraja\.tv/[^"]+)"', html))
    for l in sorted(links):
        if '/category/' in l or '/tag/' in l:
            print('  Mastiraja Link:', l)
except Exception as e:
    print('Mastiraja Error:', e)

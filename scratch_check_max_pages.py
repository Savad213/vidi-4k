import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.fsiblogxx.com/porn-videos/'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    pages = [int(p) for p in re.findall(r'/porn-videos/page/(\d+)/', html)]
    print('Max page found on pagination:', max(pages) if pages else 'None')
except Exception as e:
    print('Error:', e)

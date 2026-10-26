import urllib.request
import re

url = 'https://pimpbunny.com/videos/cutefruit18-wiggles-her-phat-booty/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        
    vids = set(re.findall(r'href="(https://pimpbunny\.com/videos/[^"]+)"', html))
    print(f'Related pimpbunny video URLs: {len(vids)}')
    for v in list(vids)[:12]:
        print('  *', v)
        
    all_links = set(re.findall(r'href="(https://pimpbunny\.com/[^"]+)"', html))
    print('\nCategories / Tags on pimpbunny:')
    for l in sorted(all_links):
        if any(k in l for k in ['tag', 'category', 'model', 'channel']):
            print('   ->', l)
            
    # Check video player source
    mp4s = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', html)
    print(f'\nDirect mp4 stream links found: {len(mp4s)}')
    for s in mp4s[:3]:
        print('   stream:', s)
except Exception as ex:
    print('Error:', ex)

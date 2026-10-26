import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
sample_url = 'https://www.fsiblogxx.com/big-boobs/boobs-show-in-saree-sleeve-moved/'
req = urllib.request.Request(sample_url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    
    print('Page title:', re.findall(r'<title>(.*?)</title>', html))
    
    # Check iframes
    iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', html)
    print('Iframes found:', len(iframes), iframes)
    
    # Check video tags
    video_sources = re.findall(r'<source[^>]+src="([^"]+)"', html)
    print('Video source tags:', video_sources)
    
    # Check direct video or m3u8 or mp4
    urls = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', html)
    print('Direct mp4/m3u8 urls:', len(urls), urls[:3])
    
    # Check embed scripts or player data
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        if 'player' in s.lower() or 'file' in s.lower() or 'source' in s.lower():
            print('Player script snippet:', s[:300])
            break
            
except Exception as e:
    print('Error:', e)

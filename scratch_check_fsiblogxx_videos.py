import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www.fsiblogxx.com/porn-videos/'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    
    print('Porn videos page title:', re.findall(r'<title>(.*?)</title>', html))
    
    # Extract video links
    links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
    porn_vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit'])]
    print(f'Porn video links found: {len(porn_vids)}')
    for v in sorted(porn_vids)[:5]:
        print('  Video link:', v)
        
    # Check one video link
    if porn_vids:
        test_v = porn_vids[0]
        print(f'\nTesting video page: {test_v}')
        treq = urllib.request.Request(test_v, headers=headers)
        with urllib.request.urlopen(treq, timeout=10) as tr:
            vhtml = tr.read().decode('utf-8', errors='ignore')
        
        # Check iframe or video tags
        iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', vhtml)
        print('Iframes on video page:', iframes)
        
        # Check video tags
        video_srcs = re.findall(r'<source[^>]+src="([^"]+)"', vhtml)
        print('Video sources on video page:', video_srcs)
        
        # Check direct mp4 or m3u8
        direct = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', vhtml)
        print('Direct stream matches:', direct[:3])

except Exception as e:
    print('Error:', e)

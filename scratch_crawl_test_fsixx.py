import urllib.request
import re
import json
import base64
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://www.fsiblogxx.com/'}

def get_page_videos(page):
    url = f'https://www.fsiblogxx.com/porn-videos/page/{page}/' if page > 1 else 'https://www.fsiblogxx.com/porn-videos/'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
        vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit', 'privacy', 'terms', 'dmca'])]
        return vids
    except Exception as e:
        print(f"Error page {page}: {e}")
        return []

def extract_video_details(v_url):
    req = urllib.request.Request(v_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            
        title_m = re.search(r'<title>(.*?)</title>', html)
        raw_title = title_m.group(1).replace(' - FSI Blog', '').replace(' - FSIBlog', '').strip() if title_m else 'Desi MMS'
        
        # Check clean-tube-player iframe with base64 q param
        # Example: player-x.php?q=cG9zdF9pZD0...
        q_match = re.search(r'player-x\.php\?q=([a-zA-Z0-9+/=]+)', html)
        stream_url = ""
        poster_url = ""
        
        if q_match:
            try:
                decoded = base64.b64decode(q_match.group(1)).decode('utf-8', errors='ignore')
                unquoted = urllib.parse.unquote(decoded)
                src_m = re.search(r'src="([^"]+\.mp4[^"]*)"', unquoted)
                if src_m:
                    stream_url = src_m.group(1)
                poster_m = re.search(r'poster="([^"]+)"', unquoted)
                if poster_m:
                    poster_url = poster_m.group(1)
            except Exception:
                pass
                
        if not stream_url:
            mp4_m = re.search(r'(https://cdn\.fsiblogxx\.com/[^\s"\'<>]+\.mp4)', html)
            if mp4_m:
                stream_url = mp4_m.group(1)
                
        if not poster_url:
            post_m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if post_m:
                poster_url = post_m.group(1)
                
        if stream_url:
            slug = v_url.rstrip('/').split('/')[-1]
            vid_id = f"fsixx_{slug}"
            return {
                "id": vid_id,
                "name": raw_title,
                "stream_url": stream_url,
                "poster": poster_url,
                "thumbnail": poster_url,
                "page_url": v_url,
                "quality": "480p+"
            }
    except Exception as e:
        pass
    return None

def main():
    print("Testing 3 pages extraction...")
    video_urls = []
    for p in range(1, 4):
        vids = get_page_videos(p)
        video_urls.extend(vids)
        print(f"Page {p}: found {len(vids)} URLs")
        
    print(f"Total video URLs to fetch: {len(video_urls)}")
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(extract_video_details, video_urls):
            if res:
                results.append(res)
                
    print(f"Successfully extracted {len(results)} direct MP4 streams from fsiblogxx.com!")
    if results:
        print("Sample item 1:")
        print(json.dumps(results[0], indent=2))

if __name__ == "__main__":
    main()

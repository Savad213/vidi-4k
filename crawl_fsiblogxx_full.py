import urllib.request
import re
import json
import base64
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.fsiblogxx.com/'
}

REPO_ROOT = Path(__file__).parent
OUTPUT_FILE = REPO_ROOT / "fsiblogxx_all.json"

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
        print(f"Error on page {page}: {e}")
        return []

def extract_video_details(v_url):
    req = urllib.request.Request(v_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            
        title_m = re.search(r'<title>(.*?)</title>', html)
        raw_title = title_m.group(1).replace(' - FSI Blog', '').replace(' - FSIBlog', '').replace(' -', '').strip() if title_m else 'Desi MMS'
        
        stream_url = ""
        poster_url = ""
        
        # Check clean-tube-player iframe with base64 q param
        q_match = re.search(r'player-x\.php\?q=([a-zA-Z0-9+/=]+)', html)
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
    except Exception:
        pass
    return None

def main():
    print("=== Harvesting fsiblogxx.com (25 Pages) ===")
    video_urls = []
    # Collect 25 pages (25 * 26 ~ 650 videos)
    for p in range(1, 26):
        vids = get_page_videos(p)
        video_urls.extend(vids)
        if p % 5 == 0:
            print(f"  Page {p}/25 collected... ({len(video_urls)} URLs so far)")
            
    # Deduplicate URLs
    unique_urls = list(dict.fromkeys(video_urls))
    print(f"Total unique video pages to extract: {len(unique_urls)}")
    
    results = []
    seen_ids = set()
    
    with ThreadPoolExecutor(max_workers=12) as ex:
        for idx, res in enumerate(ex.map(extract_video_details, unique_urls), 1):
            if res and res["id"] not in seen_ids:
                seen_ids.add(res["id"])
                results.append(res)
            if idx % 100 == 0:
                print(f"  Processed {idx}/{len(unique_urls)} pages ({len(results)} valid MP4 streams)")
                
    print(f"\n✅ Total successfully extracted from fsiblogxx.com: {len(results)} items")
    OUTPUT_FILE.write_text(json.dumps({"count": len(results), "items": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

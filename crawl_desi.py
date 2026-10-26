"""
FSIBlog Desi MMS Crawler
Harvests authentic Desi MMS, phonecam, and leak streams from fsiblog.co.im
"""

import urllib.request
import re
import ssl
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).parent
OUTPUT_FILE = REPO_ROOT / "desi_all.json"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

TAGS = [
    'https://fsiblog.co.im/tag/viral-leaks/',
    'https://fsiblog.co.im/tag/desi-mms/',
    'https://fsiblog.co.im/tag/indian-mms/',
    'https://fsiblog.co.im/tag/girlfriend/',
    'https://fsiblog.co.im/tag/wife/',
    'https://fsiblog.co.im/tag/bhabhi/',
    'https://fsiblog.co.im/tag/mallu/',
    'https://fsiblog.co.im/tag/tamil/',
    'https://fsiblog.co.im/tag/striptease/',
    'https://fsiblog.co.im/tag/teasing/',
    'https://fsiblog.co.im/tag/influencer/',
    'https://fsiblog.co.im/tag/instagram/',
    'https://fsiblog.co.im/tag/snapchat/',
    'https://fsiblog.co.im/tag/bathroom/',
    'https://fsiblog.co.im/tag/newly-married/',
    'https://fsiblog.co.im/category/exclusive/',
    'https://fsiblog.co.im/category/4k/',
]

MAX_PAGES_PER_TAG = 8

def fetch_url(url, retries=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(0.3)
    return ""

def crawl_tag_pages(base_tag_url):
    watch_urls = set()
    for page in range(1, MAX_PAGES_PER_TAG + 1):
        if page == 1:
            u = base_tag_url
        else:
            u = f"{base_tag_url.rstrip('/')}/page/{page}"
        html = fetch_url(u)
        if not html:
            break
        links = re.findall(r'href=["\'](https://fsiblog\.co\.im/watch/[^"\'?#]+)', html)
        if not links:
            break
        watch_urls.update(links)
    return watch_urls

def parse_watch_page(url):
    html = fetch_url(url)
    if not html:
        return None
    
    vid_match = re.search(r'/watch/([^/]+)/?', url)
    if not vid_match:
        return None
    vid_id = vid_match.group(1)
    
    # Title
    t_match = re.search(r'<title>(.*?)(?:\s*\|\s*FSIBlog)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else "Desi MMS"
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    clean_title = clean_title.replace('&amp;', '&').replace('&quot;', '"')
    
    # Direct Cloudflare CDN MP4
    mp4_match = re.search(r'(https://[^\s"\'<>]+\.mp4)', html)
    if not mp4_match:
        return None
    mp4_url = mp4_match.group(1)
    
    # Thumbnail
    thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    thumb = thumb_match.group(1) if thumb_match else ""
    
    # Tags
    tags = list(set(re.findall(r'/tag/([^/"]+)/', html)))
    
    return {
        "id": f"desi_{vid_id}",
        "name": clean_title,
        "title": f"{clean_title} [480p+ Desi MMS]",
        "stream_url": mp4_url,
        "url": mp4_url,
        "poster": thumb,
        "thumbnail": thumb,
        "logo": thumb,
        "tags": tags,
        "quality": "480p+",
        "orientation": "vertical" if any(k in clean_title.lower() for k in ["reel", "phone", "strip", "tease", "snap"]) else "mobile",
        "runtime": "MMS",
        "source": "fsiblog",
        "page_url": url,
    }

def main():
    print("=== Phase 1: Collecting watch URLs across tags ===")
    all_watch_urls = set()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(crawl_tag_pages, t): t for t in TAGS}
        for f in as_completed(futures):
            tag = futures[f]
            try:
                res = f.result()
                print(f"  {tag.split('/')[-2]}: {len(res)} URLs")
                all_watch_urls.update(res)
            except Exception as e:
                print(f"  Error crawling {tag}: {e}")

    print(f"\nTotal unique video pages discovered: {len(all_watch_urls)}")
    
    print("\n=== Phase 2: Extracting video streams in parallel ===")
    video_records = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(parse_watch_page, u): u for u in all_watch_urls}
        done = 0
        total = len(futures)
        for f in as_completed(futures):
            done += 1
            if done % 50 == 0 or done == total:
                print(f"  Progress: {done}/{total} ({len(video_records)} valid streams found)")
            res = f.result()
            if res:
                video_records.append(res)

    print(f"\nSuccessfully harvested {len(video_records)} valid direct CDN streams!")
    
    # Save to desi_all.json
    OUTPUT_FILE.write_text(json.dumps({
        "playlist_name": "FSIBlog Desi MMS Master Collection",
        "type": "playlist",
        "count": len(video_records),
        "items": video_records
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"Saved to {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()

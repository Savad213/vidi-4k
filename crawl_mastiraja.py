"""
Mastiraja Desi MMS & Viral Leaks Crawler
Extracts direct high-bitrate MP4 streams (3.12 Mbps) from mastiraja.tv
"""

import urllib.request
import urllib.parse
import base64
import re
import ssl
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).parent
OUTPUT_FILE = REPO_ROOT / "mastiraja_all.json"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

CATEGORIES = [
    'https://mastiraja.tv/category/viral-leaks/',
    'https://mastiraja.tv/category/amateur/',
    'https://mastiraja.tv/category/bathroom/',
    'https://mastiraja.tv/category/bhabhi/',
    'https://mastiraja.tv/category/cheating-wife/',
    'https://mastiraja.tv/category/desi-creators/',
]

MAX_PAGES = 5

def fetch_url(url, retries=2):
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(0.3)
    return ""

def crawl_cat_pages(cat_url):
    posts = set()
    for page in range(1, MAX_PAGES + 1):
        u = f"{cat_url.rstrip('/')}/page/{page}/" if page > 1 else cat_url
        html = fetch_url(u)
        if not html:
            break
        links = re.findall(r'href=["\'](https://mastiraja\.tv/[a-zA-Z0-9\-]+/)["\']', html)
        valid = [l for l in links if not any(x in l for x in ['/category/', '/tag/', '/author/', '/page/', '/wp-', '/feed/'])]
        if not valid:
            break
        posts.update(valid)
    return posts

def parse_mastiraja_post(url):
    html = fetch_url(url)
    if not html:
        return None
    
    slug_match = re.search(r'mastiraja\.tv/([^/]+)/?', url)
    if not slug_match:
        return None
    slug = slug_match.group(1)
    
    # Title
    t_match = re.search(r'<title>(.*?)(?:\s*[-–|]\s*Mastiraja)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else slug.replace('-', ' ').title()
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    
    # Direct MP4 encoded inside player-x.php?q=
    q_match = re.search(r'player-x\.php\?q=([a-zA-Z0-9+/=]+)', html)
    mp4_url = ""
    poster_url = ""
    
    if q_match:
        try:
            raw_b64 = q_match.group(1)
            decoded = urllib.parse.unquote(base64.b64decode(raw_b64).decode('utf-8', errors='ignore'))
            m_mp4 = re.search(r'src=["\'](https?://[^"\']+\.mp4)', decoded)
            if m_mp4:
                mp4_url = m_mp4.group(1)
            m_pos = re.search(r'poster=["\'](https?://[^"\']+\.(?:png|jpg|webp|jpeg))', decoded)
            if m_pos:
                poster_url = m_pos.group(1)
        except Exception:
            pass

    # Fallback to standard og:image and direct mp4 regex
    if not mp4_url:
        m_mp4_fallback = re.search(r'(https?://[^\s"\'<>]+\.mp4)', html)
        if m_mp4_fallback:
            mp4_url = m_mp4_fallback.group(1)

    if not poster_url:
        m_thumb = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if m_thumb:
            poster_url = m_thumb.group(1)

    if not mp4_url:
        return None

    return {
        "id": f"masti_{slug}",
        "name": clean_title,
        "title": f"{clean_title} [High Bitrate Desi MMS]",
        "stream_url": mp4_url,
        "url": mp4_url,
        "poster": poster_url,
        "thumbnail": poster_url,
        "logo": poster_url,
        "tags": ["mastiraja", "desi", "mms", "viral-leak", "amateur"],
        "quality": "480p+",
        "orientation": "mobile",
        "runtime": "MMS",
        "source": "mastiraja",
        "page_url": url,
    }

def main():
    print("=== Phase 1: Collecting Mastiraja Post URLs ===")
    all_post_urls = set()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(crawl_cat_pages, c): c for c in CATEGORIES}
        for f in as_completed(futures):
            cat = futures[f]
            try:
                res = f.result()
                print(f"  {cat.split('/')[-2]}: {len(res)} posts")
                all_post_urls.update(res)
            except Exception as e:
                print(f"  Error crawling {cat}: {e}")

    print(f"\nTotal unique Mastiraja posts discovered: {len(all_post_urls)}")

    print("\n=== Phase 2: Extracting Direct MP4 Streams ===")
    records = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(parse_mastiraja_post, u): u for u in all_post_urls}
        done = 0
        total = len(futures)
        for f in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == total:
                print(f"  Progress: {done}/{total} ({len(records)} direct streams extracted)")
            res = f.result()
            if res:
                records.append(res)

    print(f"\nSuccessfully harvested {len(records)} Mastiraja direct streams!")
    
    OUTPUT_FILE.write_text(json.dumps({
        "source": "mastiraja",
        "count": len(records),
        "items": records
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved to {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()

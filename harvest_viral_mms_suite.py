"""
Comprehensive Viral MMS & Pakistani Crawler
Harvests authentic Desi MMS, phone leaks, and Pakistani viral leaks from mastiraja.tv and fsiblog.co.im
Decodes high-bitrate direct MP4 streams and populates mastiraja_all.json, desi_all.json, and pakistani_all.json.
"""

import urllib.request
import urllib.parse
import ssl
import re
import json
import base64
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).resolve().parent
MASTI_FILE = REPO_ROOT / "mastiraja_all.json"
DESI_FILE = REPO_ROOT / "desi_all.json"
PAKI_FILE = REPO_ROOT / "pakistani_all.json"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Negative filter patterns
DISALLOWED_PATTERNS = [
    re.compile(r"(?i)\b(pregnant|pregnancy|baby\s*bump|expecting)\b"),
    re.compile(r"(?i)\b(ebony|black\s*girl|black\s*woman|dark\s*skin)\b"),
    re.compile(r"(?i)\b(granny|mature|gilf|grandma|old\s*woman|elderly|wrinkled)\b"),
    re.compile(r"(?i)\b(anime|hentai|3d|cartoon|animation|animated|sfm|blender|cosplay)\b"),
    re.compile(r"(?i)\b(skinny|very\s*thin|bony|petite|tiny|small\s*tits|small\s*boobs|flat)\b"),
    re.compile(r"(?i)\b(bdsm|torture|bondage|tied|abuse|punish\w*|slave|submissive)\b"),
    re.compile(r"(?i)\b(shemale|trans|tranny|ladyboy|gay)\b"),
    re.compile(r"(?i)\b(pissing|urine|watersport|scat|feet|footfetish)\b"),
]

PAKI_PAT = re.compile(r"(?i)\b(pakistan|pakistani|lahore|karachi|islamabad|rawalpindi|peshawar|punjabi|pathan|minahil|alina|imsha|alisha|ayesha|zartaj|marry)\b")

def is_clean(title, tags=None):
    txt = f"{title} {' '.join(tags or [])}"
    for pat in DISALLOWED_PATTERNS:
        if pat.search(txt):
            return False
    return True

def fetch_html(url, retries=2, timeout=8):
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(0.3)
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# 1. MASTIRAJA HARVESTING
# ─────────────────────────────────────────────────────────────────────────────

MASTIRAJA_SECTIONS = [
    ('cat', 'https://mastiraja.tv/category/viral-leaks/', 6),
    ('cat', 'https://mastiraja.tv/category/pakistani-sex/', 5),
    ('cat', 'https://mastiraja.tv/category/desi-creators/', 5),
    ('cat', 'https://mastiraja.tv/category/bhabhi/', 5),
    ('cat', 'https://mastiraja.tv/category/bathroom/', 5),
    ('cat', 'https://mastiraja.tv/category/amateur/', 5),
    ('cat', 'https://mastiraja.tv/category/aunty/', 4),
    ('cat', 'https://mastiraja.tv/category/cheating-wife/', 4),
    ('cat', 'https://mastiraja.tv/category/sexy-girl/', 4),
    ('search', 'https://mastiraja.tv/?s=mms', 4),
    ('search', 'https://mastiraja.tv/?s=viral', 4),
    ('search', 'https://mastiraja.tv/?s=pakistani', 4),
    ('search', 'https://mastiraja.tv/?s=leak', 4),
    ('search', 'https://mastiraja.tv/?s=scandal', 3),
    ('search', 'https://mastiraja.tv/?s=call', 3),
    ('search', 'https://mastiraja.tv/?s=hotel', 3),
]

def crawl_mastiraja_section(kind, base_url, max_p):
    posts = set()
    for p in range(1, max_p + 1):
        if kind == 'search':
            u = f"{base_url}&paged={p}" if p > 1 else base_url
        else:
            u = f"{base_url.rstrip('/')}/page/{p}/" if p > 1 else base_url
        html = fetch_html(u)
        if not html:
            break
        links = set(re.findall(r'href=[\'"](https://mastiraja\.tv/[a-zA-Z0-9\-]+/)[\'"]', html))
        valid = [l for l in links if not any(x in l for x in ['/category/', '/tag/', '/author/', '/page/', '/wp-', '/feed/'])]
        if not valid:
            break
        posts.update(valid)
    return posts

def parse_mastiraja_post(url):
    html = fetch_html(url)
    if not html:
        return None
    slug_match = re.search(r'mastiraja\.tv/([^/]+)/?', url)
    if not slug_match:
        return None
    slug = slug_match.group(1)
    
    t_match = re.search(r'<title>(.*?)(?:\s*[-–|]\s*Mastiraja)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else slug.replace('-', ' ').title()
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    clean_title = clean_title.replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'").strip()
    
    if not is_clean(clean_title):
        return None

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

    if not mp4_url:
        m_mp4_fallback = re.search(r'(https?://[^\s"\'<>]+\.mp4)', html)
        if m_mp4_fallback:
            mp4_url = m_mp4_fallback.group(1)

    if not poster_url:
        m_thumb = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if m_thumb:
            poster_url = m_thumb.group(1)

    if not mp4_url or not mp4_url.startswith("http"):
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

# ─────────────────────────────────────────────────────────────────────────────
# 2. FSIBLOG HARVESTING
# ─────────────────────────────────────────────────────────────────────────────

FSIBLOG_TAGS = [
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
    'https://fsiblog.co.im/tag/bathroom/',
    'https://fsiblog.co.im/tag/newly-married/',
    'https://fsiblog.co.im/category/exclusive/',
    'https://fsiblog.co.im/tag/snapchat/',
]

def crawl_fsiblog_tag(base_url, max_p=6):
    watch_urls = set()
    for p in range(1, max_p + 1):
        u = f"{base_url.rstrip('/')}/page/{p}" if p > 1 else base_url
        html = fetch_html(u)
        if not html:
            break
        links = re.findall(r'href=["\'](https://fsiblog\.co\.im/watch/[^"\'?#]+)', html)
        if not links:
            break
        watch_urls.update(links)
    return watch_urls

def parse_fsiblog_post(url):
    html = fetch_html(url)
    if not html:
        return None
    vid_match = re.search(r'/watch/([^/]+)/?', url)
    if not vid_match:
        return None
    vid_id = vid_match.group(1)
    
    t_match = re.search(r'<title>(.*?)(?:\s*\|\s*FSIBlog)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else "Desi MMS"
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    clean_title = clean_title.replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'").strip()
    
    tags = list(set(re.findall(r'/tag/([^/"]+)/', html)))
    if not is_clean(clean_title, tags):
        return None

    mp4_match = re.search(r'(https://[^\s"\'<>]+\.mp4)', html)
    if not mp4_match:
        return None
    mp4_url = mp4_match.group(1)
    
    # Don't accept dead or expired fsiblogxx cdn
    if "cdn.fsiblogxx.com" in mp4_url:
        return None

    thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    thumb = thumb_match.group(1) if thumb_match else ""

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
        "orientation": "vertical" if any(k in clean_title.lower() for k in ["reel", "phone", "strip", "tease", "snap", "call"]) else "mobile",
        "runtime": "MMS",
        "source": "fsiblog",
        "page_url": url,
    }

# ─────────────────────────────────────────────────────────────────────────────
# 3. ORCHESTRATION & STORAGE
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("DEEP VIRAL MMS & PAKISTANI HARVESTER")
    print("=" * 70)

    # 1. Collect Mastiraja links
    print("\n--- Phase 1A: Discovering Mastiraja Posts ---")
    masti_post_urls = set()
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(crawl_mastiraja_section, k, u, p): u for k, u, p in MASTIRAJA_SECTIONS}
        for f in as_completed(futures):
            res = f.result()
            print(f"  Discovered {len(res):3} posts from {futures[f].split('?')[0].split('/')[-2] or futures[f]}")
            masti_post_urls.update(res)
    print(f"Total unique Mastiraja post URLs: {len(masti_post_urls)}")

    # 2. Collect FSIBlog links
    print("\n--- Phase 1B: Discovering FSIBlog Posts ---")
    fsi_post_urls = set()
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(crawl_fsiblog_tag, u, 6): u for u in FSIBLOG_TAGS}
        for f in as_completed(futures):
            res = f.result()
            print(f"  Discovered {len(res):3} watch links from {futures[f].rstrip('/').split('/')[-1]}")
            fsi_post_urls.update(res)
    print(f"Total unique FSIBlog post URLs: {len(fsi_post_urls)}")

    # 3. Parse Mastiraja Posts
    print(f"\n--- Phase 2A: Extracting Direct Streams from {len(masti_post_urls)} Mastiraja Posts ---")
    masti_records = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(parse_mastiraja_post, u): u for u in masti_post_urls}
        done = 0
        total = len(futures)
        for f in as_completed(futures):
            done += 1
            if done % 50 == 0 or done == total:
                print(f"  Mastiraja progress: {done}/{total} ({len(masti_records)} streams extracted)")
            r = f.result()
            if r:
                masti_records.append(r)
    print(f"Harvested {len(masti_records)} valid Mastiraja stream items.")

    # 4. Parse FSIBlog Posts
    print(f"\n--- Phase 2B: Extracting Direct Streams from {len(fsi_post_urls)} FSIBlog Posts ---")
    fsi_records = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(parse_fsiblog_post, u): u for u in fsi_post_urls}
        done = 0
        total = len(futures)
        for f in as_completed(futures):
            done += 1
            if done % 50 == 0 or done == total:
                print(f"  FSIBlog progress: {done}/{total} ({len(fsi_records)} streams extracted)")
            r = f.result()
            if r:
                fsi_records.append(r)
    print(f"Harvested {len(fsi_records)} valid FSIBlog stream items.")

    # 5. Merge and Save to disk
    print("\n--- Phase 3: Merging & Updating Datasets ---")

    # Load existing datasets
    existing_masti = json.loads(MASTI_FILE.read_text(encoding="utf-8")) if MASTI_FILE.exists() else {"items": []}
    masti_items = existing_masti.get("items", []) if isinstance(existing_masti, dict) else existing_masti
    masti_map = {it["id"]: it for it in masti_items}
    for r in masti_records:
        masti_map[r["id"]] = r
    updated_masti = list(masti_map.values())
    MASTI_FILE.write_text(json.dumps({"source": "mastiraja", "count": len(updated_masti), "items": updated_masti}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Mastiraja dataset updated: {len(masti_items)} -> {len(updated_masti)} items in {MASTI_FILE.name}")

    existing_desi = json.loads(DESI_FILE.read_text(encoding="utf-8")) if DESI_FILE.exists() else {"items": []}
    desi_items = existing_desi.get("items", []) if isinstance(existing_desi, dict) else existing_desi
    desi_map = {it["id"]: it for it in desi_items}
    for r in fsi_records:
        desi_map[r["id"]] = r
    updated_desi = list(desi_map.values())
    DESI_FILE.write_text(json.dumps({"source": "desi_pool", "count": len(updated_desi), "items": updated_desi}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Desi dataset updated: {len(desi_items)} -> {len(updated_desi)} items in {DESI_FILE.name}")

    existing_paki = json.loads(PAKI_FILE.read_text(encoding="utf-8")) if PAKI_FILE.exists() else {"items": []}
    paki_items = existing_paki.get("items", []) if isinstance(existing_paki, dict) else existing_paki
    paki_map = {it["id"]: it for it in paki_items}
    for r in masti_records + fsi_records:
        txt = f"{r.get('name', '')} {' '.join(r.get('tags', []))}"
        if PAKI_PAT.search(txt):
            paki_map[r["id"]] = r
    updated_paki = list(paki_map.values())
    PAKI_FILE.write_text(json.dumps({"source": "pakistani_pool", "count": len(updated_paki), "items": updated_paki}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Pakistani dataset updated: {len(paki_items)} -> {len(updated_paki)} items in {PAKI_FILE.name}")

    print("\nHarvesting complete! Ready for rebuild.")

if __name__ == "__main__":
    main()

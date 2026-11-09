"""
High-Speed Concurrent Harvester for Desi MMS & Pakistani Leaks using curl_cffi
Bypasses Cloudflare TLS fingerprinting and streams direct MP4 links.
"""

import re
import json
import base64
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from curl_cffi import requests

REPO_ROOT = Path(__file__).resolve().parent

def log(msg):
    print(msg, flush=True)

def fetch_url(url, retries=2):
    for attempt in range(retries):
        try:
            r = requests.get(url, impersonate='chrome120', timeout=9)
            if r.status_code == 200:
                return r.text
        except Exception:
            time.sleep(0.2)
    return ""

# ─── PARSERS ─────────────────────────────────────────────────────────────────

def parse_fsiblog_page(v_url):
    html = fetch_url(v_url)
    if not html:
        return None
    vid_match = re.search(r'/watch/([^/]+)/?', v_url)
    if not vid_match:
        return None
    vid_id = vid_match.group(1)
    
    t_match = re.search(r'<title>(.*?)(?:\s*\|\s*FSIBlog)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else "Desi MMS"
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    clean_title = clean_title.replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'")
    
    mp4_match = re.search(r'(https://[^\s"\'<>]+\.mp4)', html)
    if not mp4_match:
        return None
    mp4_url = mp4_match.group(1)
    if "cdn.fsiblogxx.com" in mp4_url:
        return None
    
    thumb_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    thumb = thumb_match.group(1) if thumb_match else ""
    
    raw_tags = re.findall(r'href=["\']https://fsiblog\.co\.im/tag/([^"\'/?#]+)/?["\']', html)
    tags = list(set([t.replace('-', ' ').title() for t in raw_tags]))
    if not tags:
        tags = ["Desi", "MMS", "Viral"]
        
    is_paki = bool(re.search(r'(?i)\b(pakistan|pakistani|lahore|karachi|punjabi|pathan|rawalpindi|peshawar|islamabad)\b', f"{clean_title} {' '.join(tags)}"))
    if is_paki and "Pakistani" not in tags:
        tags.append("Pakistani")
        
    return {
        "id": f"desi_{vid_id}",
        "name": clean_title,
        "poster": thumb,
        "thumbnail": thumb,
        "stream_url": mp4_url,
        "quality": "720p HD",
        "resolution": "720p",
        "orientation": "horizontal",
        "runtime": "HD",
        "tags": tags,
        "source": "FSIBlog",
        "is_paki": is_paki
    }

def parse_mastiraja_page(v_url):
    html = fetch_url(v_url)
    if not html:
        return None
    slug_match = re.search(r'mastiraja\.tv/([^/]+)/?', v_url)
    if not slug_match:
        return None
    slug = slug_match.group(1)
    
    t_match = re.search(r'<title>(.*?)(?:\s*[-–|]\s*Mastiraja)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else slug.replace('-', ' ').title()
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    clean_title = clean_title.replace('&amp;', '&').replace('&quot;', '"').replace('&#039;', "'")
    
    mp4_url = ""
    poster_url = ""
    q_match = re.search(r'player-x\.php\?q=([a-zA-Z0-9+/=]+)', html)
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
            
    if not mp4_url or "cdn.fsiblogxx.com" in mp4_url:
        return None
        
    is_paki = bool(re.search(r'(?i)\b(pakistan|pakistani|lahore|karachi|punjabi|pathan|rawalpindi|peshawar|islamabad)\b', f"{clean_title} {v_url}"))
    tags = ["Mastiraja", "Desi", "MMS"]
    if is_paki:
        tags.append("Pakistani")
        
    return {
        "id": f"masti_paki_{slug}" if is_paki else f"masti_{slug}",
        "name": clean_title,
        "poster": poster_url,
        "thumbnail": poster_url,
        "stream_url": mp4_url,
        "quality": "720p HD",
        "resolution": "720p",
        "orientation": "horizontal",
        "runtime": "HD",
        "tags": tags,
        "source": "Mastiraja",
        "is_paki": is_paki
    }

# ─── URL DISCOVERY ───────────────────────────────────────────────────────────

def fetch_fsi_listing_page(url):
    html = fetch_url(url)
    if not html:
        return []
    return re.findall(r'href=["\'](https://fsiblog\.co\.im/watch/[^"\'?#]+)', html)

def fetch_masti_listing_page(url):
    html = fetch_url(url)
    if not html:
        return []
    links = re.findall(r'href=["\'](https://mastiraja\.tv/[a-zA-Z0-9\-]+/)["\']', html)
    return [l for l in links if not any(x in l for x in ['/category/', '/tag/', '/author/', '/page/', '/wp-', '/feed/'])]

def discover_all_urls():
    log("Building listing targets...")
    fsi_listing_urls = []
    
    # 1. FSIBlog Searches
    searches = [
        ('pakistani', 15),
        ('pakistan', 15),
        ('lahore', 10),
        ('karachi', 10),
        ('punjabi', 10),
        ('pathan', 8),
        ('rawalpindi', 6),
        ('peshawar', 6),
        ('islamabad', 6),
        ('viral+mms', 12),
        ('mms+leak', 10),
        ('scandal', 10),
        ('call+recording', 6),
        ('video+call', 6),
        ('hotel+room', 6),
    ]
    for term, max_p in searches:
        for p in range(1, max_p + 1):
            u = f"https://fsiblog.co.im/page/{p}/?s={term}" if p > 1 else f"https://fsiblog.co.im/?s={term}"
            fsi_listing_urls.append(u)

    # 2. FSIBlog Tags
    tag_list = [
        ('viral-leaks', 25),
        ('desi-mms', 25),
        ('indian-mms', 20),
        ('bhabhi', 20),
        ('girlfriend', 20),
        ('influencer', 15),
        ('instagram', 15),
        ('snapchat', 15),
        ('bathroom', 12),
    ]
    for tag, max_p in tag_list:
        for p in range(1, max_p + 1):
            u = f"https://fsiblog.co.im/tag/{tag}/page/{p}" if p > 1 else f"https://fsiblog.co.im/tag/{tag}/"
            fsi_listing_urls.append(u)

    # 3. FSIBlog Category Exclusive
    for p in range(1, 12):
        u = f"https://fsiblog.co.im/category/exclusive/page/{p}" if p > 1 else "https://fsiblog.co.im/category/exclusive/"
        fsi_listing_urls.append(u)

    # Mastiraja Listing URLs
    masti_listing_urls = []
    cats = [
        ('pakistani-sex', 5),
        ('viral-leaks', 6),
        ('amateur', 6),
        ('bhabhi', 6),
        ('bathroom', 6),
        ('cheating-wife', 6),
        ('desi-creators', 6),
    ]
    for cat, max_p in cats:
        for p in range(1, max_p + 1):
            u = f"https://mastiraja.tv/category/{cat}/page/{p}/" if p > 1 else f"https://mastiraja.tv/category/{cat}/"
            masti_listing_urls.append(u)

    masti_searches = [
        ('pakistani', 4),
        ('pakistan', 4),
        ('lahore', 4),
        ('karachi', 4),
        ('mms', 4),
        ('viral', 4),
        ('leak', 4),
    ]
    for term, max_p in masti_searches:
        for p in range(1, max_p + 1):
            u = f"https://mastiraja.tv/page/{p}/?s={term}" if p > 1 else f"https://mastiraja.tv/?s={term}"
            masti_listing_urls.append(u)

    log(f"Fetching {len(fsi_listing_urls)} FSIBlog and {len(masti_listing_urls)} Mastiraja listing pages concurrently (10 workers)...")
    
    unique_fsi = set()
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(fetch_fsi_listing_page, u): u for u in fsi_listing_urls}
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 50 == 0 or done == len(fsi_listing_urls):
                log(f"  FSIBlog listings fetched: {done}/{len(fsi_listing_urls)} (Found {len(unique_fsi)} unique video links so far)")
            res = f.result()
            if res:
                unique_fsi.update(res)

    unique_masti = set()
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(fetch_masti_listing_page, u): u for u in masti_listing_urls}
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == len(masti_listing_urls):
                log(f"  Mastiraja listings fetched: {done}/{len(masti_listing_urls)} (Found {len(unique_masti)} unique video links so far)")
            res = f.result()
            if res:
                unique_masti.update(res)

    log(f"\nDiscovery Done: {len(unique_fsi)} unique FSIBlog URLs, {len(unique_masti)} unique Mastiraja URLs.")
    return unique_fsi, unique_masti

# ─── MAIN HARVEST ─────────────────────────────────────────────────────────────

def harvest_all():
    log("=" * 70)
    log("MASS HARVEST FOR DESI MMS & PAKISTANI VIDEOS")
    log("=" * 70)
    
    desi_path = REPO_ROOT / "desi_all.json"
    paki_path = REPO_ROOT / "pakistani_all.json"
    masti_path = REPO_ROOT / "mastiraja_all.json"
    
    desi_data = json.loads(desi_path.read_text(encoding="utf-8")) if desi_path.exists() else {"items": []}
    paki_data = json.loads(paki_path.read_text(encoding="utf-8")) if paki_path.exists() else {"items": []}
    masti_data = json.loads(masti_path.read_text(encoding="utf-8")) if masti_path.exists() else {"items": []}
    
    existing_streams = set()
    existing_ids = set()
    
    for coll in [desi_data.get("items", []), paki_data.get("items", []), masti_data.get("items", [])]:
        for it in coll:
            if it.get("stream_url"):
                existing_streams.add(it["stream_url"])
            if it.get("id"):
                existing_ids.add(it["id"])
                
    log(f"Existing in datasets: {len(existing_ids)} IDs, {len(existing_streams)} streams")
    
    fsi_urls, masti_urls = discover_all_urls()
    
    new_fsi_urls = [u for u in fsi_urls if not any(slug in u for slug in existing_ids)]
    new_masti_urls = [u for u in masti_urls if not any(slug.replace('masti_', '') in u for slug in existing_ids)]
    
    log(f"\nNew targets to extract: {len(new_fsi_urls)} FSIBlog pages, {len(new_masti_urls)} Mastiraja pages")
    
    # Extract FSIBlog
    log(f"\n--- Extracting FSIBlog pages with 10 workers ---")
    new_desi_items = []
    new_paki_items = []
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(parse_fsiblog_page, u): u for u in new_fsi_urls}
        done_cnt = 0
        for f in as_completed(futures):
            done_cnt += 1
            if done_cnt % 50 == 0 or done_cnt == len(new_fsi_urls):
                log(f"  FSIBlog extracted {done_cnt}/{len(new_fsi_urls)}... (New Desi: {len(new_desi_items)}, New Paki: {len(new_paki_items)})")
            res = f.result()
            if not res:
                continue
            st = res.get("stream_url")
            vid_id = res.get("id")
            if not st or st in existing_streams or vid_id in existing_ids:
                continue
            existing_streams.add(st)
            existing_ids.add(vid_id)
            if res.get("is_paki"):
                new_paki_items.append(res)
            new_desi_items.append(res)
            
    # Extract Mastiraja
    log(f"\n--- Extracting Mastiraja pages with 10 workers ---")
    new_masti_items = []
    
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(parse_mastiraja_page, u): u for u in new_masti_urls}
        done_cnt = 0
        for f in as_completed(futures):
            done_cnt += 1
            if done_cnt % 30 == 0 or done_cnt == len(new_masti_urls):
                log(f"  Mastiraja extracted {done_cnt}/{len(new_masti_urls)}... (New: {len(new_masti_items)}, New Paki: {sum(1 for x in new_masti_items if x.get('is_paki'))})")
            res = f.result()
            if not res:
                continue
            st = res.get("stream_url")
            vid_id = res.get("id")
            if not st or st in existing_streams or vid_id in existing_ids:
                continue
            existing_streams.add(st)
            existing_ids.add(vid_id)
            new_masti_items.append(res)
            if res.get("is_paki"):
                new_paki_items.append(res)
                
    # Save
    desi_data["items"].extend(new_desi_items)
    paki_data["items"].extend(new_paki_items)
    masti_data["items"].extend(new_masti_items)
    
    desi_path.write_text(json.dumps(desi_data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    paki_path.write_text(json.dumps(paki_data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    masti_path.write_text(json.dumps(masti_data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    
    log("\n" + "=" * 70)
    log("HARVEST COMPLETE & SAVED:")
    log(f"  desi_all.json       : {len(desi_data['items'])} total items (+{len(new_desi_items)} newly added)")
    log(f"  pakistani_all.json  : {len(paki_data['items'])} total items (+{len(new_paki_items)} newly added)")
    log(f"  mastiraja_all.json  : {len(masti_data['items'])} total items (+{len(new_masti_items)} newly added)")
    log("=" * 70)

if __name__ == '__main__':
    harvest_all()

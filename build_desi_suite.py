import os
import sys
import json
import re
import base64
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import hashlib

BASE_DIR = r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\_active\vidi-4k\desi"
os.makedirs(os.path.join(BASE_DIR, "catalog", "movie"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "meta", "movie"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "stream", "movie"), exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

SKINNY_FLAT_PAT = re.compile(r'\b(skinny|petite|flat[\s\-]chest|tiny\b|bony|anorexic)\b', re.IGNORECASE)
BLACK_EBONY_PAT = re.compile(r'\b(ebony|black\s*girl|african|bbc)\b', re.IGNORECASE)

def clean_title(title):
    t = re.sub(r'[\r\n\t]+', ' ', title)
    t = re.sub(r'\s*&#8211;\s*Masti\s*Raja.*$', '', t, flags=re.I)
    t = re.sub(r'\s*-\s*Masti\s*Raja.*$', '', t, flags=re.I)
    t = re.sub(r'\s*\|\s*FSIBlog.*$', '', t, flags=re.I)
    t = re.sub(r'\s*-\s*FSIBlog.*$', '', t, flags=re.I)
    t = t.replace('&amp;', '&').replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8217;', "'").replace('&#8216;', "'").replace('&#8211;', '-')
    return t.strip()

def extract_mastiraja_post(post_url):
    try:
        req = urllib.request.Request(post_url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
        
        t_m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = clean_title(t_m.group(1)) if t_m else ''
        
        match = re.search(r'src=[\'"][^\'"]*player-x\.php\?q=([^\'"]+)[\'"]', html)
        video_url = None
        poster_url = None
        
        if match:
            decoded = urllib.parse.unquote(base64.b64decode(match.group(1)).decode('utf-8', errors='ignore'))
            src_m = re.search(r'src="([^"]+)"', decoded)
            pos_m = re.search(r'poster="([^"]+)"', decoded)
            if src_m:
                video_url = src_m.group(1).replace('videos.mastiraja.com', 'videos.mastiraja.tv')
            if pos_m:
                poster_url = pos_m.group(1)
                
        if not video_url:
            mp4s = re.findall(r'https?://videos\.mastiraja\.(?:tv|io|com)/[^\s\'"<>]+?\.mp4', html)
            if mp4s:
                video_url = mp4s[0].replace('videos.mastiraja.com', 'videos.mastiraja.tv')
                
        if not poster_url:
            og_m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
            if og_m:
                poster_url = og_m.group(1)
                
        if video_url and poster_url and title:
            if SKINNY_FLAT_PAT.search(title) or BLACK_EBONY_PAT.search(title):
                return None
            return {
                'title': title,
                'video_url': video_url,
                'poster_url': poster_url,
                'source': 'mastiraja',
                'page_url': post_url
            }
    except Exception:
        pass
    return None

def extract_fsiblog_post(watch_url):
    try:
        req = urllib.request.Request(watch_url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
        
        t_m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = clean_title(t_m.group(1)) if t_m else ''
        
        video_m = re.search(r'<source[^>]+src=[\'"]([^\'"]+?\.mp4[^\'"]*)[\'"]', html)
        if not video_m:
            video_m = re.search(r'https?://oneplay\.ltdcdn\.cloud/[^\s\'"<>]+?\.mp4', html)
        video_url = video_m.group(1) if hasattr(video_m, 'group') and video_m.lastindex else (video_m.group(0) if video_m else None)
        
        poster_m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
        if not poster_m:
            poster_m = re.search(r'poster=[\'"]([^\'"]+)[\'"]', html)
        poster_url = poster_m.group(1) if poster_m else None
        
        if video_url and poster_url and title:
            if SKINNY_FLAT_PAT.search(title) or BLACK_EBONY_PAT.search(title):
                return None
            return {
                'title': title,
                'video_url': video_url,
                'poster_url': poster_url,
                'source': 'fsiblog',
                'page_url': watch_url
            }
    except Exception:
        pass
    return None

def harvest_links_mastiraja(cat_url, pages=5):
    post_links = []
    for p in range(1, pages + 1):
        url = cat_url if p == 1 else f"{cat_url.rstrip('/')}/page/{p}/"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            links = re.findall(r'<a\s+href="(https://mastiraja\.tv/[a-z0-9\-]+(?:-[a-z0-9\-]+)+/)"', html)
            valid = [l for l in links if not any(x in l for x in ['/category/', '/tag/', '/page/', '/wp-', '/author/', '/feed/'])]
            post_links.extend(valid)
        except Exception:
            pass
    return list(set(post_links))

def harvest_links_fsiblog(tag_url, pages=5):
    watch_links = []
    for p in range(1, pages + 1):
        url = tag_url if p == 1 else f"{tag_url.rstrip('/')}/page/{p}/"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=[\'"](https://fsiblog\.co\.im/watch/[^\'"]+)[\'"]', html)
            watch_links.extend(links)
        except Exception:
            pass
    return list(set(watch_links))

def build_all():
    print("[1/5] Harvesting target category links...")
    
    # 4 explicit reference URLs
    user_refs = [
        "https://mastiraja.tv/cafe-couple-viral-boob-play/",
        "https://mastiraja.tv/bossy-girl-mms-leak-ride/",
        "https://mastiraja.tv/cuck-bf-records-his-busty-girl-obsessed-with-dicks-get-fucked-by-his-friend-after-enjoying-her-fully/",
        "https://mastiraja.tv/tanker-girl-live-ass-finger/"
    ]
    
    cat_sources = {
        "desi_bathroom": [
            ("mastiraja", "https://mastiraja.tv/category/bathroom/", 8),
            ("mastiraja", "https://mastiraja.tv/tag/bathroom-sex/", 6)
        ],
        "desi_couples_viral": [
            ("mastiraja", "https://mastiraja.tv/tag/desi-mms/", 8),
            ("mastiraja", "https://mastiraja.tv/tag/desi-couple-sex/", 6),
            ("mastiraja", "https://mastiraja.tv/tag/chudai-mms-leaks/", 6),
            ("mastiraja", "https://mastiraja.tv/tag/celebrity-leak/", 6),
            ("fsiblog", "https://fsiblog.co.im/tag/viral-leaks/", 6)
        ],
        "desi_amateur_cuck": [
            ("mastiraja", "https://mastiraja.tv/category/amateur/", 8),
            ("mastiraja", "https://mastiraja.tv/category/pakistani-sex/", 8),
            ("mastiraja", "https://mastiraja.tv/tag/cheating-indian-wife-mms/", 6)
        ],
        "desi_tease_live": [
            ("fsiblog", "https://fsiblog.co.im/tag/teasing/", 6),
            ("mastiraja", "https://mastiraja.tv/tag/desi-tease/", 6),
            ("mastiraja", "https://mastiraja.tv/tag/boob-tease/", 6),
            ("mastiraja", "https://mastiraja.tv/tag/college-girl/", 6)
        ]
    }
    
    catalog_items = {k: [] for k in cat_sources}
    all_videos = {}
    
    # Harvest explicit refs first
    print("Harvesting user references...")
    for ref_url in user_refs:
        item = extract_mastiraja_post(ref_url)
        if item:
            vid_id = "desi_" + hashlib.md5(item['video_url'].encode()).hexdigest()[:12]
            item['id'] = vid_id
            all_videos[vid_id] = item
            if "tanker" in item['title'].lower() or "live" in item['title'].lower():
                catalog_items["desi_tease_live"].insert(0, item)
            elif "cuck" in item['title'].lower() or "friend" in item['title'].lower():
                catalog_items["desi_amateur_cuck"].insert(0, item)
            elif "bossy" in item['title'].lower() or "cafe" in item['title'].lower():
                catalog_items["desi_couples_viral"].insert(0, item)
            else:
                catalog_items["desi_couples_viral"].insert(0, item)
            print(f"  [+] Reference Added: {item['title'][:60]}")
            
    # Process each catalog
    for cat_id, sources in cat_sources.items():
        print(f"\nHarvesting for catalog '{cat_id}'...")
        cat_links = []
        for s_type, s_url, s_pages in sources:
            if s_type == "mastiraja":
                links = harvest_links_mastiraja(s_url, pages=s_pages)
                print(f"  Mastiraja {s_url} -> {len(links)} links")
                cat_links.extend([("mastiraja", l) for l in links])
            elif s_type == "fsiblog":
                links = harvest_links_fsiblog(s_url, pages=s_pages)
                print(f"  FSIBlog {s_url} -> {len(links)} links")
                cat_links.extend([("fsiblog", l) for l in links])
                
        # Dedupe links
        seen_urls = set()
        unique_links = []
        for st, link in cat_links:
            if link not in seen_urls:
                seen_urls.add(link)
                unique_links.append((st, link))
                
        print(f"  Extracting {len(unique_links)} unique items concurrently...")
        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = []
            for st, link in unique_links:
                if st == "mastiraja":
                    futures.append(pool.submit(extract_mastiraja_post, link))
                else:
                    futures.append(pool.submit(extract_fsiblog_post, link))
                    
            for fut in as_completed(futures):
                res = fut.result()
                if res and res['video_url']:
                    vid_id = "desi_" + hashlib.md5(res['video_url'].encode()).hexdigest()[:12]
                    res['id'] = vid_id
                    all_videos[vid_id] = res
                    catalog_items[cat_id].append(res)
                    
        print(f"  Finished catalog '{cat_id}': {len(catalog_items[cat_id])} items")
        
    print(f"\n[2/5] Total unique videos harvested across all categories: {len(all_videos)}")
    
    # [3/5] Write metas and streams
    print("[3/5] Writing meta and stream JSON files...")
    for vid_id, item in all_videos.items():
        meta_json = {
            "meta": {
                "id": vid_id,
                "type": "movie",
                "name": item['title'],
                "poster": item['poster_url'],
                "background": item['poster_url'],
                "logo": item['poster_url'],
                "description": f"Curated High-Quality Desi & Pakistani MMS Leak: {item['title']}. Direct HD MP4 stream.",
                "releaseInfo": "2026",
                "genres": ["Desi MMS", "Indian MMS", "Pakistani Leak"],
                "behaviorHints": {
                    "defaultVideoId": vid_id
                }
            }
        }
        with open(os.path.join(BASE_DIR, "meta", "movie", f"{vid_id}.json"), "w", encoding="utf-8") as f:
            json.dump(meta_json, f, ensure_ascii=False)
            
        referer = "https://mastiraja.tv/" if item['source'] == 'mastiraja' else "https://fsiblog.co.im/"
        stream_json = {
            "streams": [
                {
                    "url": item['video_url'],
                    "name": "HD Direct Stream",
                    "title": f"{item['title'][:55]} [HD Direct]",
                    "behaviorHints": {
                        "notWebReady": True,
                        "proxyHeaders": {
                            "request": {
                                "User-Agent": HEADERS['User-Agent'],
                                "Referer": referer
                            }
                        }
                    }
                }
            ]
        }
        with open(os.path.join(BASE_DIR, "stream", "movie", f"{vid_id}.json"), "w", encoding="utf-8") as f:
            json.dump(stream_json, f, ensure_ascii=False)
            
    # [4/5] Write catalog files (paginated)
    print("[4/5] Writing paginated catalog files...")
    PAGE_SIZE = 100
    for cat_id, items in catalog_items.items():
        cat_dir = os.path.join(BASE_DIR, "catalog", "movie", cat_id)
        os.makedirs(cat_dir, exist_ok=True)
        
        base_metas = [
            {
                "id": it['id'],
                "type": "movie",
                "name": it['title'],
                "poster": it['poster_url'],
                "description": it['title'],
                "genres": ["Desi MMS", "Indian MMS", "Pakistani Leak"]
            }
            for it in items[:PAGE_SIZE]
        ]
        with open(os.path.join(BASE_DIR, "catalog", "movie", f"{cat_id}.json"), "w", encoding="utf-8") as f:
            json.dump({"metas": base_metas}, f, ensure_ascii=False)
            
        for skip in range(0, len(items), PAGE_SIZE):
            slice_items = items[skip:skip + PAGE_SIZE]
            slice_metas = [
                {
                    "id": it['id'],
                    "type": "movie",
                    "name": it['title'],
                    "poster": it['poster_url'],
                    "description": it['title'],
                    "genres": ["Desi MMS", "Indian MMS", "Pakistani Leak"]
                }
                for it in slice_items
            ]
            with open(os.path.join(cat_dir, f"skip={skip}.json"), "w", encoding="utf-8") as f:
                json.dump({"metas": slice_metas}, f, ensure_ascii=False)
                
    # Search catalog
    search_dir = os.path.join(BASE_DIR, "catalog", "movie", "desi_search")
    os.makedirs(search_dir, exist_ok=True)
    all_metas_list = [
        {
            "id": it['id'],
            "type": "movie",
            "name": it['title'],
            "poster": it['poster_url'],
            "description": it['title'],
            "genres": ["Desi MMS", "Indian MMS", "Pakistani Leak"]
        }
        for it in all_videos.values()
    ]
    with open(os.path.join(BASE_DIR, "catalog", "movie", "desi_search.json"), "w", encoding="utf-8") as f:
        json.dump({"metas": all_metas_list[:PAGE_SIZE]}, f, ensure_ascii=False)
        
    # [5/5] Write manifest.json
    print("[5/5] Generating manifest.json...")
    manifest = {
        "id": "com.savaa.stremio.desi",
        "version": "1.261111.1345",
        "name": "⭐ Desi 4K: Indian & Pakistani MMS Suite",
        "description": "Curated Indian & Pakistani Phone MMS, Viral Leaks, Bathroom Cams, Couple Private Tapes, Teasing & Real Amateur Sessions. 100% verified direct playable streams.",
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["desi_"],
        "catalogs": [
            {
                "type": "movie",
                "id": "desi_bathroom",
                "name": "🚿 Desi & Pakistani: Bathroom & Shower Leaks",
                "extra": [{"name": "skip", "isRequired": False}]
            },
            {
                "type": "movie",
                "id": "desi_couples_viral",
                "name": "📹 Desi & Pakistani: Viral Couples & Private MMS",
                "extra": [{"name": "skip", "isRequired": False}]
            },
            {
                "type": "movie",
                "id": "desi_amateur_cuck",
                "name": "🔞 Desi & Pakistani: Real Amateur & Risky Hookups",
                "extra": [{"name": "skip", "isRequired": False}]
            },
            {
                "type": "movie",
                "id": "desi_tease_live",
                "name": "💃 Desi & Pakistani: Striptease & Live Cam Leaks",
                "extra": [{"name": "skip", "isRequired": False}]
            },
            {
                "type": "movie",
                "id": "desi_search",
                "name": "🔍 Search Desi & Pakistani MMS",
                "extra": [{"name": "search", "isRequired": True}]
            }
        ],
        "behaviorHints": {
            "adult": True,
            "configurable": False
        }
    }
    
    with open(os.path.join(BASE_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"\nSUCCESS! Build complete in {BASE_DIR}")
    print(f"Total videos: {len(all_videos)}")
    for k, v in catalog_items.items():
        print(f"  - {k}: {len(v)} videos")

if __name__ == "__main__":
    build_all()

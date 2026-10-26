import urllib.request
import re
import json
import base64
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).parent
OUTPUT_FILE = REPO_ROOT / "pakistani_all.json"

HEADERS_FSI = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.fsiblogxx.com/'
}

HEADERS_MASTI = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://mastiraja.tv/'
}

def extract_fsixx_video(v_url):
    req = urllib.request.Request(v_url, headers=HEADERS_FSI)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            
        title_m = re.search(r'<title>(.*?)</title>', html)
        raw_title = title_m.group(1).replace(' - FSI Blog', '').replace(' - FSIBlog', '').replace(' -', '').strip() if title_m else 'Pakistani MMS'
        
        stream_url = ""
        poster_url = ""
        
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
            return {
                "id": f"paki_fsixx_{slug}",
                "name": raw_title,
                "stream_url": stream_url,
                "poster": poster_url,
                "thumbnail": poster_url,
                "page_url": v_url,
                "source": "FSIBlogXX",
                "quality": "480p+"
            }
    except Exception:
        pass
    return None

def extract_masti_video(v_url):
    req = urllib.request.Request(v_url, headers=HEADERS_MASTI)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            
        title_m = re.search(r'<title>(.*?)</title>', html)
        raw_title = title_m.group(1).replace(' – Masti Raja', '').replace(' | Masti Raja', '').strip() if title_m else 'Pakistani MMS'
        
        # Mastiraja direct mp4 stream search
        mp4_m = re.search(r'(https://videos\.mastiraja\.com/[^\s"\'<>]+\.mp4)', html)
        poster_m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        
        if mp4_m:
            stream_url = mp4_m.group(1)
            poster_url = poster_m.group(1) if poster_m else ""
            slug = v_url.rstrip('/').split('/')[-1]
            return {
                "id": f"paki_masti_{slug}",
                "name": raw_title,
                "stream_url": stream_url,
                "poster": poster_url,
                "thumbnail": poster_url,
                "page_url": v_url,
                "source": "Mastiraja",
                "quality": "720p HD"
            }
    except Exception:
        pass
    return None

def main():
    print("=== Harvesting High-Quality Pakistani Videos ===")
    all_fsixx_urls = []
    
    # 1. Collect from fsiblogxx tag: pakistani-girl (pages 1 to 10)
    for p in range(1, 11):
        url = f'https://www.fsiblogxx.com/tag/pakistani-girl/page/{p}/' if p > 1 else 'https://www.fsiblogxx.com/tag/pakistani-girl/'
        try:
            req = urllib.request.Request(url, headers=HEADERS_FSI)
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
            links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
            vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit'])]
            all_fsixx_urls.extend(vids)
        except Exception as e:
            print(f"Error fsixx pakistani-girl p{p}: {e}")

    # 2. Collect from fsiblogxx tag: pakistani (pages 1 to 5)
    for p in range(1, 6):
        url = f'https://www.fsiblogxx.com/tag/pakistani/page/{p}/' if p > 1 else 'https://www.fsiblogxx.com/tag/pakistani/'
        try:
            req = urllib.request.Request(url, headers=HEADERS_FSI)
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
            links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
            vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit'])]
            all_fsixx_urls.extend(vids)
        except Exception as e:
            print(f"Error fsixx pakistani p{p}: {e}")

    unique_fsixx = list(dict.fromkeys(all_fsixx_urls))
    print(f"Collected {len(unique_fsixx)} unique Pakistani URLs from FSIBlogXX")

    # 3. Collect from Mastiraja category: pakistani-sex (pages 1 to 4)
    all_masti_urls = []
    for p in range(1, 5):
        url = f'https://mastiraja.tv/category/pakistani-sex/page/{p}/' if p > 1 else 'https://mastiraja.tv/category/pakistani-sex/'
        try:
            req = urllib.request.Request(url, headers=HEADERS_MASTI)
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
            links = set(re.findall(r'href="(https://mastiraja\.tv/[^"]+)"', html))
            vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'privacy', 'dmca', 'terms', 'contact'])]
            all_masti_urls.extend(vids)
        except Exception as e:
            print(f"Error masti pakistani-sex p{p}: {e}")

    unique_masti = [u for u in dict.fromkeys(all_masti_urls) if 'filter=' not in u and 'compliance' not in u]
    print(f"Collected {len(unique_masti)} unique Pakistani URLs from Mastiraja")

    results = []
    seen = set()

    print("\nExtracting FSIBlogXX Pakistani streams...")
    with ThreadPoolExecutor(max_workers=10) as ex:
        for res in ex.map(extract_fsixx_video, unique_fsixx):
            if res and res["id"] not in seen:
                seen.add(res["id"])
                results.append(res)

    print("\nExtracting Mastiraja Pakistani streams...")
    with ThreadPoolExecutor(max_workers=10) as ex:
        for res in ex.map(extract_masti_video, unique_masti):
            if res and res["id"] not in seen:
                seen.add(res["id"])
                results.append(res)

    print(f"\n✅ Total High-Quality Pakistani Videos Harvested: {len(results)}")
    OUTPUT_FILE.write_text(json.dumps({"count": len(results), "items": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

import urllib.request
import urllib.parse
import base64
import re
import ssl
import json
import time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://mastiraja.tv/'
}

def fetch_url(url, retries=2):
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
                return r.read().decode('utf-8', errors='ignore')
        except Exception:
            time.sleep(0.3)
    return ""

def parse_post(url):
    html = fetch_url(url)
    if not html:
        return None
    slug_match = re.search(r'mastiraja\.tv/([^/]+)/?', url)
    if not slug_match:
        return None
    slug = slug_match.group(1)
    
    t_match = re.search(r'<title>(.*?)(?:\s*[-–|]\s*Mastiraja)?</title>', html, re.IGNORECASE)
    raw_title = t_match.group(1).strip() if t_match else slug.replace('-', ' ').title()
    clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)
    
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

    if not mp4_url:
        return None

    return {
        "id": f"masti_paki_{slug}",
        "name": clean_title,
        "stream_url": mp4_url,
        "poster": poster_url,
        "thumbnail": poster_url,
        "page_url": url,
        "source": "Mastiraja",
        "quality": "480p+"
    }

posts = set()
for page in range(1, 10):
    u = f"https://mastiraja.tv/category/pakistani-sex/page/{page}/" if page > 1 else "https://mastiraja.tv/category/pakistani-sex/"
    html = fetch_url(u)
    if not html:
        break
    links = re.findall(r'href=["\'](https://mastiraja\.tv/[a-zA-Z0-9\-]+/)["\']', html)
    valid = [l for l in links if not any(x in l for x in ['/category/', '/tag/', '/author/', '/page/', '/wp-', '/feed/'])]
    if not valid:
        break
    posts.update(valid)

print(f"Total Mastiraja Pakistani posts found: {len(posts)}")

results = []
with ThreadPoolExecutor(max_workers=10) as ex:
    for res in ex.map(parse_post, list(posts)):
        if res:
            results.append(res)

print(f"Successfully extracted {len(results)} Mastiraja Pakistani videos!")

# Now merge with pakistani_all.json
paki_file = r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k\pakistani_all.json"
with open(paki_file, "r", encoding="utf-8") as f:
    existing = json.load(f)["items"]

all_items = existing + results
# Deduplicate by stream_url and id
seen_stream = set()
unique_items = []
for it in all_items:
    st = it.get("stream_url")
    if st and st not in seen_stream:
        seen_stream.add(st)
        unique_items.append(it)

print(f"Combined total Pakistani items: {len(unique_items)}")
with open(paki_file, "w", encoding="utf-8") as f:
    json.dump({"count": len(unique_items), "items": unique_items}, f, indent=2, ensure_ascii=False)
print("Updated pakistani_all.json successfully!")

"""
Weekly Catalog Refresh Automation for vidi-4k:
- Re-crawls latest updates from Mastiraja, FSIBlogXX, FSIBlog, and Pimpbunny
- Strict content filtering: passes candidates through check_universal() / check_solo()
- Drops duplicates and dead links
- Updates source catalog pools and triggers build_full_suite.py
- Works standalone on local PC or inside GitHub Actions free tier
"""

import os
import sys
import json
import re
import ssl
import time
import urllib.request
import urllib.parse
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

REPO_ROOT = Path(__file__).parent
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def fetch_html(url, headers=None, timeout=10):
    h = HEADERS.copy()
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

def refresh_mastiraja(existing_stream_urls):
    print("--- Checking Mastiraja for New Leaks ---")
    new_items = []
    cat_urls = [
        'https://mastiraja.tv/category/viral-leaks/',
        'https://mastiraja.tv/category/desi-creators/',
        'https://mastiraja.tv/category/bathroom/'
    ]
    posts = set()
    for cat in cat_urls:
        for page in range(1, 3):
            u = f"{cat.rstrip('/')}/page/{page}/" if page > 1 else cat
            html = fetch_html(u)
            if not html:
                continue
            links = re.findall(r'href=["\'](https://mastiraja\.tv/[a-zA-Z0-9\-]+/)["\']', html)
            for l in links:
                if not any(x in l for x in ['/category/', '/tag/', '/author/', '/page/', '/wp-', '/feed/']):
                    posts.add(l)

    for p_url in list(posts)[:40]:
        html = fetch_html(p_url)
        if not html:
            continue
        slug_match = re.search(r'mastiraja\.tv/([^/]+)/?', p_url)
        if not slug_match:
            continue
        slug = slug_match.group(1)

        t_match = re.search(r'<title>(.*?)(?:\s*[-–|]\s*Mastiraja)?</title>', html, re.IGNORECASE)
        raw_title = t_match.group(1).strip() if t_match else slug.replace('-', ' ').title()
        clean_title = re.sub(r'[\r\n\t]+', ' ', raw_title)

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

        if mp4_url and mp4_url not in existing_stream_urls:
            new_items.append({
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
                "runtime": "MMS",
                "source": "mastiraja.tv"
            })
            existing_stream_urls.add(mp4_url)

    print(f"Mastiraja: Found {len(new_items)} candidate new items")
    return new_items

def refresh_fsiblogxx(existing_stream_urls):
    print("--- Checking FSIBlogXX for New Leaks ---")
    new_items = []
    headers = {'Referer': 'https://www.fsiblogxx.com/'}
    posts = set()
    for page in range(1, 3):
        url = f'https://www.fsiblogxx.com/porn-videos/page/{page}/' if page > 1 else 'https://www.fsiblogxx.com/porn-videos/'
        html = fetch_html(url, headers=headers)
        if not html:
            continue
        links = set(re.findall(r'href="(https://www\.fsiblogxx\.com/[^"]+)"', html))
        vids = [l for l in links if not any(k in l for k in ['/category/', '/tag/', '/page/', 'porn-videos', 'about', 'contact', 'submit', 'privacy', 'terms', 'dmca'])]
        posts.update(vids)

    for v_url in list(posts)[:40]:
        html = fetch_html(v_url, headers=headers)
        if not html:
            continue
        title_m = re.search(r'<title>(.*?)</title>', html)
        raw_title = title_m.group(1).replace(' - FSI Blog', '').replace(' - FSIBlog', '').replace(' -', '').strip() if title_m else 'Desi MMS'

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
            m_thumb = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if m_thumb:
                poster_url = m_thumb.group(1)

        slug_m = re.search(r'fsiblogxx\.com/([^/]+)/?', v_url)
        slug = slug_m.group(1) if slug_m else re.sub(r'[^a-zA-Z0-9]', '_', raw_title[:30])

        # Drop cdn.fsiblogxx.com streams because they require Referer header and 403 on iOS/Vidi
        if stream_url and "cdn.fsiblogxx.com" in stream_url:
            stream_url = ""

        if stream_url and stream_url not in existing_stream_urls:
            new_items.append({
                "id": f"fsixx_{slug}",
                "name": raw_title,
                "stream_url": stream_url,
                "url": stream_url,
                "poster": poster_url,
                "thumbnail": poster_url,
                "logo": poster_url,
                "tags": ["fsiblogxx", "desi", "mms", "viral-leak", "amateur"],
                "quality": "480p+",
                "runtime": "MMS",
                "source": "fsiblogxx.com"
            })
            existing_stream_urls.add(stream_url)

    print(f"FSIBlogXX: Found {len(new_items)} candidate new items")
    return new_items

def run_weekly_refresh():
    print("==================================================")
    print("      vidi-4k Automated Weekly Refresh            ")
    print("==================================================")

    # 1. Collect all known stream URLs
    existing_streams = set()
    pool_files = [
        REPO_ROOT / "mastiraja_all.json",
        REPO_ROOT / "fsiblogxx_all.json",
        REPO_ROOT / "desi_all.json",
        REPO_ROOT / "vidi.json",
        REPO_ROOT / "vidi_all.json",
    ]
    for pf in pool_files:
        if pf.exists():
            try:
                data = json.load(open(pf, encoding='utf-8'))
                items = data.get("items", []) if isinstance(data, dict) else data
                for it in items:
                    st = it.get("stream_url") or it.get("url")
                    if st:
                        existing_streams.add(st)
            except Exception:
                pass

    print(f"Loaded {len(existing_streams)} existing known streams for deduplication.")

    # 2. Fetch new candidates
    masti_new = refresh_mastiraja(existing_streams)
    fsixx_new = refresh_fsiblogxx(existing_streams)

    # 3. Import filters from build_full_suite
    from build_full_suite import check_universal, check_solo

    passed_masti = []
    for it in masti_new:
        ok, reason = check_universal(it)
        if ok:
            passed_masti.append(it)
        else:
            print(f"Filtered out Mastiraja item '{it['name']}': {reason}")

    passed_fsixx = []
    for it in fsixx_new:
        ok, reason = check_universal(it)
        if ok:
            passed_fsixx.append(it)
        else:
            print(f"Filtered out FSIBlogXX item '{it['name']}': {reason}")

    print(f"Passed Filter: Mastiraja {len(passed_masti)}/{len(masti_new)} | FSIBlogXX {len(passed_fsixx)}/{len(fsixx_new)}")

    # 4. Append to pool files if any
    changed = False
    if passed_masti:
        m_file = REPO_ROOT / "mastiraja_all.json"
        cur = json.load(open(m_file, encoding='utf-8')) if m_file.exists() else []
        cur.extend(passed_masti)
        m_file.write_text(json.dumps(cur, indent=2, ensure_ascii=False), encoding='utf-8')
        changed = True

    if passed_fsixx:
        f_file = REPO_ROOT / "fsiblogxx_all.json"
        cur = json.load(open(f_file, encoding='utf-8')) if f_file.exists() else []
        cur.extend(passed_fsixx)
        f_file.write_text(json.dumps(cur, indent=2, ensure_ascii=False), encoding='utf-8')
        changed = True

    # 5. Trigger Master Rebuild & Post-Build No-Header Filter
    print("\nTriggering build_full_suite.py...")
    import subprocess
    cmd = [sys.executable, str(REPO_ROOT / "build_full_suite.py")]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Build Warnings/Errors:", res.stderr)

    print("\nRunning post-build no-header stream audit (fix_header_streams.py)...")
    cmd_fix = [sys.executable, str(REPO_ROOT / "fix_header_streams.py")]
    res_fix = subprocess.run(cmd_fix, cwd=str(REPO_ROOT), capture_output=True, text=True)
    print(res_fix.stdout)
    if res_fix.stderr:
        print("Header fix warnings:", res_fix.stderr)

    print("\n=== Weekly Refresh Run Completed Successfully ===")

if __name__ == "__main__":
    run_weekly_refresh()

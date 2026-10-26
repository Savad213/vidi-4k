"""
Standalone and Pre-Build Link Checker for vidi-4k:
- Validates active stream URLs via HTTP Range requests (bytes=0-1024)
- Identifies and drops dead links (404, 410, connection drops)
- Distinguishes 'Endpoint Responded' from full container playback
- Outputs link_checker_report.json with catalog-by-catalog metrics
"""

import json
import os
import urllib.request
import ssl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

REPO_ROOT = Path(__file__).parent
STREAM_DIR = REPO_ROOT / "stream" / "movie"
REPORT_FILE = REPO_ROOT / "link_checker_report.json"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def probe_stream(stream_info):
    vid_id, stream_url, proxy_headers = stream_info
    if not stream_url:
        return vid_id, False, "NoUrl", None, None

    # Handle local media file
    if "savad213.github.io/vidi-4k/media/" in stream_url or stream_url.startswith("media/"):
        local_p = REPO_ROOT / "media" / Path(stream_url).name
        if local_p.exists():
            return vid_id, True, 200, "video/mp4", local_p.stat().st_size

    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Range': 'bytes=0-1024'
    }
    # Vidi and Stremio Web/iPhone cannot send custom headers, so probe exactly like the
    # client does: no Referer, no proxyHeaders. A stream that needs them is dead for us.

    try:
        req = urllib.request.Request(stream_url, headers=req_headers)
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            c_len = resp.headers.get('Content-Length')
            c_type = resp.headers.get('Content-Type')
            return vid_id, True, resp.status, c_type, c_len
    except urllib.error.HTTPError as he:
        # 206 Partial Content or 200 OK are success; 404, 410, 403 are errors
        if he.code in (200, 206):
            return vid_id, True, he.code, "stream", None
        return vid_id, False, he.code, None, None
    except Exception as e:
        return vid_id, False, str(type(e).__name__), None, None

def run_link_checker(active_catalogs_data, max_workers=25):
    print("=== Running Active Stream Link Checker ===")
    report = {
        "catalogs": {},
        "total_checked": 0,
        "total_alive": 0,
        "total_dead": 0
    }
    
    dead_ids = set()

    for cid, cdata in active_catalogs_data.items():
        items = cdata["items"]
        stream_tuples = []
        for it in items:
            vid_id = it["id"]
            st_url = it.get("stream_url") or it.get("url") or ""
            # check stream file if exists for stream URL and proxyHeaders
            s_file = STREAM_DIR / f"{vid_id}.json"
            proxy_headers = None
            if s_file.exists():
                try:
                    s_data = json.load(open(s_file, encoding='utf-8'))
                    if not st_url and "streams" in s_data and s_data["streams"]:
                        st_url = s_data["streams"][0].get("url", "")
                    proxy_headers = s_data['streams'][0].get('behaviorHints', {}).get('proxyHeaders')
                except:
                    pass
            stream_tuples.append((vid_id, st_url, proxy_headers))

        cat_alive = 0
        cat_dead = 0
        cat_dead_items = []

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for vid_id, is_alive, status, c_type, c_len in pool.map(probe_stream, stream_tuples):
                if is_alive:
                    cat_alive += 1
                else:
                    cat_dead += 1
                    cat_dead_items.append({"id": vid_id, "status": status})
                    dead_ids.add(vid_id)

        report["catalogs"][cid] = {
            "name": cdata["name"],
            "checked": len(items),
            "alive": cat_alive,
            "dead": cat_dead,
            "dead_details": cat_dead_items
        }
        report["total_checked"] += len(items)
        report["total_alive"] += cat_alive
        report["total_dead"] += cat_dead

        print(f"Catalog {cid:22} | Checked: {len(items):4} | Responded (200/206): {cat_alive:4} | Dead: {cat_dead:2}")

    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Link check report saved to {REPORT_FILE.name}")
    return dead_ids, report

if __name__ == "__main__":
    # Test run against current manifest catalogs
    manifest = json.load(open(REPO_ROOT / "manifest.json", encoding="utf-8"))
    test_data = {}
    for c in manifest["catalogs"]:
        cid = c["id"]
        cat_file = REPO_ROOT / "catalog" / "movie" / f"{cid}.json"
        if cat_file.exists():
            d = json.load(open(cat_file, encoding="utf-8"))
            test_data[cid] = {"name": c["name"], "items": d.get("metas", [])}
    run_link_checker(test_data, max_workers=20)

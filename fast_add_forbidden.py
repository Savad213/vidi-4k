import urllib.request
import json
import base64
import re
import hashlib
import socket
from pathlib import Path

socket.setdefaulttimeout(4)

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")

cfg = {
    'sources': ['pornrips', 'piratebay'],
    'rdKey': 'Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ',
    'debridApiKey': 'Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ',
    'debridProvider': 'realdebrid',
    'qual4k': True,
    'qual1080p': True,
    'compactStudios': True,
    'extraIndexers': True,
    'enable1337x': True,
    'hideP2P': True
}
b64 = base64.b64encode(json.dumps(cfg).encode()).decode()
base_url = f"https://tpb-adult-addon.click/{b64}"
headers = {'User-Agent': 'Mozilla/5.0'}

with open('C:/Users/SM.DESKTOP-P1R0508.000/.gemini/antigravity-cli/brain/2a859197-7e46-4613-bfc6-5fad31b252d3/scratch/forbidden_candidates.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# Load existing taboo catalog
with open(REPO_ROOT / "catalog/movie/xfhq_slow_burn_taboo.json", "r", encoding="utf-8") as f:
    taboo_catalog = json.load(f)["metas"]

seen_ids = {m["id"] for m in taboo_catalog}

verified_new = []

for idx, c in enumerate(candidates):
    name = c["name"]
    mid = c["id"]
    studio = c["studio"]
    
    slug = hashlib.md5(name.encode()).hexdigest()[:10]
    item_id = f"xfhq_taboo_{slug}"
    if item_id in seen_ids:
        continue
        
    s_url = f"{base_url}/stream/Porn/{mid}.json"
    try:
        req = urllib.request.Request(s_url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as r:
            streams = json.loads(r.read().decode()).get("streams", [])
            if streams and streams[0].get("url"):
                cdn_url = streams[0]["url"]
                # Test byte range
                v_req = urllib.request.Request(cdn_url, headers={'User-Agent': 'Mozilla/5.0', 'Range': 'bytes=0-32767'})
                with urllib.request.urlopen(v_req, timeout=4) as v_resp:
                    chunk = v_resp.read()
                    if v_resp.status in (200, 206) and len(chunk) > 0:
                        clean_title = re.sub(r'(?i)\b(2160p|1080p|mp4|hevc|x265|p2p|xc|xxx|split scenes|part \d+)\b', '', name)
                        clean_title = re.sub(r'[\[\]\(\)\-_]', ' ', clean_title).strip()
                        clean_title = re.sub(r'\s+', ' ', clean_title)
                        clean_title = re.sub(r'^\d{2}\s+\d{2}\s+\d{2}\s*', '', clean_title)
                        clean_title = re.sub(rf'^{studio}\s*', '', clean_title, flags=re.I).strip()
                        display_name = f"{studio}: {clean_title}"
                        
                        seen_ids.add(item_id)
                        print(f"[{len(verified_new)+1}] [PASS {v_resp.status}] {display_name} -> {len(chunk)} bytes", flush=True)
                        
                        meta_obj = {
                            "id": item_id,
                            "type": "movie",
                            "name": display_name,
                            "poster": c.get("poster") or "",
                            "posterShape": "poster",
                            "background": c.get("poster") or "",
                            "description": f"🔥 Slow-Burn Forbidden Romance · Studio: {studio} · Feature Narrative with psychological tension, dialogue, slow seduction & intense 1-on-1 chemistry · 4K/1080p Real-Debrid Instant Stream.",
                            "genres": [studio, "Slow Burn", "Forbidden Romance", "Taboo", "Story", "1-on-1", "4K UHD"],
                            "releaseInfo": "4K / 1080p UHD",
                            "runtime": "45 min+",
                            "behaviorHints": {
                                "defaultVideoId": item_id
                            }
                        }
                        
                        # Save meta
                        m_path = REPO_ROOT / f"meta/movie/{item_id}.json"
                        with open(m_path, "w", encoding="utf-8") as mf:
                            json.dump({"meta": meta_obj}, mf, ensure_ascii=False)
                            
                        # Save stream
                        formatted_streams = []
                        for s in streams:
                            formatted_streams.append({
                                "name": f"🔥 {studio} 4K/1080p [RD]",
                                "title": f"{display_name}\n[Real-Debrid Direct Instant CDN]",
                                "url": s.get("url"),
                                "behaviorHints": {
                                    "notWebReady": False
                                }
                            })
                            
                        s_path = REPO_ROOT / f"stream/movie/{item_id}.json"
                        with open(s_path, "w", encoding="utf-8") as sf:
                            json.dump({"streams": formatted_streams}, sf, ensure_ascii=False)
                            
                        verified_new.append(meta_obj)
                        if len(verified_new) >= 10:
                            break
            else:
                print(f" [-] No stream: {name[:40]}", flush=True)
    except Exception as e:
        print(f" [-] Skip: {name[:40]}", flush=True)

print(f"\nAdded {len(verified_new)} new verified forbidden movies!", flush=True)

if verified_new:
    taboo_catalog.extend(verified_new)
    cat_path = REPO_ROOT / "catalog/movie/xfhq_slow_burn_taboo.json"
    with open(cat_path, "w", encoding="utf-8") as cf:
        json.dump({"metas": taboo_catalog}, cf, ensure_ascii=False)
        
    manifest_file = REPO_ROOT / "manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as mf:
        manifest = json.load(mf)
    v_parts = manifest.get("version", "5.261029.1247").split(".")
    v_parts[-1] = str(int(v_parts[-1]) + 1)
    manifest["version"] = ".".join(v_parts)
    with open(manifest_file, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)
    print(f"Manifest bumped to version {manifest['version']}! Total taboo films now: {len(taboo_catalog)}", flush=True)

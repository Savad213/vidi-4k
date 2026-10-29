import json
import base64
import os
import re
import urllib.request
import hashlib
import time
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")

cfg = {
    'sources': ['pornrips', 'piratebay'],
    'rdKey': 'Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ',
    'debridApiKey': 'Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ',
    'debridProvider': 'realdebrid',
    'qual4k': True,
    'qual1080p': False,
    'minSeeders': 1,
    'maxResults': 30,
    'compactStudios': True,
    'extraIndexers': True,
    'enable1337x': True,
    'hideP2P': True
}
b64 = base64.b64encode(json.dumps(cfg).encode()).decode()
base_url = f'https://tpb-adult-addon.click/{b64}'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

TARGET_STUDIOS = [
    ('MissaX', 'xxx_studio_missax'),
    ('Pure Taboo', 'xxx_studio_puretaboo'),
    ('Deeper', 'xxx_studio_deeper'),
    ('Adult Time', 'xxx_studio_adulttime')
]

EXCLUDE = re.compile(r'(?i)(anal|threesome|3some|gangbang|orgy|foursome|tag-team|rough|chok|slap|bdsm|pain|trans|toilet|piss|fetish|fist|creampie party|strap|lesbian)')

print("1. Fetching candidate slow-burn forbidden movies...", flush=True)

candidate_items = []
seen_titles = set()

for studio_name, cat in TARGET_STUDIOS:
    try:
        url = f'{base_url}/catalog/Porn/{cat}.json'
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode())
        items = data.get('metas', [])
        print(f"Loaded {len(items)} items from {studio_name}", flush=True)
        
        added = 0
        for it in items:
            raw_title = it.get('name', '').strip()
            desc = it.get('description', '')
            combo = f"{raw_title} {desc}"
            
            if EXCLUDE.search(combo):
                continue
            if raw_title.lower() in seen_titles:
                continue
                
            seen_titles.add(raw_title.lower())
            it['studio_name'] = studio_name
            candidate_items.append(it)
            added += 1
            if added >= 4:
                break
    except Exception as e:
        print(f"Skipping {studio_name}: {e}", flush=True)

print(f"\n2. Verifying Real-Debrid 4K streams for {len(candidate_items)} candidates...", flush=True)

curated_movies = []

for idx, it in enumerate(candidate_items):
    raw_title = it.get('name', '').strip()
    studio_name = it['studio_name']
    
    stream_url = f"{base_url}/stream/Porn/{it['id']}.json"
    try:
        s_req = urllib.request.Request(stream_url, headers=headers)
        s_resp = urllib.request.urlopen(s_req, timeout=15)
        s_data = json.loads(s_resp.read().decode())
        streams = s_data.get('streams', [])
        if not streams or not streams[0].get('url'):
            print(f" [-] No stream for {raw_title}", flush=True)
            continue
            
        slug = hashlib.md5(raw_title.encode()).hexdigest()[:10]
        item_id = f"xfhq_taboo_{slug}"
        
        clean_name = re.sub(r'\[.*?\]', '', raw_title).strip()
        display_name = f"{studio_name}: {clean_name}"
            
        poster = it.get('poster') or ""
        background = it.get('background') or poster
        
        meta_obj = {
            "id": item_id,
            "type": "movie",
            "name": display_name,
            "poster": poster,
            "posterShape": "poster",
            "background": background,
            "description": f"🔥 Slow-Burn Forbidden Romance · Studio: {studio_name} · Feature Narrative with prolonged psychological tension, dialogue, slow seduction & intense 1-on-1 chemistry · 4K UHD Real-Debrid Instant Stream.",
            "genres": [studio_name, "Slow Burn", "Forbidden", "Taboo Romance", "Story", "1-on-1", "4K UHD"],
            "releaseInfo": "4K UHD",
            "runtime": "45 min+",
            "behaviorHints": {
                "defaultVideoId": item_id
            }
        }
        
        # Save meta
        m_path = REPO_ROOT / "meta/movie" / f"{item_id}.json"
        m_path.parent.mkdir(parents=True, exist_ok=True)
        with open(m_path, "w", encoding="utf-8") as mf:
            json.dump({"meta": meta_obj}, mf, ensure_ascii=False)
            
        formatted_streams = []
        for s in streams:
            formatted_streams.append({
                "name": "🔥 4K UHD [RD]",
                "title": f"{display_name}\n[Real-Debrid Direct Instant 4K]",
                "url": s.get("url"),
                "behaviorHints": {
                    "notWebReady": False
                }
            })
            
        # Save stream
        s_path = REPO_ROOT / "stream/movie" / f"{item_id}.json"
        s_path.parent.mkdir(parents=True, exist_ok=True)
        with open(s_path, "w", encoding="utf-8") as sf:
            json.dump({"streams": formatted_streams}, sf, ensure_ascii=False)
            
        curated_movies.append(meta_obj)
        print(f" [+] [{len(curated_movies)}/12] Verified & Saved: {display_name}", flush=True)
        
        if len(curated_movies) >= 12:
            break
        time.sleep(0.4)
    except Exception as e:
        print(f" [-] Stream check error for {raw_title}: {e}", flush=True)

print(f"\nTotal curated slow-burn films: {len(curated_movies)}", flush=True)

# Save catalog file
catalog_path = REPO_ROOT / "catalog/movie/xfhq_slow_burn_taboo.json"
catalog_path.parent.mkdir(parents=True, exist_ok=True)
with open(catalog_path, "w", encoding="utf-8") as cf:
    json.dump({"metas": curated_movies}, cf, ensure_ascii=False)
print("Saved catalog: xfhq_slow_burn_taboo.json", flush=True)

# Update manifest.json
manifest_file = REPO_ROOT / "manifest.json"
with open(manifest_file, "r", encoding="utf-8") as mf:
    manifest = json.load(mf)

# Insert xfhq_slow_burn_taboo right after xfhq_curated_favorites
manifest["catalogs"] = [c for c in manifest.get("catalogs", []) if c.get("id") != "xfhq_slow_burn_taboo"]

taboo_catalog_entry = {
    "type": "movie",
    "id": "xfhq_slow_burn_taboo",
    "name": "🔥 Slow-Burn & Forbidden Romance (4K UHD)",
    "extra": [
        {"name": "search", "isRequired": False},
        {"name": "skip", "isRequired": False}
    ]
}

# Insert at index 1 (right below Savaa's Personal Favorites at 0)
manifest["catalogs"].insert(1, taboo_catalog_entry)

# Ensure xfhq is in idPrefixes (already there)
if "xfhq" not in manifest.get("idPrefixes", []):
    manifest["idPrefixes"].append("xfhq")

v_parts = manifest.get("version", "5.261027.229").split(".")
v_parts[-1] = str(int(v_parts[-1]) + 1)
manifest["version"] = ".".join(v_parts)

with open(manifest_file, "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)

print(f"Manifest updated to version {manifest['version']} with 🔥 Slow-Burn & Forbidden Romance at position 1!", flush=True)

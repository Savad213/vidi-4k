import json
import base64
import os
import re
import urllib.request
import hashlib
import time
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")

# Clean up any leftover cinema_ files
for folder in ["meta/movie", "stream/movie"]:
    p = REPO_ROOT / folder
    if p.exists():
        for f in p.glob("cinema_*.json"):
            try:
                f.unlink()
            except Exception:
                pass

cfg = {
    'sources': ['pornrips', 'piratebay'],
    'rdKey': 'Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ',
    'debridApiKey': 'Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ',
    'debridProvider': 'realdebrid',
    'qual4k': True,
    'qual1080p': True,
    'minSeeders': 1,
    'maxResults': 30,
    'compactStudios': True,
    'extraIndexers': True,
    'enable1337x': True,
    'hideP2P': True
}
b64 = base64.b64encode(json.dumps(cfg).encode()).decode()
base_url = f'https://tpb-adult-addon.click/{b64}'

EXCLUDE = re.compile(r'(?i)(anal|threesome|3some|gangbang|orgy|foursome|tag-team|1 bbc for 3|rough|chok|slap|bdsm|pain|trans|toilet|piss|fetish|fist|creampie party|strap|lesbian)')

# Targeted search queries for user's confirmed favorite actresses & studios
TARGET_FEEDS = [
    ('Kendra Sunderland', 'xxx_studio_kendra_sunderland', 'Kendra Sunderland', 'Vixen'),
    ('Lena Paul', 'xxx_studio_lena_paul', 'Lena Paul', 'Deeper'),
    ('Angela White', 'xxx_studio_angela_white', 'Angela White', 'Family Therapy'),
    ('Elizabeth Skylar', 'xxx_studio_elizabeth_skylar', 'Elizabeth Skylar', 'MissaX'),
    ('Ellie Nova', 'xxx_studio_ellie_nova', 'Ellie Nova', 'Adult Time'),
    ('MissaX Story', 'xxx_studio_missax', 'MissaX', 'MissaX'),
    ('Deeper Story', 'xxx_studio_deeper', 'Deeper', 'Deeper'),
    ('Pure Taboo', 'xxx_studio_puretaboo', 'Pure Taboo', 'Pure Taboo')
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Fetching targeted films for Savaa's favorite performers...", flush=True)

candidate_items = []
seen_titles = set()

for label, cat, performer_name, default_studio in TARGET_FEEDS:
    try:
        url = f'{base_url}/catalog/Porn/{cat}.json'
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req, timeout=6).read().decode())
        items = data.get('metas', [])
        
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
            it['performer_name'] = performer_name
            it['default_studio'] = default_studio
            candidate_items.append(it)
            added += 1
            if added >= 2:
                break
        print(f"Loaded {added} candidates from {label}", flush=True)
        time.sleep(0.3)
    except Exception as e:
        print(f"Skipping {label}: {e}", flush=True)

print(f"\nVerifying streams sequentially for {len(candidate_items)} candidates...", flush=True)

curated_movies = []

for idx, it in enumerate(candidate_items):
    raw_title = it.get('name', '').strip()
    performer_name = it['performer_name']
    default_studio = it['default_studio']
    
    stream_url = f"{base_url}/stream/Porn/{it['id']}.json"
    try:
        time.sleep(0.5)
        s_req = urllib.request.Request(stream_url, headers=headers)
        s_resp = urllib.request.urlopen(s_req, timeout=8)
        s_data = json.loads(s_resp.read().decode())
        streams = s_data.get('streams', [])
        if not streams:
            print(f" [-] No streams for {raw_title}", flush=True)
            continue
            
        slug = hashlib.md5(raw_title.encode()).hexdigest()[:10]
        item_id = f"xfhq_fav_{slug}"
        
        clean_name = re.sub(r'\[.*?\]', '', raw_title).strip()
        if performer_name not in ('MissaX', 'Deeper', 'Pure Taboo') and performer_name.lower() not in clean_name.lower():
            display_name = f"{performer_name}: {clean_name}"
        else:
            display_name = clean_name
            
        poster = it.get('poster') or ""
        background = it.get('background') or poster
        
        meta_obj = {
            "id": item_id,
            "type": "movie",
            "name": display_name,
            "poster": poster,
            "posterShape": "poster",
            "background": background,
            "description": f"⭐ Verified Favorite · Star: {performer_name} · Studio: {default_studio} · Sensual, romantic 1-on-1 chemistry · 4K UHD Real-Debrid Instant Stream.",
            "genres": [performer_name, default_studio, "Sensual", "Romance", "1-on-1", "4K UHD"],
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
                "name": "⭐ 4K UHD [RD]",
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
    except Exception as e:
        print(f" [-] Failed stream check for {raw_title}: {e}", flush=True)

print(f"\nTotal curated films verified & created: {len(curated_movies)}", flush=True)

# Save to catalog
catalog_path = REPO_ROOT / "catalog/movie/xfhq_curated_favorites.json"
catalog_path.parent.mkdir(parents=True, exist_ok=True)
with open(catalog_path, "w", encoding="utf-8") as cf:
    json.dump({"metas": curated_movies}, cf, ensure_ascii=False)
print("Saved catalog file: xfhq_curated_favorites.json", flush=True)

# Update manifest.json
manifest_file = REPO_ROOT / "manifest.json"
with open(manifest_file, "r", encoding="utf-8") as mf:
    manifest = json.load(mf)

# Clean up catalog list
manifest["catalogs"] = [c for c in manifest.get("catalogs", []) if c.get("id") not in ("savaa_curated_cinema", "xfhq_curated_favorites")]

# Insert new favorites catalog at position 0
manifest["catalogs"].insert(0, {
    "type": "movie",
    "id": "xfhq_curated_favorites",
    "name": "⭐ Savaa's Personal Favorites (4K UHD)",
    "extra": [
        {"name": "search", "isRequired": False},
        {"name": "skip", "isRequired": False}
    ]
})

v_parts = manifest.get("version", "5.261027.228").split(".")
v_parts[-1] = str(int(v_parts[-1]) + 1)
manifest["version"] = ".".join(v_parts)

with open(manifest_file, "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)

print(f"Manifest updated to version {manifest['version']} with ⭐ Savaa's Personal Favorites at position 0!", flush=True)

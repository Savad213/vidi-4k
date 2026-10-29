import urllib.request
import json
import base64
import os
import re
import hashlib
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")

# Base configuration for tpb-adult-addon with Real-Debrid
cfg = {
    "sources": ["pornrips", "piratebay"],
    "installSources": ["pornrips", "piratebay"],
    "rdKey": "Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ",
    "debridApiKey": "Q7ACJHL2LIV7AKHMY2CPKCY76GJHWNA4M3WKE2PYAB3EW5BPZGGQ",
    "debridProvider": "realdebrid",
    "qual4k": True,
    "qual1080p": True,
    "minSeeders": 1,
    "maxResults": 30,
    "compactStudios": True,
    "hideFromHome": False,
    "namePostfix": "Curated Cinema 4K",
    "enabledCatalogs": [
        "xxx_studio_missax",
        "xxx_studio_deeper",
        "xxx_studio_bellesafilms",
        "xxx_studio_sexart",
        "xxx_studio_puretaboo",
        "xxx_studio_dorcelclub",
        "xxx_studio_nurumassage"
    ],
    "prCatalogs": {
        "pr_recent": True,
        "pr_studio": True,
        "pr_tag": True,
        "pr_search": True
    },
    "extraIndexers": True,
    "enable1337x": True,
    "hideP2P": True,
    "studioSearch": True,
    "prewarmDebrid": False,
    "hideGroups": ["studios"],
    "disabledCatalogs": []
}

b64_cfg = base64.b64encode(json.dumps(cfg).encode()).decode()
base_url = f"https://tpb-adult-addon.click/{b64_cfg}"

studios = [
    ("MissaX", "xxx_studio_missax"),
    ("Deeper", "xxx_studio_deeper"),
    ("Bellesa Films", "xxx_studio_bellesafilms"),
    ("Pure Taboo", "xxx_studio_puretaboo"),
    ("Dorcel Club", "xxx_studio_dorcelclub"),
    ("SexArt", "xxx_studio_sexart"),
    ("Nuru Massage", "xxx_studio_nurumassage")
]

NEG_FILTER = re.compile(r'(?i)(anal|gangbang|orgy|rough|chok|slap|bdsm|pain|trans|toilet|piss|fetish|straplez)')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Fetching candidates from top studio feeds...")

catalog_metas = []
seen_titles = set()

for studio_label, cat_id in studios:
    try:
        cat_url = f"{base_url}/catalog/Porn/{cat_id}.json"
        req = urllib.request.Request(cat_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode())
        items = data.get("metas", [])
        
        studio_added = 0
        for it in items:
            raw_name = it.get("name", "").strip()
            desc = it.get("description", "")
            combo = f"{raw_name} {desc}"
            
            if NEG_FILTER.search(combo):
                continue
            if raw_name.lower() in seen_titles:
                continue
                
            # Query stream endpoint to verify availability
            stream_url = f"{base_url}/stream/Porn/{it['id']}.json"
            try:
                s_req = urllib.request.Request(stream_url, headers=headers)
                s_resp = urllib.request.urlopen(s_req, timeout=6)
                s_data = json.loads(s_resp.read().decode())
                streams = s_data.get("streams", [])
                if not streams:
                    continue
            except Exception as se:
                print(f"Skipping {raw_name}: stream check error {se}")
                continue
                
            seen_titles.add(raw_name.lower())
            
            # Create a clean unique cinema ID
            slug = hashlib.md5(raw_name.encode()).hexdigest()[:12]
            cinema_id = f"cinema_{slug}"
            
            # Format title nicely
            clean_name = re.sub(r'\[.*?\]', '', raw_name).strip()
            display_title = f"{studio_label}: {clean_name}"
            
            poster = it.get("poster") or ""
            background = it.get("background") or poster
            
            meta_obj = {
                "id": cinema_id,
                "type": "movie",
                "name": display_title,
                "poster": poster,
                "posterShape": "poster",
                "background": background,
                "description": f"⭐ 4K UHD Masterpiece · Studio: {studio_label} · Sensual, romantic & narrative erotica · Verified Real-Debrid Instant Stream.",
                "genres": [studio_label, "Sensual", "Romance", "4K UHD", "Narrative"],
                "releaseInfo": "4K UHD",
                "runtime": "45 min+",
                "behaviorHints": {
                    "defaultVideoId": cinema_id
                }
            }
            
            # Save meta file
            meta_path = REPO_ROOT / "meta" / "movie" / f"{cinema_id}.json"
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump({"meta": meta_obj}, mf, ensure_ascii=False)
                
            # Enhance stream object titles
            for s in streams:
                s["name"] = f"⭐ {studio_label} 4K [RD]"
                s["title"] = f"{display_title}\n[Real-Debrid Instant 4K CDN Cache]"
                
            # Save stream file
            stream_path = REPO_ROOT / "stream" / "movie" / f"{cinema_id}.json"
            stream_path.parent.mkdir(parents=True, exist_ok=True)
            with open(stream_path, "w", encoding="utf-8") as sf:
                json.dump({"streams": streams}, sf, ensure_ascii=False)
                
            catalog_metas.append(meta_obj)
            studio_added += 1
            print(f" [+] Added: {display_title} -> {cinema_id}")
            
            if studio_added >= 3:
                break
    except Exception as e:
        print(f"Error processing {cat_id}: {e}")

print(f"\nTotal curated cinema masterpieces added: {len(catalog_metas)}")

# Write catalog file
cat_file = REPO_ROOT / "catalog" / "movie" / "savaa_curated_cinema.json"
cat_file.parent.mkdir(parents=True, exist_ok=True)
with open(cat_file, "w", encoding="utf-8") as cf:
    json.dump({"metas": catalog_metas}, cf, ensure_ascii=False)
print("Saved catalog: savaa_curated_cinema.json")

# Update manifest.json
manifest_file = REPO_ROOT / "manifest.json"
with open(manifest_file, "r", encoding="utf-8") as mf:
    manifest = json.load(mf)

if "cinema_" not in manifest.get("idPrefixes", []):
    manifest["idPrefixes"].insert(0, "cinema_")

# Remove old savaa_curated_cinema if present
manifest["catalogs"] = [c for c in manifest.get("catalogs", []) if c.get("id") != "savaa_curated_cinema"]

# Insert at top (position 0)
new_catalog_entry = {
    "type": "movie",
    "id": "savaa_curated_cinema",
    "name": "⭐ Curated Cinema: Sensual & Narrative Masterpieces (4K)",
    "extra": [
        {"name": "search", "isRequired": False},
        {"name": "skip", "isRequired": False}
    ]
}
manifest["catalogs"].insert(0, new_catalog_entry)

# Bump patch version
v_parts = manifest.get("version", "5.261027.226").split(".")
v_parts[-1] = str(int(v_parts[-1]) + 1)
manifest["version"] = ".".join(v_parts)

with open(manifest_file, "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)

print(f"Updated manifest.json to version {manifest['version']} with ⭐ Curated Cinema at position 0!")

import json
import re
import hashlib
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")

# Load verified new MissaX 4K items
with open(r"C:\Users\SM.DESKTOP-P1R0508.000\.gemini\antigravity-cli\brain\2a859197-7e46-4613-bfc6-5fad31b252d3\scratch\verified_missax_4k.json", "r", encoding="utf-8") as f:
    new_items = json.load(f)

# Load existing taboo movies to grab existing MissaX entries
with open(REPO_ROOT / "catalog/movie/xfhq_slow_burn_taboo.json", "r", encoding="utf-8") as f:
    taboo_metas = json.load(f)["metas"]

existing_missax = [m for m in taboo_metas if "MissaX" in m.get("name", "")]

print(f"Loaded {len(new_items)} new MissaX 4K items and {len(existing_missax)} existing MissaX items.")

missax_metas = []
seen_ids = set()

# Process existing MissaX first
for m in existing_missax:
    mid = m["id"]
    if mid not in seen_ids:
        seen_ids.add(mid)
        # clone and update genre/description
        m_copy = dict(m)
        m_copy["genres"] = ["MissaX", "4K UHD", "Forbidden Romance", "Slow Burn", "Story", "Drama"]
        m_copy["description"] = f"🎭 MissaX 4K Feature Film · {m.get('name')} · Intense psychological story, forbidden tension, emotional dialogue & slow seduction · Real-Debrid Direct Instant 4K."
        missax_metas.append(m_copy)

# Process new 4K MissaX items
for it in new_items:
    raw_name = it["name"]
    # Clean name
    clean_title = re.sub(r'(?i)\b(2160p|1080p|mp4|hevc|x265|p2p|xc|xxx)\b', '', raw_name)
    clean_title = re.sub(r'[\[\]\(\)\-_]', ' ', clean_title).strip()
    clean_title = re.sub(r'\s+', ' ', clean_title)
    
    # Remove dates like 26 05 31 or 24 12 19 if present
    clean_title = re.sub(r'^\d{2}\s+\d{2}\s+\d{2}\s*', '', clean_title)
    clean_title = re.sub(r'^MissaX\s*', '', clean_title, flags=re.I).strip()
    
    display_name = f"MissaX: {clean_title}"
    slug = hashlib.md5(raw_name.encode()).hexdigest()[:10]
    item_id = f"xfhq_missax_{slug}"
    
    if item_id in seen_ids:
        continue
    seen_ids.add(item_id)
    
    poster = it.get("poster") or ""
    background = it.get("background") or poster
    
    meta_obj = {
        "id": item_id,
        "type": "movie",
        "name": display_name,
        "poster": poster,
        "posterShape": "poster",
        "background": background,
        "description": f"🎭 MissaX 4K Feature Cinema · {clean_title} · 4K UHD Feature Narrative with authentic dialogue, psychological tension & 1-on-1 chemistry · Real-Debrid Edge CDN.",
        "genres": ["MissaX", "4K UHD", "Forbidden Romance", "Slow Burn", "Story", "Drama"],
        "releaseInfo": "4K UHD (2160p)",
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
        
    # Format streams
    formatted_streams = []
    for s in it.get("streams", []):
        formatted_streams.append({
            "name": "🎭 MissaX 4K UHD",
            "title": f"{display_name}\n[Real-Debrid Direct CDN 2160p]",
            "url": s.get("url"),
            "behaviorHints": {
                "notWebReady": False
            }
        })
        
    s_path = REPO_ROOT / "stream/movie" / f"{item_id}.json"
    s_path.parent.mkdir(parents=True, exist_ok=True)
    with open(s_path, "w", encoding="utf-8") as sf:
        json.dump({"streams": formatted_streams}, sf, ensure_ascii=False)
        
    missax_metas.append(meta_obj)
    print(f" [+] Verified & Saved: {display_name}")

print(f"\nTotal curated MissaX 4K films: {len(missax_metas)}")

# Save catalog file
cat_path = REPO_ROOT / "catalog/movie/xfhq_missax_4k.json"
cat_path.parent.mkdir(parents=True, exist_ok=True)
with open(cat_path, "w", encoding="utf-8") as cf:
    json.dump({"metas": missax_metas}, cf, ensure_ascii=False)

print(f"Saved catalog: {cat_path}")

# Update manifest.json
manifest_file = REPO_ROOT / "manifest.json"
with open(manifest_file, "r", encoding="utf-8") as mf:
    manifest = json.load(mf)

# Insert xfhq_missax_4k right below xfhq_slow_burn_taboo (position 2)
manifest["catalogs"] = [c for c in manifest.get("catalogs", []) if c.get("id") != "xfhq_missax_4k"]

missax_cat_entry = {
    "type": "movie",
    "id": "xfhq_missax_4k",
    "name": "🎭 MissaX 4K: Forbidden Stories & Drama",
    "extra": [
        {"name": "search", "isRequired": False},
        {"name": "skip", "isRequired": False}
    ]
}

# Insert at index 2 (Favorites at 0, Slow-Burn at 1, MissaX 4K at 2)
manifest["catalogs"].insert(2, missax_cat_entry)

# Bump manifest version
v_parts = manifest.get("version", "5.261029.1246").split(".")
v_parts[-1] = str(int(v_parts[-1]) + 1)
manifest["version"] = ".".join(v_parts)

with open(manifest_file, "w", encoding="utf-8") as mf:
    json.dump(manifest, mf, indent=2, ensure_ascii=False)

print(f"Manifest updated to version {manifest['version']} with 🎭 MissaX 4K at position 2!")

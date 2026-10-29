import json
import re
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")
PAGE_SIZE = 100

BLOCK_PATTERNS = re.compile(r"""
    \btentacle\b | \bhorror\b | \bscreaming\b | prison\s*parade |
    \bpiss\b | \burine\b | watersport | \bscat\b |
    pgad | unusual\s*people | medical\s*award |
    \bzucchini\b | vegetable | \bveggie\b |
    wifebucket | 33\s*minutes | 36\s*minute |
    glory\s*hole | monster\s*cock | trophy\s*wife |
    sodom | gomorrah | czech\s*fantasy |
    \bbestial\b | \bbizarre\b | extreme\s*insertion |
    riding\s*dirty | rv\s*encounter |
    big\s*dick\s*\d | mike\s*big\s*dick |
    compilation.*\d{2,}\s*min |
    \bchoking\s*down\b | destroys.*tight |
    unrealporn | festivalslut |
    getting\s*fucked\s*hard | fucked\s*hard |
    redneck | \bwreckin\b | john\s*\d\b | bdsm\s*orgy |
    \banal\b | \btrans\b | \bgangbang\b | \borgy\b
""", re.VERBOSE | re.IGNORECASE)

COMMON_SEARCH_TERMS = [
    "shower", "bath", "twerk", "booty", "strip", "solo", "amateur",
    "couple", "selfie", "mirror", "latina", "blonde", "brunette", "creampie"
]

def to_meta(item):
    tags = item.get("tags", [])
    runtime = item.get("runtime", "")
    return {
        "id": item["id"],
        "type": "movie",
        "name": item["name"],
        "poster": item.get("poster") or item.get("thumbnail") or "",
        "background": item.get("poster") or item.get("thumbnail") or "",
        "logo": item.get("logo") or item.get("thumbnail") or "",
        "description": f"⭐ 4K UHD (2160p) · {runtime} · {', '.join(tags[:5])}",
        "genres": tags,
        "releaseInfo": "4K UHD",
        "runtime": str(runtime),
        "behaviorHints": {"defaultVideoId": item["id"]},
    }

print("1. Loading vidi_4k.json...")
with open(REPO_ROOT / "vidi_4k.json", "r", encoding="utf-8") as f:
    raw_items = json.load(f)["items"]

clean_items = []
for it in raw_items:
    text = f"{it.get('name', '')} {it.get('title', '')} {' '.join(it.get('tags', []))}"
    if BLOCK_PATTERNS.search(text):
        continue
    clean_items.append(it)

print(f"Total: {len(raw_items)} -> Cleaned: {len(clean_items)} items.")

metas = [to_meta(it) for it in clean_items]

print("2. Writing catalog/movie/xfhq_4k_uhd...")
cat_dir = REPO_ROOT / "catalog" / "movie" / "xfhq_4k_uhd"
cat_dir.mkdir(parents=True, exist_ok=True)

# Page 0
root_file = REPO_ROOT / "catalog" / "movie" / "xfhq_4k_uhd.json"
root_file.write_text(
    json.dumps({"metas": metas[:PAGE_SIZE]}, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8"
)

# Skip pages
for skip in range(PAGE_SIZE, len(metas), PAGE_SIZE):
    chunk = metas[skip : skip + PAGE_SIZE]
    skip_file = cat_dir / f"skip={skip}.json"
    skip_file.write_text(
        json.dumps({"metas": chunk}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )

# Search pre-indexed pages
for term in COMMON_SEARCH_TERMS:
    matches = [m for m in metas if term.lower() in (m["name"] + " " + " ".join(m.get("genres", []))).lower()][:PAGE_SIZE]
    if matches:
        search_file = cat_dir / f"search={term}.json"
        search_file.write_text(
            json.dumps({"metas": matches}, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8"
        )

print("3. Updating manifest.json...")
manifest_file = REPO_ROOT / "manifest.json"
manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

# Check if xfhq_4k_uhd catalog already in manifest
cat_entry = {
    "type": "movie",
    "id": "xfhq_4k_uhd",
    "name": "⭐ 4K Ultra HD Only (2160p Direct)",
    "extra": [
        {"name": "search", "isRequired": False},
        {"name": "skip", "isRequired": False}
    ]
}

existing_cats = [c for c in manifest["catalogs"] if c["id"] != "xfhq_4k_uhd"]
# Insert at position 1 (right after xfhq_curated_favorites)
if existing_cats and existing_cats[0]["id"] == "xfhq_curated_favorites":
    existing_cats.insert(1, cat_entry)
else:
    existing_cats.insert(0, cat_entry)

manifest["catalogs"] = existing_cats
manifest["version"] = "5.261029.1245"
manifest["description"] = "Curated Stremio Master Suite: 5100+ videos. Dedicated ⭐ 4K Ultra HD Only (2160p Direct) + Natural Solo, Couples & Authentic Mastiraja & FSIBlog Desi MMS Leaks. Filtered and Verified."

manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Manifest updated to version {manifest['version']} with {len(manifest['catalogs'])} catalogs.")

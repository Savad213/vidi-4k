"""
vidi-4k Catalog Rebuilder
Savaa's curated preference — 5 clean rows from vidi_all.json
"""

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent

# ─── HARD NEGATIVE FILTER ────────────────────────────────────────────────────
# Any item whose title OR tags match ANY of these is BLOCKED from all catalogs
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
    redneck | \bwreckin\b | john\s*\d\b | bdsm\s*orgy
""", re.VERBOSE | re.IGNORECASE)

# ─── MINIMUM QUALITY ─────────────────────────────────────────────────────────
ALLOWED_QUALITIES = {"4K", "1080p+"}  # reject 720p, 480p, etc.

# ─── CATALOG DEFINITIONS ─────────────────────────────────────────────────────
CATALOGS = [
    # ── Shower & Wet — narrowest, run FIRST before solo eats them ──
    {
        "id": "xfhq_shower_wet",
        "name": "Nude Shower & Wet Bath (1080p+)",
        "require_tags": {"Shower", "Bath", "Soapy"},
        "require_any": True,
        "block_tags": {"Pissing", "Tentacle", "Horror", "GiantDildo", "HugeAnalDildo",
                       "Couples", "AmateurCouple", "Blowjob", "Facial", "Cumshot"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|screaming|monster|wifebucket|compilation|fucked hard|getting fuck|fuck.*shower|blowjob|cock|dick|pounded)"),
    },
    # ── Latina — run SECOND ──
    {
        "id": "xfhq_latina_solo",
        "name": "Latina Solo & Curves (1080p+)",
        "require_tags": {"Latina", "Latin"},
        "require_any": True,
        "block_tags": {"Pissing", "GiantDildo", "HugeAnalDildo",
                       "Blowjob", "Facial", "Cumshot"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|wifebucket|compilation|blowjob|fucked|cock|dick|pounded|cumshot|facial|gangbang)"),
    },
    # ── Thick Booty — run THIRD ──
    {
        "id": "xfhq_thick_booty",
        "name": "Thick Booty, Curvy & Twerk (1080p+)",
        "require_tags": {"BigAss", "BubbleButt", "Twerking", "Ass", "Curvy",
                         "ThickBooty", "BigButt", "Booty", "Thick"},
        "require_any": True,
        "block_tags": {"Pissing", "GiantDildo", "HugeAnalDildo",
                       "Blowjob", "Facial", "Cumshot", "AnatPlay"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|wifebucket|blowjob|fucked|cock|dick|pounded|cumshot|facial|gangbang|creampie|wreckin|greasy|redneck|john\s*\d)"),
    },
    # ── Couple & Girl-Girl — FOURTH ──
    {
        "id": "xfhq_couple_girlgirl",
        "name": "Real Couple & Girl-Girl (1080p+)",
        "require_tags": {"Couples", "AmateurCouple", "Homemade", "Lesbians",
                         "Girls", "Lesbian", "GirlOnGirl", "Fucking",
                         "Doggystyle", "Cowgirl", "Missionary", "Blowjob",
                         "RealCouple", "Creampie"},
        "require_any": True,
        "block_tags": {"Pissing", "Scat", "Tentacle", "Horror", "GiantDildo", "HugeAnalDildo"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|prison|wifebucket|pgad|unusual people|zucchini|sodom|gomorrah|glory hole|czech fantasy|screaming|cocks and pussies galore|unrealporn|redneck|john\s*\d)"),
    },
    # ── Solo Tease — LAST ──
    {
        "id": "xfhq_solo_tease",
        "name": "Solo Tease & Strip (1080p+)",
        "require_tags": {"Solo", "Teasing", "Striptease", "Onlyfans", "Lingerie",
                         "Undress", "Selfie", "NakedSelfie", "Beautiful",
                         "Naked", "Flashing", "OnlyfansModels", "Amateurs",
                         "Masturbation", "Fingering", "Orgasm", "Dildo",
                         "BigTits", "Blonde", "Brunette", "Tattoo", "Shaved"},
        "require_any": True,
        "block_tags": {"Pissing", "Scat", "Tentacle", "Horror", "GiantDildo", "HugeAnalDildo",
                       "Blowjob", "Facial", "Cumshot", "BigCock"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|prison|wifebucket|pgad|unusual people|zucchini|sodom|gomorrah|glory hole|czech fantasy|compilation.*\d{2}\s*min|blowjob|fucked.*him|rides.*him|pounded|cumshot|facial|cock|big dick|riding dirty|screaming|chaos|orgy|jerked|bdsm)"),
    },
]

PAGE_SIZE = 100  # items per catalog page


def text_for_item(item):
    """Combine name + tags for matching."""
    tags = item.get("tags", [])
    return item.get("name", "") + " " + " ".join(tags)


def item_passes_global(item):
    """Global hard block + quality filter."""
    if item.get("quality") not in ALLOWED_QUALITIES:
        return False
    txt = text_for_item(item)
    if BLOCK_PATTERNS.search(txt):
        return False
    return True


def item_passes_catalog(item, cat):
    """Per-catalog tag and title filters."""
    tags = set(item.get("tags", []))
    name = item.get("name", "")

    # Must have at least one required tag
    if cat["require_any"]:
        if not tags.intersection(cat["require_tags"]):
            return False

    # Must not have any blocked tag
    if tags.intersection(cat["block_tags"]):
        return False

    # Must not match blocked title pattern
    if cat["block_title"].search(name):
        return False

    return True


def to_stremio_meta(item):
    """Convert vidi_all item to Stremio catalog meta."""
    return {
        "id": item["id"],
        "type": "movie",
        "name": item["name"],
        "poster": item.get("poster") or item.get("thumbnail") or "",
        "background": item.get("poster") or item.get("thumbnail") or "",
        "logo": item.get("logo") or item.get("thumbnail") or "",
        "description": f"{item.get('quality','?')} · {item.get('runtime','?')} · {', '.join(item.get('tags', [])[:5])}",
        "genres": item.get("tags", []),
        "releaseInfo": item.get("quality", ""),
        "runtime": item.get("runtime", ""),
        "behaviorHints": {"defaultVideoId": item["id"]},
    }


def write_paginated(cat_dir: Path, metas: list, cat_name: str):
    """Write skip-paginated JSON files for a catalog."""
    cat_dir.mkdir(parents=True, exist_ok=True)

    # Base page (first 100)
    base = {"metas": metas[:PAGE_SIZE]}
    (cat_dir.parent / f"{cat_dir.name}.json").write_text(
        json.dumps(base, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )

    # Skip pages
    for skip in range(PAGE_SIZE, len(metas), PAGE_SIZE):
        chunk = metas[skip: skip + PAGE_SIZE]
        skip_file = cat_dir / f"skip={skip}.json"
        skip_file.write_text(
            json.dumps({"metas": chunk}, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

    print(f"  [{cat_name}] {len(metas)} items → {1 + max(0, (len(metas)-1)//PAGE_SIZE)} pages")


def build():
    print("Loading vidi_all.json …")
    pool = json.loads((REPO_ROOT / "vidi_all.json").read_text(encoding="utf-8"))
    items = pool["items"]
    print(f"  Total items in pool: {len(items)}")

    # Global filter
    items = [i for i in items if item_passes_global(i)]
    print(f"  After quality + global block filter: {len(items)}")

    # Deduplicate by id
    seen = set()
    unique = []
    for i in items:
        if i["id"] not in seen:
            seen.add(i["id"])
            unique.append(i)
    items = unique
    print(f"  After dedup: {len(items)}")

    # Sort 4K first, then by likes desc
    items.sort(key=lambda x: (0 if x.get("quality") == "4K" else 1, -x.get("likes", 0)))

    # Per-catalog assignment — each ID goes to first matching catalog only
    assigned_ids = set()
    catalog_results = {}

    for cat in CATALOGS:
        matched = []
        for item in items:
            if item["id"] in assigned_ids:
                continue
            if item_passes_catalog(item, cat):
                matched.append(item)

        # Mark as assigned
        for item in matched:
            assigned_ids.add(item["id"])

        catalog_results[cat["id"]] = {
            "name": cat["name"],
            "metas": [to_stremio_meta(i) for i in matched],
            "raw_items": matched,
        }
        print(f"  Catalog '{cat['name']}': {len(matched)} items")

    # Write catalog files
    print("\nWriting catalog files …")
    cat_movie_dir = REPO_ROOT / "catalog" / "movie"
    for cat in CATALOGS:
        cid = cat["id"]
        result = catalog_results[cid]
        cat_dir = cat_movie_dir / cid
        write_paginated(cat_dir, result["metas"], result["name"])

    # Write clean M3U playlists
    print("\nWriting clean M3U playlists …")
    m3u_all_lines = ["#EXTM3U", "#PLAYLIST:xfree HQ Curated Vertical"]
    m3u_4k_lines = ["#EXTM3U", "#PLAYLIST:xfree 4K Curated Vertical"]

    for cat in CATALOGS:
        cid = cat["id"]
        cname = cat["name"].split(" (")[0]
        for it in catalog_results[cid]["raw_items"]:
            dur = it.get("duration", 0)
            iid = it.get("id", "")
            title = it.get("name", "").replace('"', '').replace(',', ' ')
            logo = it.get("poster") or it.get("thumbnail") or ""
            stream = it.get("stream_url") or it.get("url") or ""
            qual = it.get("quality", "1080p+")
            
            line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [{qual} Vertical]'
            m3u_all_lines.append(line_inf)
            m3u_all_lines.append(stream)
            
            if qual == "4K":
                m3u_4k_lines.append(line_inf)
                m3u_4k_lines.append(stream)

    (REPO_ROOT / "playlist.m3u").write_text("\n".join(m3u_all_lines), encoding="utf-8")
    (REPO_ROOT / "playlist_4k.m3u").write_text("\n".join(m3u_4k_lines), encoding="utf-8")
    print(f"  playlist.m3u written: {len(m3u_all_lines)//2} streams")
    print(f"  playlist_4k.m3u written: {len(m3u_4k_lines)//2} streams (pure 4K)")

    # Write manifest.json
    print("\nWriting manifest.json …")
    catalogs_manifest = []
    for cat in CATALOGS:
        cid = cat["id"]
        total = len(catalog_results[cid]["metas"])
        extra = [{"name": "skip", "isRequired": False}]
        catalogs_manifest.append({
            "type": "movie",
            "id": cid,
            "name": catalog_results[cid]["name"],
            "extra": extra,
        })

    manifest = {
        "id": "com.lo.xfree.hq",
        "version": "2.261026.1421",
        "name": "xfree HQ – Curated Solo, Booty, Shower & Couple",
        "description": (
            f"Savaa curated: {sum(len(r['metas']) for r in catalog_results.values())} "
            f"vertical videos (1080p+ & 4K). "
            f"Solo Tease · Thick Booty · Shower · Latina · Couple & Girl-Girl."
        ),
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["xfhq"],
        "catalogs": catalogs_manifest,
        "behaviorHints": {"adult": True, "configurable": False},
    }
    (REPO_ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Summary
    print("\n✅ Build complete!")
    print(f"  Total assigned: {len(assigned_ids)}")
    for cat in CATALOGS:
        print(f"  {cat['name']}: {len(catalog_results[cat['id']]['metas'])}")


if __name__ == "__main__":
    build()

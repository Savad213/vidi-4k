"""
Full Suite Rebuilder for vidi-4k
Integrates:
- 5 xfree Curated Catalogs (1080p+ & 4K)
- 2 Desi MMS Curated Catalogs (480p+ Direct Cloudflare CDN)
- Generates meta & stream files for Desi items
- Updates manifest.json with 7 premier catalogs
- Generates playlist.m3u, playlist_4k.m3u, playlist_desi.m3u
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent
VIDI_ALL = REPO_ROOT / "vidi_all.json"
DESI_ALL = REPO_ROOT / "desi_all.json"

PAGE_SIZE = 100

# ── 1. GLOBAL BLOCK LIST ──────────────────────────────────────────────────────
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

WESTERN_STARS = re.compile(r"(?i)\b(violet myers|riley reid|lana rhoades|mia malkova|eva elfie|angela white|abella danger|kendra lust|brandi love|cory chase|alexis texas)\b")

# ── 2. XFREE 5 CATALOGS ───────────────────────────────────────────────────────
XFREE_CATALOGS = [
    {
        "id": "xfhq_shower_wet",
        "name": "Nude Shower & Wet Bath (1080p+)",
        "require_tags": {"Shower", "Bath", "Soapy"},
        "require_any": True,
        "block_tags": {"Pissing", "Tentacle", "Horror", "GiantDildo", "HugeAnalDildo",
                       "Couples", "AmateurCouple", "Blowjob", "Facial", "Cumshot"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|screaming|monster|wifebucket|compilation|fucked hard|getting fuck|fuck.*shower|blowjob|cock|dick|pounded)"),
    },
    {
        "id": "xfhq_latina_solo",
        "name": "Latina Solo & Curves (1080p+)",
        "require_tags": {"Latina", "Latin"},
        "require_any": True,
        "block_tags": {"Pissing", "GiantDildo", "HugeAnalDildo",
                       "Blowjob", "Facial", "Cumshot"},
        "block_title": re.compile(r"(?i)(tentacle|horror|piss|wifebucket|compilation|blowjob|fucked|cock|dick|pounded|cumshot|facial|gangbang)"),
    },
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

def to_meta(item):
    return {
        "id": item["id"],
        "type": "movie",
        "name": item["name"],
        "poster": item.get("poster") or item.get("thumbnail") or "",
        "background": item.get("poster") or item.get("thumbnail") or "",
        "logo": item.get("logo") or item.get("thumbnail") or "",
        "description": f"{item.get('quality','480p+')} · {item.get('runtime','MMS')} · {', '.join(item.get('tags', [])[:5])}",
        "genres": item.get("tags", []),
        "releaseInfo": item.get("quality", "1080p+"),
        "runtime": item.get("runtime", ""),
        "behaviorHints": {"defaultVideoId": item["id"]},
    }

def write_paginated(cat_dir: Path, metas: list):
    cat_dir.mkdir(parents=True, exist_ok=True)
    base = {"metas": metas[:PAGE_SIZE]}
    (cat_dir.parent / f"{cat_dir.name}.json").write_text(
        json.dumps(base, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    for skip in range(PAGE_SIZE, len(metas), PAGE_SIZE):
        chunk = metas[skip: skip + PAGE_SIZE]
        skip_file = cat_dir / f"skip={skip}.json"
        skip_file.write_text(
            json.dumps({"metas": chunk}, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

def main():
    print("=== Step 1: Processing xfree Videos ===")
    vidi_pool = json.loads(VIDI_ALL.read_text(encoding="utf-8"))["items"]
    clean_vidi = []
    seen = set()
    for it in vidi_pool:
        if it.get("quality") not in {"4K", "1080p+"}:
            continue
        txt = it.get("name", "") + " " + " ".join(it.get("tags", []))
        if BLOCK_PATTERNS.search(txt):
            continue
        if it["id"] not in seen:
            seen.add(it["id"])
            clean_vidi.append(it)

    clean_vidi.sort(key=lambda x: (0 if x.get("quality") == "4K" else 1, -x.get("likes", 0)))

    assigned_vidi = set()
    catalog_results = {}

    for cat in XFREE_CATALOGS:
        matched = []
        for it in clean_vidi:
            if it["id"] in assigned_vidi:
                continue
            tags = set(it.get("tags", []))
            name = it.get("name", "")
            if not tags.intersection(cat["require_tags"]):
                continue
            if tags.intersection(cat["block_tags"]):
                continue
            if cat["block_title"].search(name):
                continue
            matched.append(it)
            assigned_vidi.add(it["id"])

        catalog_results[cat["id"]] = {
            "name": cat["name"],
            "metas": [to_meta(i) for i in matched],
            "raw_items": matched,
        }
        print(f"  {cat['name']}: {len(matched)} items")

    print("\n=== Step 2: Processing Desi MMS Videos ===")
    desi_pool = json.loads(DESI_ALL.read_text(encoding="utf-8"))["items"]
    clean_desi = []
    desi_seen = set()

    for it in desi_pool:
        name = it.get("name", "")
        tags = it.get("tags", [])
        txt = name + " " + " ".join(tags)
        
        # Block Western stars & global filth
        if WESTERN_STARS.search(name) or BLOCK_PATTERNS.search(txt):
            continue
        
        # Verify genuine Desi context
        desi_context = ['desi', 'indian', 'bhabhi', 'mallu', 'tamil', 'village', 'girlfriend',
                        'wife', 'cheating', 'aunt', 'aunty', 'pakistani', 'punjabi', 'bengali',
                        'marathi', 'kannada', 'telugu', 'college', 'mms', 'leaked', 'viral',
                        'chubby', 'saree', 'salwar', 'shikha', 'pooja', 'neha', 'priya',
                        'anjali', 'sonia', 'newly-married', 'desitales', 'masa49', 'vid65']
        if not any(k in txt.lower() for k in desi_context):
            continue

        if it["id"] not in desi_seen:
            desi_seen.add(it["id"])
            clean_desi.append(it)

    print(f"  Clean genuine Desi items: {len(clean_desi)}")

    # Split into 2 Desi catalogs: MMS/Phonecam vs Solo Tease
    desi_tease_items = []
    desi_mms_items = []

    tease_indicators = re.compile(r"(?i)(strip|tease|cam|solo|seduction|chubby|lingerie|saree|flick|touch|undress|mirror|snap)")

    for it in clean_desi:
        txt = it["name"] + " " + " ".join(it.get("tags", []))
        if tease_indicators.search(txt) and "fuck" not in it["name"].lower():
            desi_tease_items.append(it)
        else:
            desi_mms_items.append(it)

    catalog_results["xfhq_desi_mms"] = {
        "name": "Desi Leaked MMS & Viral Phonecam (480p+)",
        "metas": [to_meta(i) for i in desi_mms_items],
        "raw_items": desi_mms_items,
    }
    catalog_results["xfhq_desi_tease"] = {
        "name": "Desi Girlfriend & Bhabhi Tease (480p+)",
        "metas": [to_meta(i) for i in desi_tease_items],
        "raw_items": desi_tease_items,
    }
    print(f"  Desi Leaked MMS & Viral Phonecam: {len(desi_mms_items)} items")
    print(f"  Desi Girlfriend & Bhabhi Tease: {len(desi_tease_items)} items")

    print("\n=== Step 3: Writing Static Stream & Meta JSONs for Desi Items ===")
    meta_dir = REPO_ROOT / "meta" / "movie"
    stream_dir = REPO_ROOT / "stream" / "movie"
    meta_dir.mkdir(parents=True, exist_ok=True)
    stream_dir.mkdir(parents=True, exist_ok=True)

    for it in clean_desi:
        vid_id = it["id"]
        # meta file
        m_file = meta_dir / f"{vid_id}.json"
        meta_obj = {
            "meta": {
                "id": vid_id,
                "type": "movie",
                "name": it["name"],
                "poster": it.get("poster") or it.get("thumbnail") or "",
                "posterShape": "poster",
                "background": it.get("poster") or it.get("thumbnail") or "",
                "description": f"480p+ Direct Cloudflare CDN · Authentic Desi MMS · {', '.join(it.get('tags', [])[:5])}",
                "genres": it.get("tags", ["Indian", "Desi", "MMS"]),
                "releaseInfo": "480p+",
                "runtime": "MMS"
            }
        }
        m_file.write_text(json.dumps(meta_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

        # stream file
        s_file = stream_dir / f"{vid_id}.json"
        stream_obj = {
            "streams": [
                {
                    "url": it["stream_url"],
                    "name": "Desi MMS Direct CDN",
                    "title": f"{it['name']} [480p+ Direct Cloudflare CDN]",
                    "behaviorHints": {"notWebReady": False}
                }
            ]
        }
        s_file.write_text(json.dumps(stream_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    print(f"  Wrote {len(clean_desi)} meta & stream JSON files.")

    print("\n=== Step 4: Writing 7 Catalog Pagination Files ===")
    ALL_CATALOG_ORDER = [
        # Premier xfree
        ("xfhq_shower_wet", "Nude Shower & Wet Bath (1080p+)"),
        ("xfhq_latina_solo", "Latina Solo & Curves (1080p+)"),
        ("xfhq_thick_booty", "Thick Booty, Curvy & Twerk (1080p+)"),
        ("xfhq_couple_girlgirl", "Real Couple & Girl-Girl (1080p+)"),
        ("xfhq_solo_tease", "Solo Tease & Strip (1080p+)"),
        # Authentic Desi
        ("xfhq_desi_mms", "Desi Leaked MMS & Viral Phonecam (480p+)"),
        ("xfhq_desi_tease", "Desi Girlfriend & Bhabhi Tease (480p+)"),
    ]

    cat_movie_dir = REPO_ROOT / "catalog" / "movie"
    catalogs_manifest = []

    for cid, cname in ALL_CATALOG_ORDER:
        res = catalog_results[cid]
        cat_dir = cat_movie_dir / cid
        write_paginated(cat_dir, res["metas"])
        catalogs_manifest.append({
            "type": "movie",
            "id": cid,
            "name": res["name"],
            "extra": [{"name": "skip", "isRequired": False}]
        })

    print("\n=== Step 5: Updating manifest.json ===")
    total_all_videos = sum(len(catalog_results[c[0]]["metas"]) for c in ALL_CATALOG_ORDER)
    manifest = {
        "id": "com.lo.xfree.hq",
        "version": "2.261026.1500",
        "name": "xfree HQ + Desi MMS (Curated 4K & Leaks)",
        "description": (
            f"Savaa curated master suite: {total_all_videos} videos. "
            f"5 Curated 4K/1080p rows + 2 Authentic Desi MMS & Tease rows. "
            f"Zero junk, pure direct high-bitrate streaming."
        ),
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["xfhq", "desi_"],
        "catalogs": catalogs_manifest,
        "behaviorHints": {"adult": True, "configurable": False},
    }
    (REPO_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== Step 6: Generating M3U Playlists ===")
    # 1. playlist.m3u (xfree)
    # 2. playlist_4k.m3u (xfree 4K)
    # 3. playlist_desi.m3u (Desi MMS)
    m3u_all = ["#EXTM3U", "#PLAYLIST:xfree HQ Curated Vertical"]
    m3u_4k = ["#EXTM3U", "#PLAYLIST:xfree 4K Curated Vertical"]
    m3u_desi = ["#EXTM3U", "#PLAYLIST:Desi Leaked MMS & Authentic Phonecam"]

    for cid, _ in ALL_CATALOG_ORDER[:5]:
        cname = catalog_results[cid]["name"].split(" (")[0]
        for it in catalog_results[cid]["raw_items"]:
            dur = it.get("duration", 0)
            iid = it.get("id", "")
            title = it.get("name", "").replace('"', '').replace(',', ' ')
            logo = it.get("poster") or it.get("thumbnail") or ""
            stream = it.get("stream_url") or it.get("url") or ""
            qual = it.get("quality", "1080p+")
            line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [{qual} Vertical]'
            m3u_all.append(line_inf)
            m3u_all.append(stream)
            if qual == "4K":
                m3u_4k.append(line_inf)
                m3u_4k.append(stream)

    for cid in ["xfhq_desi_mms", "xfhq_desi_tease"]:
        cname = catalog_results[cid]["name"].split(" (")[0]
        for it in catalog_results[cid]["raw_items"]:
            dur = 120
            iid = it.get("id", "")
            title = it.get("name", "").replace('"', '').replace(',', ' ')
            logo = it.get("poster") or it.get("thumbnail") or ""
            stream = it.get("stream_url")
            line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [480p+ Desi MMS]'
            m3u_desi.append(line_inf)
            m3u_desi.append(stream)

    (REPO_ROOT / "playlist.m3u").write_text("\n".join(m3u_all), encoding="utf-8")
    (REPO_ROOT / "playlist_4k.m3u").write_text("\n".join(m3u_4k), encoding="utf-8")
    (REPO_ROOT / "playlist_desi.m3u").write_text("\n".join(m3u_desi), encoding="utf-8")

    print(f"  playlist.m3u: {len(m3u_all)//2} items")
    print(f"  playlist_4k.m3u: {len(m3u_4k)//2} items (pure 4K)")
    print(f"  playlist_desi.m3u: {len(m3u_desi)//2} items (authentic Desi MMS)")
    print("\n✅ MASTER SUITE BUILD COMPLETE!")

if __name__ == "__main__":
    main()

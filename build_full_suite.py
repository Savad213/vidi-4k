"""
Master Suite Rebuilder for Stremio: 100% Natural Solo & Authentic Curation
Strictly excludes:
- Any male performers, dudes, penetration, couples, blowjobs, groaning guys, male names
- Pregnant women / baby bumps / maternity
- Black / Ebony categories
- Old / mature / granny / aging women
- Anime / 3D / Hentai / cartoons / cosplay
- Flat / very thin / skinny / petite bodies (curvy & thick natural figures only)
- Weird rear gaping / extreme openings / prolapse
- Group scenes / threesomes / orgies
- Rough / hardcore / BDSM / choking / slapping / submissive / pain / deflowering
- Toys / dildos / vibrators / butt plugs / machines / vegetables
"""

import json
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent
VIDI_ALL = REPO_ROOT / "vidi_all.json"
DESI_ALL = REPO_ROOT / "desi_all.json"
MASTIRAJA_ALL = REPO_ROOT / "mastiraja_all.json"

PAGE_SIZE = 100

# 1. COMPREHENSIVE NEGATIVE FILTER (Regex)
BLOCK_EVERYTHING = re.compile(r"""(?i)\b(
    # Male roles & references
    dude|dudes|guy|guys|man|men|male|males|boy|boys|boyfriend|boyfriends|bf|husband|husbands|lover|lovers|uncle|boss|driver|handyman|
    devar|jeth|jija|brother|stepbro|stepbrother|stepdad|father|son|doctor|plumber|stranger|cousin|tau\s*ji|chacha|mama|sardar|
    partner|partners|neighbor|neighbors|client|clients|customer|customers|pimp|teacher|sir|servant|guard|watchman|escort|fwb|
    daddy|daddies|sugar\s*daddy|baby\s*daddy|
    he|him|his|cock|cocks|dick|dicks|penis|shaft|balls|bwc|bbc|lund|loda|chochi|
    danny\s*d|johnny\s*sins|jordi|keiran\s*lee|manuel\s*ferrara|jmac|
    
    # Acts with male / couple / oral / penetration / sex
    sex|creampie|creampies|deepthroat|throat|facial|facials|bj|blowjob|blowjobs|handjob|handjobs|
    suck\w*|swallow\w*|cum\s*in|cum\s*on|cumshot\w*|
    doggy|doggystyle|missionary|cowgirl|penetrat\w*|thrust\w*|pounded|pounding|pound|drilling|drilled|drill|
    breeding|bred|breed|piped|piping|pipe|railed|railing|rail|fucking|fucked|fuck|fucks|chudai|
    couple|couples|amateurcouple|realcouple|duo|interracial|honeymoon|quickie|suhagraat|
    split\w*|deflower\w*|virgin|dard|pain\w*|screaming|cry\w*|destroy\w*|destruction|
    ride|rides|riding|rode|getting\s*cum|
    
    # Age safety: Boundary 1 enforcement
    teen|teens|underage|schoolgirl|minor|
    
    # 1. Pregnant ladies
    pregnant|pregnancy|baby\s*bump|expecting|maternity|
    
    # 2. Black color ladies
    ebony|black\s*girl|black\s*woman|dark\s*skin|
    
    # 3. Old ladies
    granny|mature|gilf|grandma|old\s*woman|elderly|wrinkled|senior|aged\s*woman|
    
    # 4. Anime / 3D / Cartoons
    anime|hentai|3d|cartoon|animation|animated|sfm|blender|cosplay|manga|
    
    # 5. Flat / Very Thin / Skinny
    flat|flat\s*chest|flat\s*ass|skinny|very\s*thin|bony|petite|tiny|small\s*tits|small\s*boobs|
    
    # 6. Weird back / gaping / extreme opening
    gape|gaping|prolapse|goatse|fist|fisting|extreme\s*anal|speculum|spread\s*wide\s*open|
    
    # 7. Groups
    group|orgy|gangbang|threesome|foursome|swinger|party|
    
    # 8. Being so hard / rough / BDSM
    rough|hardcore|slap\w*|choke\w*|bdsm|torture|bondage|tied|abuse|punish\w*|slave|submissive|submission|master|mistress|dominat\w*|owned|
    
    # 9. Using toys / plugs / objects / vegetables
    toy|toys|dildo|dildos|vibrator|vibrators|sybian|machine|magic\s*wand|wand|strap|strapon|plug|anal\s*plug|butt\s*plug|
    carrot|cucumber|banana|vegetable|belan|bottle|brush|
    
    # Western stars in Desi
    lena\s*the\s*plug|violet\s*myers|riley\s*reid|lana\s*rhoades|mia\s*malkova|eva\s*elfie|angela\s*white|abella\s*danger|kendra\s*lust|brandi\s*love|cory\s*chase|alexis\s*texas|emily\s*emika|autumn\s*falls|gabbie\s*carter|leah\s*gotti|abigaiil\s*morris|sweetie\s*fox|
    
    # Filth / Other
    pee|piss|pissing|scat|toilet|watersport
)\b|takes?\s*(a|his|big|cock|dick|screaming)|used\s*by|fucked\s*by|choking\s*down|splits?\s*her|getting\s*fingered|holes?\s*filled|stretched\s*by|legs\s*on""", re.VERBOSE)

# 2. DISALLOWED TAG SETS
TOY_TAGS = {'Dildo', 'GiantDildo', 'HugeAnalDildo', 'Vibrator', 'Sybian', 'SexToys', 'Toy', 'Toys', 'AnalPlug', 'ButtPlug'}
PREGNANT_TAGS = {'Pregnant', 'PregnantSolo', 'PregnantTits'}
OLD_TAGS = {'Granny', 'Mature', 'GILF', 'Old'}
SKINNY_TAGS = {'Skinny', 'Petite', 'SmallTits', 'Tiny'}
ANIME_TAGS = {'Hentai', 'Anime', '3D', 'Cosplay'}
EBONY_TAGS = {'Ebony', 'Black'}
GROUP_TAGS = {'Threesome', 'Foursome', 'Group', 'Orgy', 'Couples', 'AmateurCouple', 'RealCouple'}
ROUGH_TAGS = {'BDSM', 'Rough', 'Bondage'}

DISALLOWED_TAGS = TOY_TAGS | PREGNANT_TAGS | OLD_TAGS | SKINNY_TAGS | ANIME_TAGS | EBONY_TAGS | GROUP_TAGS | ROUGH_TAGS

# 3. AUTHENTIC DESI KEYWORDS
DESI_KW = re.compile(r"""(?i)\b(
    desi|indian|bhabhi|mallu|tamil|punjabi|pakistani|bengali|marathi|kannada|telugu|
    saree|salwar|aunty|jatti|randi|baddie|college|hostel|mms|leaked|viral|
    shikha|pooja|neha|priya|anjali|sonia|minahil
)\b""", re.VERBOSE)

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
    print("=== Step 1: Processing xfree Solo Videos (Zero Dudes / Zero Toys) ===")
    vidi_pool = json.loads(VIDI_ALL.read_text(encoding="utf-8"))["items"]
    clean_vidi = []
    seen = set()
    for it in vidi_pool:
        if it.get("quality") not in {"4K", "1080p+"}:
            continue
        tags = set(it.get("tags", []))
        if tags.intersection(DISALLOWED_TAGS):
            continue
        txt = it.get("name", "") + " " + " ".join(tags)
        if BLOCK_EVERYTHING.search(txt):
            continue
        if it["id"] not in seen:
            seen.add(it["id"])
            clean_vidi.append(it)

    clean_vidi.sort(key=lambda x: (0 if x.get("quality") == "4K" else 1, -x.get("likes", 0)))
    print(f"  Total Clean xfree Solo items: {len(clean_vidi)}")

    # Assign to 4 Stremio Solo Catalogs
    assigned_vidi = set()
    catalog_results = {}

    # Catalog 1: Thick Booty & Curvy Flaunt
    thick_items = []
    thick_tags = {"BigAss", "BubbleButt", "Twerking", "Ass", "Curvy", "ThickBooty", "BigButt", "Booty", "Thick"}
    for it in clean_vidi:
        tags = set(it.get("tags", []))
        if tags.intersection(thick_tags):
            thick_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_thick_booty"] = {
        "name": "Thick Booty & Curvy Flaunt (1080p+)",
        "metas": [to_meta(i) for i in thick_items],
        "raw_items": thick_items,
    }
    print(f"  Thick Booty & Curvy Flaunt: {len(thick_items)} items")

    # Catalog 2: Phonecam & Mirror Selfie Tease
    phone_items = []
    phone_kws = re.compile(r"(?i)\b(selfie|mirror|phone|snap|snapchat|bedroom|baddie|amateur|hotel|tiktok)\b")
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        tags = set(it.get("tags", []))
        txt = it["name"] + " " + " ".join(tags)
        if tags.intersection({"Selfie", "NakedSelfie", "Mirror"}) or phone_kws.search(txt):
            phone_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_phone_selfie"] = {
        "name": "Phonecam & Mirror Selfie Tease (1080p+)",
        "metas": [to_meta(i) for i in phone_items],
        "raw_items": phone_items,
    }
    print(f"  Phonecam & Mirror Selfie Tease: {len(phone_items)} items")

    # Catalog 3: Shower & Wet Bath
    shower_items = []
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        tags = set(it.get("tags", []))
        if tags.intersection({"Shower", "Bath", "Soapy"}):
            shower_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_shower_wet"] = {
        "name": "Nude Shower & Wet Bath (1080p+)",
        "metas": [to_meta(i) for i in shower_items],
        "raw_items": shower_items,
    }
    print(f"  Nude Shower & Wet Bath: {len(shower_items)} items")

    # Catalog 4: Pure Solo Tease & Strip
    solo_items = []
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        solo_items.append(it)
        assigned_vidi.add(it["id"])
    catalog_results["xfhq_solo_tease"] = {
        "name": "Pure Solo Tease & Strip (1080p+)",
        "metas": [to_meta(i) for i in solo_items],
        "raw_items": solo_items,
    }
    print(f"  Pure Solo Tease & Strip: {len(solo_items)} items")

    print("\n=== Step 2: Processing Authentic Desi Solo Videos ===")
    desi_pool = json.loads(DESI_ALL.read_text(encoding="utf-8"))["items"]
    if MASTIRAJA_ALL.exists():
        masti_pool = json.loads(MASTIRAJA_ALL.read_text(encoding="utf-8"))["items"]
        print(f"  Loaded {len(masti_pool)} videos from Mastiraja")
        desi_pool.extend(masti_pool)

    clean_desi = []
    desi_seen = set()

    for it in desi_pool:
        tags = set(it.get("tags", []))
        if tags.intersection(DISALLOWED_TAGS):
            continue
        txt = it.get("name", "") + " " + " ".join(tags)
        if BLOCK_EVERYTHING.search(txt):
            continue
        if not DESI_KW.search(txt):
            continue
        if it["id"] not in desi_seen:
            desi_seen.add(it["id"])
            clean_desi.append(it)

    print(f"  Total Clean Desi Solo items: {len(clean_desi)}")

    # Split into 3 Requested Desi Catalogs:
    # 1. Pakistani Solo & Cam Leaks
    # 2. Desi Nude (Solo & Natural)
    # 3. Desi Leaked MMS (Phonecam Solo)
    paki_pat = re.compile(r"(?i)\b(pakistan|pakistani|lahore|karachi|islamabad|minahil|alina|imsha|alisha)\b")
    nude_pat = re.compile(r"(?i)\b(nude|naked|strip|shower|bath|boob|boobs|tits|bouncing|flaunt|terrace)\b")

    assigned_desi = set()
    paki_items = []
    nude_items = []
    mms_items = []

    for it in clean_desi:
        txt = it["name"] + " " + " ".join(it.get("tags", []))
        if paki_pat.search(txt):
            paki_items.append(it)
            assigned_desi.add(it["id"])

    for it in clean_desi:
        if it["id"] in assigned_desi:
            continue
        txt = it["name"] + " " + " ".join(it.get("tags", []))
        if nude_pat.search(txt):
            nude_items.append(it)
            assigned_desi.add(it["id"])

    for it in clean_desi:
        if it["id"] in assigned_desi:
            continue
        mms_items.append(it)
        assigned_desi.add(it["id"])

    catalog_results["xfhq_desi_nude"] = {
        "name": "Desi Nude (Solo & Natural)",
        "metas": [to_meta(i) for i in nude_items],
        "raw_items": nude_items,
    }
    catalog_results["xfhq_desi_mms"] = {
        "name": "Desi Leaked MMS (Phonecam Solo)",
        "metas": [to_meta(i) for i in mms_items],
        "raw_items": mms_items,
    }
    catalog_results["xfhq_desi_pakistan"] = {
        "name": "Pakistani Solo & Cam Leaks",
        "metas": [to_meta(i) for i in paki_items],
        "raw_items": paki_items,
    }
    print(f"  Desi Nude (Solo & Natural): {len(nude_items)} items")
    print(f"  Desi Leaked MMS (Phonecam Solo): {len(mms_items)} items")
    print(f"  Pakistani Solo & Cam Leaks: {len(paki_items)} items")

    print("\n=== Step 3: Writing Static Stream & Meta JSONs for Desi Items ===")
    meta_dir = REPO_ROOT / "meta" / "movie"
    stream_dir = REPO_ROOT / "stream" / "movie"
    meta_dir.mkdir(parents=True, exist_ok=True)
    stream_dir.mkdir(parents=True, exist_ok=True)

    for it in clean_desi:
        vid_id = it["id"]
        is_masti = "masti_" in vid_id
        source_name = "Mastiraja 3.1 Mbps" if is_masti else "Cloudflare CDN 1.8 Mbps"

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
                "description": f"Direct {source_name} · Authentic Desi Solo · {', '.join(it.get('tags', [])[:5])}",
                "genres": it.get("tags", ["Indian", "Desi", "Solo"]),
                "releaseInfo": "480p+",
                "runtime": "MMS"
            }
        }
        m_file.write_text(json.dumps(meta_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

        # stream file with proxyHeaders for Mastiraja to prevent 403 Forbidden
        s_file = stream_dir / f"{vid_id}.json"
        stream_entry = {
            "url": it["stream_url"],
            "name": source_name,
            "title": f"{it['name']} [{source_name} High Bitrate]",
            "behaviorHints": {
                "notWebReady": False
            }
        }
        if is_masti:
            stream_entry["behaviorHints"]["proxyHeaders"] = {
                "request": {
                    "Referer": "https://mastiraja.tv/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }

        stream_obj = {"streams": [stream_entry]}
        s_file.write_text(json.dumps(stream_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    print(f"  Wrote {len(clean_desi)} meta & stream JSON files.")

    print("\n=== Step 4: Refreshing Catalog Directories ===")
    cat_movie_dir = REPO_ROOT / "catalog" / "movie"
    if cat_movie_dir.exists():
        for item in cat_movie_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.suffix == ".json":
                item.unlink()

    ALL_CATALOG_ORDER = [
        # Global Creator Suite
        ("xfhq_thick_booty", "Thick Booty & Curvy Flaunt (1080p+)"),
        ("xfhq_phone_selfie", "Phonecam & Mirror Selfie Tease (1080p+)"),
        ("xfhq_shower_wet", "Nude Shower & Wet Bath (1080p+)"),
        ("xfhq_solo_tease", "Pure Solo Tease & Strip (1080p+)"),
        # Desi Authentic Suite
        ("xfhq_desi_nude", "Desi Nude (Solo & Natural)"),
        ("xfhq_desi_mms", "Desi Leaked MMS (Phonecam Solo)"),
        ("xfhq_desi_pakistan", "Pakistani Solo & Cam Leaks"),
    ]

    catalogs_manifest = []

    for cid, _ in ALL_CATALOG_ORDER:
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
        "id": "com.savaa.stremio.solo",
        "version": "3.261026.1550",
        "name": "Natural Solo & Desi MMS (1080p+)",
        "description": (
            f"Curated Stremio Master Suite: {total_all_videos} videos across 7 categories. "
            f"1080p+/4K Natural Solo & Authentic Desi/Pakistani Leaks. "
            f"Strictly zero males, zero couples, zero toys, pure natural aesthetics."
        ),
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["xfhq", "desi_", "masti_"],
        "catalogs": catalogs_manifest,
        "behaviorHints": {"adult": True, "configurable": False},
    }
    (REPO_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== Step 6: Generating M3U Playlists ===")
    m3u_all = ["#EXTM3U", "#PLAYLIST:Stremio Curated Natural Solo"]
    m3u_4k = ["#EXTM3U", "#PLAYLIST:Stremio 4K Natural Solo"]
    m3u_desi = ["#EXTM3U", "#PLAYLIST:Desi Authentic Solo MMS"]

    for cid, _ in ALL_CATALOG_ORDER[:4]:
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

    for cid in ["xfhq_desi_nude", "xfhq_desi_mms", "xfhq_desi_pakistan"]:
        cname = catalog_results[cid]["name"].split(" (")[0]
        for it in catalog_results[cid]["raw_items"]:
            dur = 120
            iid = it.get("id", "")
            title = it.get("name", "").replace('"', '').replace(',', ' ')
            logo = it.get("poster") or it.get("thumbnail") or ""
            stream = it.get("stream_url")
            is_masti = "masti_" in iid
            line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [480p+ Desi Solo]'
            m3u_desi.append(line_inf)
            if is_masti:
                m3u_desi.append("#EXTVLCOPT:http-referrer=https://mastiraja.tv/")
                m3u_desi.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            m3u_desi.append(stream)

    (REPO_ROOT / "playlist.m3u").write_text("\n".join(m3u_all), encoding="utf-8")
    (REPO_ROOT / "playlist_4k.m3u").write_text("\n".join(m3u_4k), encoding="utf-8")
    (REPO_ROOT / "playlist_desi.m3u").write_text("\n".join(m3u_desi), encoding="utf-8")

    print(f"  playlist.m3u: {len(m3u_all)//2} items")
    print(f"  playlist_4k.m3u: {len(m3u_4k)//2} items (pure 4K)")
    print(f"  playlist_desi.m3u: {len(clean_desi)} items (authentic Desi Solo)")
    print("\n✅ MASTER SUITE BUILD COMPLETE!")

if __name__ == "__main__":
    main()

"""
Master Suite Rebuilder for Stremio:
- Strict Anti-Spreading Purge across ALL catalogs (Zero spreading, gaping, wide-open, or spread-cheeks)
- xfree: Solo Nude Shower, Phat Booty & Twerk (Zero BubbleButt), Real Solo Striptease, Amateur Phonecam (Zero Masturbation, Zero Dudes, Zero Toys)
- fsiblogxx: Curated Direct MP4 Leaks with Anti-Spreading Purge
- Pakistani HD: 400+ Authenticated Pakistani MMS & Video Call Leaks (from FSIBlogXX & Mastiraja)
- Mastiraja: Curated Desi Creators & Solo Nude
- Pimpbunny Special: HaleyQuinnLA Twerks In Her Bathroom (720p HD Hosted Permanently)
"""

import json
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent
VIDI_ALL = REPO_ROOT / "vidi_all.json"
FSI_XX = REPO_ROOT / "fsiblogxx_all.json"
MASTIRAJA_ALL = REPO_ROOT / "mastiraja_all.json"
PAKI_ALL = REPO_ROOT / "pakistani_all.json"

PAGE_SIZE = 100

# 1. STRICT UNIVERSAL NEGATIVE FILTER (Applied to ALL catalogs)
BLOCK_EVERYTHING = re.compile(r"""(?i)\b(
    dude|dudes|guy|guys|man|men|male|males|boy|boys|boyfriend|boyfriends|bf|husband|husbands|lover|lovers|uncle|boss|driver|handyman|
    devar|jeth|jija|brother|stepbro|stepbrother|stepdad|father|son|doctor|plumber|stranger|cousin|tau\s*ji|chacha|mama|sardar|
    partner|partners|neighbor|neighbors|client|clients|customer|customers|pimp|teacher|sir|servant|guard|watchman|escort|fwb|
    daddy|daddies|sugar\s*daddy|baby\s*daddy|
    he|him|his|cock|cocks|dick|dicks|penis|shaft|balls|bwc|bbc|lund|loda|chochi|
    danny\s*d|johnny\s*sins|jordi|keiran\s*lee|manuel\s*ferrara|jmac|
    sex|creampie|creampies|deepthroat|throat|facial|facials|bj|blowjob|blowjobs|handjob|handjobs|
    suck\w*|swallow\w*|cum\s*in|cum\s*on|cumshot\w*|
    doggy|doggystyle|missionary|cowgirl|penetrat\w*|thrust\w*|pounded|pounding|pound|drilling|drilled|drill|
    breeding|bred|breed|piped|piping|pipe|railed|railing|rail|fucking|fucked|fuck|fucks|chudai|
    couple|couples|amateurcouple|realcouple|duo|interracial|honeymoon|quickie|suhagraat|
    split\w*|deflower\w*|virgin|dard|pain\w*|screaming|cry\w*|destroy\w*|destruction|
    ride|rides|riding|rode|getting\s*cum|
    teen|teens|underage|schoolgirl|minor|
    pregnant|pregnancy|baby\s*bump|expecting|maternity|
    ebony|black\s*girl|black\s*woman|dark\s*skin|
    granny|mature|gilf|grandma|old\s*woman|elderly|wrinkled|senior|aged\s*woman|
    anime|hentai|3d|cartoon|animation|animated|sfm|blender|cosplay|manga|
    flat|flat\s*chest|flat\s*ass|skinny|very\s*thin|bony|petite|tiny|small\s*tits|small\s*boobs|
    gape|gaping|prolapse|goatse|fist|fisting|extreme\s*anal|speculum|spread\w*|spred\w*|wide\s*open|open\s*wide|cheek\s*spread\w*|leg\s*spread\w*|
    group|orgy|gangbang|threesome|foursome|swinger|party|
    rough|hardcore|slap\w*|choke\w*|bdsm|torture|bondage|tied|abuse|punish\w*|slave|submissive|submission|master|mistress|dominat\w*|owned|
    toy|toys|dildo|dildos|vibrator|vibrators|sybian|machine|magic\s*wand|wand|strap|strapon|plug|anal\s*plug|butt\s*plug|
    carrot|cucumber|banana|vegetable|belan|bottle|brush|
    bubblebutt|masturbation|
    lena\s*the\s*plug|violet\s*myers|riley\s*reid|lana\s*rhoades|mia\s*malkova|eva\s*elfie|angela\s*white|abella\s*danger|kendra\s*lust|brandi\s*love|cory\s*chase|alexis\s*texas|emily\s*emika|autumn\s*falls|gabbie\s*carter|leah\s*gotti|abigaiil\s*morris|sweetie\s*fox|
    pee|piss|pissing|scat|toilet|watersport
)\b|takes?\s*(a|his|big|cock|dick|screaming)|used\s*by|fucked\s*by|choking\s*down|splits?\s*her|getting\s*fingered|holes?\s*filled|stretched\s*by|legs\s*on|spreads?\s*(her|them|legs|cheeks|pussy|ass)""", re.VERBOSE)

DISALLOWED_TAGS = {
    'Dildo', 'GiantDildo', 'HugeAnalDildo', 'Vibrator', 'Sybian', 'SexToys', 'Toy', 'Toys', 'AnalPlug', 'ButtPlug',
    'BubbleButt', 'Masturbation',
    'Pregnant', 'PregnantSolo', 'PregnantTits', 'Granny', 'Mature', 'GILF', 'Old', 'Skinny', 'Petite', 'SmallTits', 'Tiny',
    'Hentai', 'Anime', '3D', 'Cosplay', 'Ebony', 'Black', 'Threesome', 'Foursome', 'Group', 'Orgy', 'Couples', 'AmateurCouple', 'RealCouple', 'BDSM', 'Rough', 'Bondage',
    'SpreadPussy', 'SpreadAss', 'AnalGape', 'Gape', 'FingerSpread', 'Spread', 'Stretching', 'AssSpread', 'SpreadingPussy', 'SpreadLegs'
}

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
    print("=== Step 1: Processing xfree Solo (Zero Spreading, Zero BubbleButt, Zero Masturbation) ===")
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
    print(f"  Total Clean xfree items: {len(clean_vidi)}")

    catalog_results = {}
    assigned_vidi = set()

    # 1. Phat Booty & Twerk Flaunt (NO BubbleButt) + Pimpbunny Special
    thick_items = []
    
    # Add HaleyQuinnLA Twerks In Her Bathroom at the very top of Thick Booty
    haley_item = {
        "id": "pb_haleyquinnla_bathroom_twerk",
        "name": "HaleyQuinnLA Twerks In Her Bathroom",
        "poster": "https://pimpbunny.com/contents/videos_screenshots/524000/524982/preview_720p.mp4.jpg",
        "thumbnail": "https://pimpbunny.com/contents/videos_screenshots/524000/524982/preview_720p.mp4.jpg",
        "stream_url": "https://savad213.github.io/vidi-4k/media/haleyquinnla_bathroom_twerk.mp4",
        "quality": "720p HD",
        "runtime": "0:33",
        "tags": ["Twerking", "BigAss", "PhatBooty", "Bathroom", "Solo"]
    }
    thick_items.append(haley_item)
    assigned_vidi.add(haley_item["id"])

    thick_tags = {"BigAss", "Twerking", "Ass", "ThickBooty", "BigButt", "Booty", "Thick"}
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        tags = set(it.get("tags", []))
        if tags.intersection(thick_tags):
            thick_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_thick_booty"] = {
        "name": "Phat Booty & Twerk Flaunt (1080p+)",
        "metas": [to_meta(i) for i in thick_items],
        "raw_items": thick_items,
    }
    print(f"  Phat Booty & Twerk Flaunt: {len(thick_items)} items (incl. HaleyQuinnLA)")

    # 2. Solo Nude Shower & Wet Bath
    shower_items = []
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        tags = set(it.get("tags", []))
        if tags.intersection({"Shower", "Bath", "Soapy"}):
            shower_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_shower_wet"] = {
        "name": "Solo Nude Shower & Wet Bath (1080p+)",
        "metas": [to_meta(i) for i in shower_items],
        "raw_items": shower_items,
    }
    print(f"  Solo Nude Shower & Wet Bath: {len(shower_items)} items")

    # 3. Real Solo Striptease
    strip_items = []
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        tags = set(it.get("tags", []))
        if tags.intersection({"Striptease", "Teasing", "Lingerie"}):
            strip_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_solo_strip"] = {
        "name": "Real Solo Striptease (1080p+)",
        "metas": [to_meta(i) for i in strip_items],
        "raw_items": strip_items,
    }
    print(f"  Real Solo Striptease: {len(strip_items)} items")

    # 4. Amateur Phonecam & Mirror Selfies
    selfie_items = []
    phone_kws = re.compile(r"(?i)\b(selfie|mirror|phone|snap|snapchat|bedroom|baddie|amateur|hotel|tiktok)\b")
    for it in clean_vidi:
        if it["id"] in assigned_vidi:
            continue
        tags = set(it.get("tags", []))
        txt = it["name"] + " " + " ".join(tags)
        if tags.intersection({"Selfie", "NakedSelfie", "Mirror"}) or phone_kws.search(txt):
            selfie_items.append(it)
            assigned_vidi.add(it["id"])
    catalog_results["xfhq_phone_selfie"] = {
        "name": "Amateur Phonecam & Mirror Selfies (1080p+)",
        "metas": [to_meta(i) for i in selfie_items],
        "raw_items": selfie_items,
    }
    print(f"  Amateur Phonecam & Mirror Selfies: {len(selfie_items)} items")

    print("\n=== Step 2: Processing fsiblogxx.com (Applying Strict Anti-Spreading Purge) ===")
    fsixx_raw = json.loads(FSI_XX.read_text(encoding="utf-8"))["items"]
    fsixx_clean = []
    seen_fsi = set()
    for it in fsixx_raw:
        txt = it.get("name", "") + " " + " ".join(it.get("tags", []))
        if BLOCK_EVERYTHING.search(txt):
            continue
        st = it.get("stream_url")
        if st and st not in seen_fsi:
            seen_fsi.add(st)
            fsixx_clean.append(it)
    print(f"  Loaded {len(fsixx_clean)} clean direct MP4 videos from fsiblogxx.com (filtered from {len(fsixx_raw)})")
    catalog_results["xfhq_fsixx_mms"] = {
        "name": "Desi Leaked MMS (FSIBlogXX Direct)",
        "metas": [to_meta(i) for i in fsixx_clean],
        "raw_items": fsixx_clean,
    }

    print("\n=== Step 3: Processing Pakistani HD & Desi Creators ===")
    paki_raw = json.loads(PAKI_ALL.read_text(encoding="utf-8"))["items"] if PAKI_ALL.exists() else []
    masti_pool = json.loads(MASTIRAJA_ALL.read_text(encoding="utf-8"))["items"]
    
    paki_items = []
    desi_creator_items = []
    seen_paki_streams = set()
    paki_pat = re.compile(r"(?i)\b(pakistan|pakistani|lahore|karachi|islamabad|rawalpindi|peshawar|punjabi|pathan|minahil|alina|imsha|alisha|ayesha)\b")
    
    # 1. Harvested Pakistani Collection
    for it in paki_raw:
        txt = it.get("name", "") + " " + " ".join(it.get("tags", []))
        if BLOCK_EVERYTHING.search(txt):
            continue
        st = it.get("stream_url")
        if st and st not in seen_paki_streams:
            seen_paki_streams.add(st)
            paki_items.append(it)

    # 2. Mastiraja Pool
    for it in masti_pool:
        txt = it.get("name", "") + " " + " ".join(it.get("tags", []))
        if BLOCK_EVERYTHING.search(txt):
            continue
        st = it.get("stream_url")
        if paki_pat.search(txt):
            if st and st not in seen_paki_streams:
                seen_paki_streams.add(st)
                paki_items.append(it)
        else:
            desi_creator_items.append(it)

    catalog_results["xfhq_desi_pakistan"] = {
        "name": "Pakistani Solo & Cam Leaks (HD)",
        "metas": [to_meta(i) for i in paki_items],
        "raw_items": paki_items,
    }
    catalog_results["xfhq_desi_creators"] = {
        "name": "Desi Creators & Nude Solo (Mastiraja)",
        "metas": [to_meta(i) for i in desi_creator_items],
        "raw_items": desi_creator_items,
    }
    print(f"  Pakistani Solo & Cam Leaks (HD): {len(paki_items)} items")
    print(f"  Desi Creators & Nude Solo: {len(desi_creator_items)} items")

    print("\n=== Step 4: Writing Static Stream & Meta JSONs for All Desi & PB Items ===")
    meta_dir = REPO_ROOT / "meta" / "movie"
    stream_dir = REPO_ROOT / "stream" / "movie"
    meta_dir.mkdir(parents=True, exist_ok=True)
    stream_dir.mkdir(parents=True, exist_ok=True)

    # 4A: Haley Quinn meta & stream
    m_file = meta_dir / f"{haley_item['id']}.json"
    s_file = stream_dir / f"{haley_item['id']}.json"
    m_file.write_text(json.dumps({"meta": to_meta(haley_item)}, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    s_file.write_text(json.dumps({"streams": [{"url": haley_item["stream_url"], "name": "Permanent 720p HD", "title": "HaleyQuinnLA Twerks In Her Bathroom [720p HD]", "behaviorHints": {"notWebReady": False}}]}, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    all_desi_items = fsixx_clean + paki_items + desi_creator_items
    for it in all_desi_items:
        vid_id = it["id"]
        is_fsixx = "fsixx_" in vid_id or it.get("source") == "FSIBlogXX" or "cdn.fsiblogxx.com" in it.get("stream_url", "")
        referer = "https://www.fsiblogxx.com/" if is_fsixx else "https://mastiraja.tv/"
        source_name = "FSIBlogXX Direct CDN" if is_fsixx else "Mastiraja 3.1 Mbps"

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
                "description": f"Direct {source_name} · High Bitrate Desi MMS · {', '.join(it.get('tags', [])[:5])}",
                "genres": it.get("tags", ["Indian", "Desi", "MMS"]),
                "releaseInfo": "480p+",
                "runtime": "MMS"
            }
        }
        m_file.write_text(json.dumps(meta_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

        # stream file with appropriate proxyHeaders
        s_file = stream_dir / f"{vid_id}.json"
        stream_entry = {
            "url": it["stream_url"],
            "name": source_name,
            "title": f"{it['name']} [{source_name}]",
            "behaviorHints": {
                "notWebReady": False,
                "proxyHeaders": {
                    "request": {
                        "Referer": referer,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                }
            }
        }
        stream_obj = {"streams": [stream_entry]}
        s_file.write_text(json.dumps(stream_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    print(f"  Wrote {len(all_desi_items) + 1} meta & stream JSON files.")

    print("\n=== Step 5: Refreshing Catalog Directories ===")
    cat_movie_dir = REPO_ROOT / "catalog" / "movie"
    if cat_movie_dir.exists():
        for item in cat_movie_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            elif item.suffix == ".json":
                item.unlink()

    ALL_CATALOG_ORDER = [
        # Global Creator Suite
        ("xfhq_thick_booty", "Phat Booty & Twerk Flaunt (1080p+)"),
        ("xfhq_shower_wet", "Solo Nude Shower & Wet Bath (1080p+)"),
        ("xfhq_solo_strip", "Real Solo Striptease (1080p+)"),
        ("xfhq_phone_selfie", "Amateur Phonecam & Mirror Selfies (1080p+)"),
        # Desi Authentic Suite
        ("xfhq_fsixx_mms", "Desi Leaked MMS (FSIBlogXX Direct)"),
        ("xfhq_desi_creators", "Desi Creators & Nude Solo (Mastiraja)"),
        ("xfhq_desi_pakistan", "Pakistani Solo & Cam Leaks (HD)"),
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

    print("\n=== Step 6: Updating manifest.json ===")
    total_all_videos = sum(len(catalog_results[c[0]]["metas"]) for c in ALL_CATALOG_ORDER)
    manifest = {
        "id": "com.savaa.stremio.solo",
        "version": "4.261026.1625",
        "name": "Natural Solo & Desi MMS Suite",
        "description": (
            f"Curated Stremio Master Suite: {total_all_videos} videos across 7 categories. "
            f"1080p+/4K Natural Solo & Authentic FSIBlogXX / Mastiraja Leaks. "
            f"Direct high-bitrate streaming."
        ),
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["xfhq", "fsixx_", "masti_", "pb_", "paki_"],
        "catalogs": catalogs_manifest,
        "behaviorHints": {"adult": True, "configurable": False},
    }
    (REPO_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== Step 7: Generating M3U Playlists ===")
    m3u_all = ["#EXTM3U", "#PLAYLIST:Stremio Curated Natural Solo"]
    m3u_4k = ["#EXTM3U", "#PLAYLIST:Stremio 4K Natural Solo"]
    m3u_desi = ["#EXTM3U", "#PLAYLIST:Desi Leaked MMS Suite (FSIBlogXX & Mastiraja)"]

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

    for cid in ["xfhq_fsixx_mms", "xfhq_desi_creators", "xfhq_desi_pakistan"]:
        cname = catalog_results[cid]["name"].split(" (")[0]
        for it in catalog_results[cid]["raw_items"]:
            dur = 120
            iid = it.get("id", "")
            title = it.get("name", "").replace('"', '').replace(',', ' ')
            logo = it.get("poster") or it.get("thumbnail") or ""
            stream = it.get("stream_url")
            is_fsixx = "fsixx_" in iid or it.get("source") == "FSIBlogXX" or "cdn.fsiblogxx.com" in it.get("stream_url", "")
            ref = "https://www.fsiblogxx.com/" if is_fsixx else "https://mastiraja.tv/"
            line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [Desi MMS]'
            m3u_desi.append(line_inf)
            m3u_desi.append(f"#EXTVLCOPT:http-referrer={ref}")
            m3u_desi.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            m3u_desi.append(stream)

    (REPO_ROOT / "playlist.m3u").write_text("\n".join(m3u_all), encoding="utf-8")
    (REPO_ROOT / "playlist_4k.m3u").write_text("\n".join(m3u_4k), encoding="utf-8")
    (REPO_ROOT / "playlist_desi.m3u").write_text("\n".join(m3u_desi), encoding="utf-8")

    print(f"  playlist.m3u: {len(m3u_all)//2} items")
    print(f"  playlist_4k.m3u: {len(m3u_4k)//2} items (pure 4K)")
    print(f"  playlist_desi.m3u: {len(all_desi_items)} items (Desi MMS)")
    print(f"\n✅ Total Master Suite videos: {total_all_videos}")
    print("✅ BUILD COMPLETE!")

if __name__ == "__main__":
    main()

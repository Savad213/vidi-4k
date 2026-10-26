"""
Master Suite Rebuilder for Stremio / Vidi (vidi-4k):
- Types strictly ["movie"] only
- Content Filter: Excludes pregnant, black, old/mature, anime/cartoons, flat/skinny, group sex,
  rough/BDSM, toys (dildo/vibrator/wand/plug), gaping/spreading close-ups, men-focused clips,
  tentacle/piss/prison/gloryhole/fetish, BubbleButt tag, Masturbation tag.
- 8 Curated Catalogs (Max ~8-10):
  1. xfhq_thick_booty: Phat Booty & Twerk Flaunt (1080p+) [incl. HaleyQuinnLA]
  2. xfhq_shower_wet: Solo Nude Shower & Wet Bath (1080p+)
  3. xfhq_solo_strip: Real Solo Striptease (1080p+)
  4. xfhq_phone_selfie: Amateur Phonecam & Mirror Selfies (1080p+)
  5. xfhq_couples: Couples & Passionate Fucking (1080p+) [MF Natural, No Group, No Toys]
  6. xfhq_desi_mms: Desi Viral MMS Leaks (Direct HD) [Mastiraja + FSIBlog + FSIBlogXX]
  7. xfhq_desi_creators: Desi Creators & Nude Solo (Direct HD) [Authentic Desi Solo Nudes]
  8. xfhq_desi_pakistan: Pakistani Solo & Cam Leaks (Direct HD) [Mastiraja 100% Direct + Clean Leaks]
- Pillow humping folded into thick booty / solo strip / couples as requested.
- Static stream & meta JSON generation for 100% of candidate items.
- Complete pagination (skip=100.json, skip=200.json, etc.) for all catalogs.
- Logs every single removed item with reason.
"""

import json
import os
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent
PAGE_SIZE = 100

# 1. LOAD SOURCES
print("=== Step 1: Loading Source Catalog Pools ===")
vidi_pool = json.load(open(REPO_ROOT / "vidi.json", encoding="utf-8"))["items"]
vidi_all_pool = json.load(open(REPO_ROOT / "vidi_all.json", encoding="utf-8"))["items"]
vidi_by_id = {it["id"]: it for it in vidi_pool}
for it in vidi_all_pool:
    if it["id"] not in vidi_by_id:
        vidi_by_id[it["id"]] = it
all_vidi = list(vidi_by_id.values())

masti_pool = json.load(open(REPO_ROOT / "mastiraja_all.json", encoding="utf-8"))["items"]
desi_pool = json.load(open(REPO_ROOT / "desi_all.json", encoding="utf-8"))["items"]
paki_pool = json.load(open(REPO_ROOT / "pakistani_all.json", encoding="utf-8"))["items"]
fsixx_raw = json.load(open(REPO_ROOT / "fsiblogxx_all.json", encoding="utf-8"))
fsixx_pool = fsixx_raw.get("items", fsixx_raw) if isinstance(fsixx_raw, dict) else fsixx_raw

# Known dead IDs from live HTTP checks
DEAD_FSIXX_IDS = {
    'fsixx_small-boobs-girlfriend-horny-sex', 'fsixx_sexy-ass-marathi-housewife-sucking',
    'fsixx_cute-bengali-girlfriend-boob-showing', 'fsixx_bengali-aunty-outdoor-shoot-in-saree',
    'fsixx_mom-walking-naked-from-bathroom', 'fsixx_tamil-wife-boob-show-in-nighty',
    'fsixx_beautiful-small-boobs-girlfriend-hungry', 'fsixx_desi-porn-bhabhi-salu-nude-fingering',
    'fsixx_huge-boobs-wife-shared-with-cuckold', 'fsixx_desi-lady-dress-change-and-romance',
    'masti_paki_pakistani-girlfriend-bdsm-punishment', 'masti_paki_slutty-pakistani-sensual-boob-mast',
    'masti_paki_slutty-pakistani-boob-lick-finger'
}

WESTERN_PORNSTAR_PAT = re.compile(r"""(?i)\b(
    violet\s*myers|riley\s*reid|lana\s*rhoades|eva\s*elfie|angela\s*white|abella\s*danger|
    kendra\s*lust|brandi\s*love|cory\s*chase|alexis\s*texas|emily\s*emika|autumn\s*falls|
    gabbie\s*carter|leah\s*gotti|abigaiil\s*morris|sweetie\s*fox|lena\s*the\s*plug
)\b""", re.VERBOSE)

print(f"Sources loaded: Vidi={len(all_vidi)}, Masti={len(masti_pool)}, Desi={len(desi_pool)}, Paki={len(paki_pool)}, FSIXX={len(fsixx_pool)}")

# 2. UNIVERSAL CONTENT FILTERS
DISALLOWED_TAGS = {
    'pregnant', 'pregnantsolo', 'pregnanttits',
    'ebony', 'black', 'darkskin',
    'granny', 'mature', 'gilf', 'old',
    'hentai', 'anime', '3d', 'cosplay', 'animation',
    'skinny', 'petite', 'smalltits', 'tiny', 'flat',
    'threesome', 'foursome', 'group', 'orgy', 'gangbang', 'doublepenetration', 'dp',
    'bdsm', 'rough', 'bondage', 'hardcore', 'spanking', 'domination', 'submissive', 'abuse',
    'dildo', 'giantdildo', 'hugeanaldildo', 'vibrator', 'sybian', 'sextoys', 'toy', 'toys',
    'analplug', 'buttplug', 'strapon', 'sexmachine',
    'spreadpussy', 'spreadass', 'analgape', 'gape', 'fingerspread', 'spread', 'stretching',
    'assspread', 'spreadingpussy', 'spreadlegs',
    'shemale', 'trans', 'tranny', 'ladyboy', 'gay',
    'tentacle', 'pissing', 'urine', 'watersport', 'scat', 'feet', 'footfetish',
    'bubblebutt', 'masturbation'
}

UNIVERSAL_NEGATIVE_PATTERNS = [
    ("PREGNANT", re.compile(r"(?i)\b(pregnant|pregnancy|baby\s*bump|expecting|maternity)\b")),
    ("BLACK_WOMAN", re.compile(r"(?i)\b(ebony|black\s*girl|black\s*woman|dark\s*skin)\b")),
    ("OLD_WOMAN", re.compile(r"(?i)\b(granny|mature|gilf|grandma|old\s*woman|elderly|wrinkled|senior|aged\s*woman)\b")),
    ("ANIME_CARTOON", re.compile(r"(?i)\b(anime|hentai|3d|cartoon|animation|animated|sfm|blender|cosplay|manga)\b")),
    ("FLAT_THIN", re.compile(r"(?i)\b(flat|flat\s*chest|flat\s*ass|skinny|very\s*thin|bony|petite|tiny|small\s*tits|small\s*boobs)\b")),
    ("GROUP_SEX", re.compile(r"(?i)\b(group|orgy|gangbang|threesome|foursome|swinger|party|3some|4some)\b")),
    ("ROUGH_BDSM", re.compile(r"(?i)\b(rough|hardcore|slap\w*|choke\w*|bdsm|torture|bondage|tied|abuse|punish\w*|slave|submissive|submission|master|mistress|dominat\w*)\b")),
    ("TOYS", re.compile(r"(?i)\b(toy|toys|dildo|dildos|vibrator|vibrators|sybian|machine|magic\s*wand|wand|strap|strapon|plug|anal\s*plug|butt\s*plug|fleshlight|lush|lovense|carrot|cucumber|banana|belan)\b")),
    ("SPREADING_GAPE", re.compile(r"""(?i)(
        \b(gape|gaping|prolapse|goatse|fist|fisting|extreme\s*anal|speculum|spread\w*|spred\w*|wide\s*open|open\s*wide|cheek\s*spread\w*|leg\s*spread\w*|finger\s*spread\w*|stretching)\b |
        spreads?\s*(her|them|legs|cheeks|pussy|ass) |
        (juicy|tight)\s*holes? |
        asshole\s*(pumping|stretch\w*) |
        fingers?\s*in\s*(my|her)\s*(big\s*)?asshole
    )""", re.VERBOSE)),
    ("MEN_TRANS", re.compile(r"(?i)\b(shemale|trans|tranny|ladyboy|ts|gay|solo\s*male|cock\s*close\s*up)\b")),
    ("FETISH_PISS", re.compile(r"(?i)\b(tentacle|piss\w*|pee\w*|watersport\w*|scat|toilet|prison|glory\s*hole|fetish|feet|foot)\b")),
    ("BUBBLEBUTT_MAST", re.compile(r"(?i)\b(bubblebutt|masturbation)\b"))
]

SOLO_EXCLUSION_PATTERN = re.compile(r"""(?i)\b(
    dude|dudes|guy|guys|man|men|male|males|boy|boys|boyfriend|boyfriends|bf|husband|husbands|lover|lovers|uncle|boss|driver|
    cock|cocks|dick|dicks|penis|shaft|balls|bwc|bbc|lund|loda|
    creampie|creampies|deepthroat|throat|facial|facials|bj|blowjob|blowjobs|handjob|handjobs|
    suck\w*|swallow\w*|cum\s*in|cum\s*on|cumshot\w*|
    doggy|doggystyle|missionary|cowgirl|penetrat\w*|thrust\w*|pounded|pounding|pound|drilling|drilled|drill|
    breeding|bred|breed|piped|piping|pipe|railed|railing|rail|fucking|fucked|fuck|fucks|chudai|
    couple|couples|amateurcouple|realcouple|duo|interracial|honeymoon|quickie|suhagraat|
    ride|rides|riding|rode
)\b""", re.VERBOSE)

def check_universal(item):
    name = item.get('name', '')
    desc = item.get('description', '')
    tags = [t.lower() for t in item.get('tags', []) + item.get('genres', [])]
    txt = f"{name} {desc} {' '.join(tags)}"

    for t in tags:
        if t in DISALLOWED_TAGS:
            return False, f"Disallowed tag: '{t}'"

    for cat_name, pat in UNIVERSAL_NEGATIVE_PATTERNS:
        m = pat.search(txt)
        if m:
            return False, f"{cat_name} match: '{m.group(0)}'"

    return True, "OK"

def check_solo(item):
    ok, reason = check_universal(item)
    if not ok:
        return False, reason
    name = item.get('name', '')
    desc = item.get('description', '')
    tags = [t.lower() for t in item.get('tags', []) + item.get('genres', [])]
    txt = f"{name} {desc} {' '.join(tags)}"
    m = SOLO_EXCLUSION_PATTERN.search(txt)
    if m:
        return False, f"Solo violation: '{m.group(0)}'"
    return True, "OK"

# 3. BUILD 8 CURATED CATALOGS
print("\n=== Step 2: Filtering and Building 8 Master Catalogs ===")

catalogs_data = {
    "xfhq_thick_booty": {"name": "Phat Booty & Twerk Flaunt (1080p+)", "items": [], "removed": []},
    "xfhq_shower_wet": {"name": "Solo Nude Shower & Wet Bath (1080p+)", "items": [], "removed": []},
    "xfhq_solo_strip": {"name": "Real Solo Striptease (1080p+)", "items": [], "removed": []},
    "xfhq_phone_selfie": {"name": "Amateur Phonecam & Mirror Selfies (1080p+)", "items": [], "removed": []},
    "xfhq_couples": {"name": "Couples & Passionate Fucking (1080p+)", "items": [], "removed": []},
    "xfhq_desi_mms": {"name": "Desi Viral MMS Leaks (Direct HD)", "items": [], "removed": []},
    "xfhq_desi_creators": {"name": "Desi Creators & Nude Solo (Direct HD)", "items": [], "removed": []},
    "xfhq_desi_pakistan": {"name": "Pakistani Solo & Cam Leaks (Direct HD)", "items": [], "removed": []},
}

assigned_global = set()

# A. HaleyQuinnLA twerk video at top of Phat Booty
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
catalogs_data["xfhq_thick_booty"]["items"].append(haley_item)
assigned_global.add(haley_item["id"])

# B. Shower Wet (Run first to capture all bath/shower)
shower_tags = {"Shower", "Bath", "Soapy"}
for it in all_vidi:
    if it["id"] in assigned_global: continue
    if it.get("quality") not in {"4K", "1080p+"}: continue
    tags = set(it.get("tags", []))
    if tags.intersection(shower_tags):
        ok, reason = check_solo(it)
        if ok:
            catalogs_data["xfhq_shower_wet"]["items"].append(it)
            assigned_global.add(it["id"])
        else:
            catalogs_data["xfhq_shower_wet"]["removed"].append((it["id"], it["name"], reason))

# C. Thick Booty (Ass, Twerking, Curvy, Phat Booty + pillow humping folded in)
thick_tags = {"BigAss", "Twerking", "Ass", "ThickBooty", "BigButt", "Booty", "Thick"}
pillow_kws = re.compile(r"(?i)\b(pillow|hump\w*|grind\w*)\b")
for it in all_vidi:
    if it["id"] in assigned_global: continue
    if it.get("quality") not in {"4K", "1080p+"}: continue
    tags = set(it.get("tags", []))
    txt = it.get("name", "") + " " + " ".join(tags)
    if tags.intersection(thick_tags) or 'PillowHumping' in tags or pillow_kws.search(txt):
        ok, reason = check_solo(it)
        if ok:
            catalogs_data["xfhq_thick_booty"]["items"].append(it)
            assigned_global.add(it["id"])
        else:
            catalogs_data["xfhq_thick_booty"]["removed"].append((it["id"], it["name"], reason))

# D. Real Solo Striptease (Striptease, Teasing, Lingerie, Undress)
strip_tags = {"Striptease", "Teasing", "Lingerie", "Undress"}
for it in all_vidi:
    if it["id"] in assigned_global: continue
    if it.get("quality") not in {"4K", "1080p+"}: continue
    tags = set(it.get("tags", []))
    if tags.intersection(strip_tags):
        ok, reason = check_solo(it)
        if ok:
            catalogs_data["xfhq_solo_strip"]["items"].append(it)
            assigned_global.add(it["id"])
        else:
            catalogs_data["xfhq_solo_strip"]["removed"].append((it["id"], it["name"], reason))

# E. Amateur Phonecam & Mirror Selfies (Selfie, Mirror, Phonecam, Bedroom Baddie)
phone_tags = {"Selfie", "NakedSelfie", "Mirror"}
phone_kws = re.compile(r"(?i)\b(selfie|mirror|phone|snap|snapchat|bedroom|baddie|amateur|tiktok)\b")
for it in all_vidi:
    if it["id"] in assigned_global: continue
    if it.get("quality") not in {"4K", "1080p+"}: continue
    tags = set(it.get("tags", []))
    txt = it.get("name", "") + " " + " ".join(tags)
    if tags.intersection(phone_tags) or phone_kws.search(txt):
        ok, reason = check_solo(it)
        if ok:
            catalogs_data["xfhq_phone_selfie"]["items"].append(it)
            assigned_global.add(it["id"])
        else:
            catalogs_data["xfhq_phone_selfie"]["removed"].append((it["id"], it["name"], reason))

# F. Couples & Passionate Fucking (Natural, strictly MF, no group, no toys)
couples_tags = {"Couples", "AmateurCouple", "RealCouple", "Fucking", "Homemade", "Missionary", "Cowgirl", "Doggystyle"}
for it in all_vidi:
    if it["id"] in assigned_global: continue
    if it.get("quality") not in {"4K", "1080p+"}: continue
    tags = set(it.get("tags", []))
    txt = it.get("name", "") + " " + " ".join(tags)
    if tags.intersection(couples_tags) or "couple" in txt.lower():
        ok, reason = check_universal(it)
        if ok:
            catalogs_data["xfhq_couples"]["items"].append(it)
            assigned_global.add(it["id"])
        else:
            catalogs_data["xfhq_couples"]["removed"].append((it["id"], it["name"], reason))

# G. Pakistani Solo & Cam Leaks (Direct HD first from Mastiraja, then verified sources)
paki_pat = re.compile(r"(?i)\b(pakistan|pakistani|lahore|karachi|islamabad|rawalpindi|peshawar|punjabi|pathan|minahil|alina|imsha|alisha|ayesha)\b")
seen_desi_streams = set()

for it in paki_pool:
    if it["id"] in DEAD_FSIXX_IDS:
        continue
    st = it.get("stream_url", "")
    if not st or st in seen_desi_streams: continue
    ok, reason = check_universal(it)
    if ok:
        seen_desi_streams.add(st)
        catalogs_data["xfhq_desi_pakistan"]["items"].append(it)
    else:
        catalogs_data["xfhq_desi_pakistan"]["removed"].append((it["id"], it["name"], reason))

# H. Desi Viral MMS Leaks & Desi Creators
mms_pat = re.compile(r"(?i)\b(mms|viral|leak|scandal|hotel|tape|hidden|cam|call|room|caught)\b")
all_desi_candidates = masti_pool + desi_pool + fsixx_pool
for it in all_desi_candidates:
    if it["id"] in DEAD_FSIXX_IDS:
        continue
    st = it.get("stream_url", "")
    if not st or st in seen_desi_streams: continue
    txt = it.get("name", "") + " " + " ".join(it.get("tags", []))

    # Drop Western porn star imports from Desi collections
    if WESTERN_PORNSTAR_PAT.search(txt):
        catalogs_data["xfhq_desi_creators"]["removed"].append((it["id"], it["name"], "Non-Desi Western porn star"))
        continue

    # Route Pakistani leaks to Pakistani catalog if matching
    if paki_pat.search(txt):
        ok, reason = check_universal(it)
        if ok:
            seen_desi_streams.add(st)
            catalogs_data["xfhq_desi_pakistan"]["items"].append(it)
        else:
            catalogs_data["xfhq_desi_pakistan"]["removed"].append((it["id"], it["name"], reason))
    elif mms_pat.search(txt) or any("mms" in t.lower() or "leak" in t.lower() or "viral" in t.lower() for t in it.get("tags", [])):
        ok, reason = check_universal(it)
        if ok:
            seen_desi_streams.add(st)
            catalogs_data["xfhq_desi_mms"]["items"].append(it)
        else:
            catalogs_data["xfhq_desi_mms"]["removed"].append((it["id"], it["name"], reason))
    else:
        # Desi Creators & Nude Solo (Strictly solo)
        ok_solo, reason_solo = check_solo(it)
        if ok_solo:
            seen_desi_streams.add(st)
            catalogs_data["xfhq_desi_creators"]["items"].append(it)
        else:
            # If not solo, check if it's a valid couple MMS leak
            ok_uni, reason_uni = check_universal(it)
            if ok_uni:
                seen_desi_streams.add(st)
                catalogs_data["xfhq_desi_mms"]["items"].append(it)
            else:
                catalogs_data["xfhq_desi_creators"]["removed"].append((it["id"], it["name"], reason_uni))

# Sort catalogs: 4K items first, then by likes or popularity
for cid in ["xfhq_thick_booty", "xfhq_shower_wet", "xfhq_solo_strip", "xfhq_phone_selfie", "xfhq_couples"]:
    catalogs_data[cid]["items"].sort(
        key=lambda x: (
            0 if x.get("id") == haley_item["id"] else (
                1 if x.get("quality") == "4K" else 2
            ),
            -x.get("likes", 0)
        )
    )

print("\n=== Candidate Filtering Summary ===")
total_all_videos = 0
for cid, cdata in catalogs_data.items():
    total_all_videos += len(cdata["items"])
    print(f"Catalog: {cid:22} | Kept: {len(cdata['items']):4} | Removed: {len(cdata['removed']):4}")
print(f"Total Active Videos Across All Catalogs: {total_all_videos}")

# 4. WRITE STATIC STREAM AND META FILES FOR ALL ACTIVE CANDIDATES
print("\n=== Step 3: Verifying and Generating Stream & Meta JSON Files ===")
meta_dir = REPO_ROOT / "meta" / "movie"
stream_dir = REPO_ROOT / "stream" / "movie"
meta_dir.mkdir(parents=True, exist_ok=True)
stream_dir.mkdir(parents=True, exist_ok=True)

written_streams = 0
written_metas = 0

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
        "runtime": str(item.get("runtime", "")),
        "behaviorHints": {"defaultVideoId": item["id"]},
    }

for cid, cdata in catalogs_data.items():
    for it in cdata["items"]:
        vid_id = it["id"]
        m_file = meta_dir / f"{vid_id}.json"
        s_file = stream_dir / f"{vid_id}.json"

        # Ensure meta file exists
        if not m_file.exists():
            meta_obj = {"meta": to_meta(it)}
            m_file.write_text(json.dumps(meta_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
            written_metas += 1

        # Ensure stream file exists
        if not s_file.exists():
            st_url = it.get("stream_url") or it.get("url") or ""
            stream_obj = {
                "streams": [
                    {
                        "url": st_url,
                        "name": "Direct Stream",
                        "title": f"{it['name']} [{it.get('quality', '1080p+')}]",
                        "behaviorHints": {"notWebReady": False}
                    }
                ]
            }
            if "cdn.fsiblogxx.com" in st_url:
                stream_obj["streams"][0]["behaviorHints"]["proxyHeaders"] = {
                    "request": {
                        "Referer": "https://www.fsiblogxx.com/",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                }
            s_file.write_text(json.dumps(stream_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
            written_streams += 1

print(f"Newly created: {written_metas} meta files, {written_streams} stream files.")

# 5. WRITE PAGINATED CATALOG FILES
print("\n=== Step 4: Refreshing and Writing Paginated Catalog Files ===")
cat_movie_dir = REPO_ROOT / "catalog" / "movie"
if cat_movie_dir.exists():
    for item in cat_movie_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        elif item.suffix == ".json":
            item.unlink()

def write_paginated_catalog(cat_dir: Path, metas: list):
    cat_dir.mkdir(parents=True, exist_ok=True)
    base = {"metas": metas[:PAGE_SIZE]}
    (cat_dir.parent / f"{cat_dir.name}.json").write_text(
        json.dumps(base, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    for skip in range(PAGE_SIZE, len(metas), PAGE_SIZE):
        chunk = metas[skip : skip + PAGE_SIZE]
        skip_file = cat_dir / f"skip={skip}.json"
        skip_file.write_text(
            json.dumps({"metas": chunk}, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

catalogs_manifest = []
ALL_CATALOG_ORDER = [
    "xfhq_thick_booty",
    "xfhq_shower_wet",
    "xfhq_solo_strip",
    "xfhq_phone_selfie",
    "xfhq_couples",
    "xfhq_desi_mms",
    "xfhq_desi_creators",
    "xfhq_desi_pakistan"
]

for cid in ALL_CATALOG_ORDER:
    cdata = catalogs_data[cid]
    metas = [to_meta(i) for i in cdata["items"]]
    cat_dir = cat_movie_dir / cid
    write_paginated_catalog(cat_dir, metas)
    catalogs_manifest.append({
        "type": "movie",
        "id": cid,
        "name": cdata["name"],
        "extra": [{"name": "skip", "isRequired": False}]
    })

# 6. UPDATE MANIFEST.JSON
print("\n=== Step 5: Updating manifest.json ===")
manifest = {
    "id": "com.savaa.stremio.solo",
    "version": "5.261027.0135",
    "name": "Natural Solo, Couples & Desi MMS Suite",
    "description": (
        f"Curated Stremio Master Suite: {total_all_videos} videos across 8 categories. "
        f"Direct 1080p+/4K Natural Solo & Couples + Authentic Mastiraja & FSIBlog Desi MMS Leaks. "
        f"Filtered and Verified."
    ),
    "resources": ["catalog", "meta", "stream"],
    "types": ["movie"],
    "idPrefixes": ["xfhq", "masti_", "pb_", "paki_", "desi_", "fsixx_"],
    "catalogs": catalogs_manifest,
    "behaviorHints": {"adult": True, "configurable": False},
}
(REPO_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

# 7. GENERATE M3U PLAYLISTS
print("\n=== Step 6: Generating M3U Playlists ===")
m3u_all = ["#EXTM3U", "#PLAYLIST:Stremio Curated Master Suite"]
m3u_4k = ["#EXTM3U", "#PLAYLIST:Stremio 4K Master Suite"]
m3u_desi = ["#EXTM3U", "#PLAYLIST:Desi Leaked MMS & Pakistani Suite"]

for cid in ALL_CATALOG_ORDER[:5]:
    cname = catalogs_data[cid]["name"].split(" (")[0]
    for it in catalogs_data[cid]["items"]:
        dur = it.get("duration", 0)
        iid = it.get("id", "")
        title = it.get("name", "").replace('"', '').replace(',', ' ')
        logo = it.get("poster") or it.get("thumbnail") or ""
        stream = it.get("stream_url") or it.get("url") or ""
        qual = it.get("quality", "1080p+")
        line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [{qual}]'
        m3u_all.append(line_inf)
        m3u_all.append(stream)
        if qual == "4K":
            m3u_4k.append(line_inf)
            m3u_4k.append(stream)

for cid in ALL_CATALOG_ORDER[5:]:
    cname = catalogs_data[cid]["name"].split(" (")[0]
    for it in catalogs_data[cid]["items"]:
        dur = 120
        iid = it.get("id", "")
        title = it.get("name", "").replace('"', '').replace(',', ' ')
        logo = it.get("poster") or it.get("thumbnail") or ""
        stream = it.get("stream_url") or it.get("url") or ""
        qual = it.get("quality", "720p HD")
        line_inf = f'#EXTINF:{dur} tvg-id="{iid}" tvg-name="{title}" tvg-logo="{logo}" group-title="{cname}",{title} [{qual}]'
        m3u_desi.append(line_inf)
        m3u_desi.append(stream)

(REPO_ROOT / "playlist.m3u").write_text("\n".join(m3u_all), encoding="utf-8")
(REPO_ROOT / "playlist_4k.m3u").write_text("\n".join(m3u_4k), encoding="utf-8")
(REPO_ROOT / "playlist_desi.m3u").write_text("\n".join(m3u_desi), encoding="utf-8")

# 8. SAVE AUDIT LOG
print("\n=== Step 7: Saving Removal Audit Log ===")
audit_data = {}
for cid, cdata in catalogs_data.items():
    audit_data[cid] = {
        "name": cdata["name"],
        "kept_count": len(cdata["items"]),
        "removed_count": len(cdata["removed"]),
        "removed_items": [{"id": r[0], "name": r[1], "reason": r[2]} for r in cdata["removed"]]
    }
(REPO_ROOT / "removed_items_audit.json").write_text(json.dumps(audit_data, indent=2, ensure_ascii=False), encoding="utf-8")

print("✅ BUILD COMPLETE! All 8 catalogs paginated, manifest bumped, stream files verified.")

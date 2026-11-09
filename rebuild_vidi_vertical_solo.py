"""
Vidi 4K Dedicated Rebuilder: 100% Vertical Solo, OnlyFans, Tease, Shower, Desi Phone MMS & Pakistani Leaks.
Completely eliminates all Western studio films, cinema, roleplay, and couples from Vidi 4K.
Exclusively indexes authentic leaked phone videos, WhatsApp/Snapchat video calls, hotel recordings, and creator-free real MMS.
"""

import json
import os
import re
import html
import shutil
import datetime
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parent
PAGE_SIZE = 100

# ─── 1. TARGET CATALOG DEFINITIONS ───────────────────────────────────────────
TARGET_CATALOGS = [
    {
        "type": "movie",
        "id": "xfhq_phone_selfie",
        "name": "Portrait: Phone & Mirror Selfies / OnlyFans",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "xfhq_solo_strip",
        "name": "Portrait: Solo Striptease & Tease",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "xfhq_shower_wet",
        "name": "Portrait: Shower & Wet Bath",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "xfhq_thick_booty",
        "name": "Portrait: Curvy & Twerk Flaunt",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "xfhq_desi_mms",
        "name": "Desi Phone MMS Leaks",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "xfhq_desi_pakistan",
        "name": "Pakistani Phone & Video Call Leaks",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "xfhq_search",
        "name": "Search Vidi 4K",
        "extra": [{"name": "search", "isRequired": True}]
    }
]

TARGET_CATALOG_IDS = [c["id"] for c in TARGET_CATALOGS if c["id"] != "xfhq_search"]

# ─── 2. CONTENT FILTERS & BOUNDARIES ─────────────────────────────────────────
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
    'tentacle', 'pissing', 'urine', 'watersport', 'scat', 'feet', 'footfetish'
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
    ("FETISH_PISS", re.compile(r"(?i)\b(tentacle|piss\w*|pee\w*|watersport\w*|scat|toilet|prison|glory\s*hole|fetish|feet|foot)\b"))
]

SOLO_EXCLUSION_PATTERN = re.compile(r"""(?i)\b(
    dude|dudes|guy|guys|man|men|male|males|boy|boys|boyfriend|boyfriends|bf|husband|husbands|lover|lovers|uncle|boss|driver|
    cock|cocks|dick|dicks|penis|shaft|balls|bwc|bbc|lund|loda|
    creampie|creampies|deepthroat|throat|facial|facials|bj|blowjob|blowjobs|handjob|handjobs|
    suck\w*|swallow\w*|cum\s*in|cum\s*on|cumshot\w*|
    doggy|doggystyle|missionary|cowgirl|penetrat\w*|thrust\w*|pounded|pounding|pound|drilling|drilled|drill|
    breeding|bred|breed|piped|piping|pipe|railed|railing|rail|fucking|fucked|fuck|fucks|chudai|
    couple|couples|amateurcouple|realcouple|duo|interracial|honeymoon|quickie|suhagraat|
    ride|rides|riding|rode|wifebucket
)\b""", re.VERBOSE)

WESTERN_PORNSTAR_PAT = re.compile(r"""(?i)\b(
    violet\s*myers|riley\s*reid|lana\s*rhoades|eva\s*elfie|angela\s*white|abella\s*danger|
    kendra\s*lust|brandi\s*love|cory\s*chase|alexis\s*texas|emily\s*emika|autumn\s*falls|
    gabbie\s*carter|leah\s*gotti|abigaiil\s*morris|sweetie\s*fox|lena\s*the\s*plug
)\b""", re.VERBOSE)

# Strict ban on creators, models, webseries, and studios in MMS / Pakistani leak rows
CREATOR_OR_STUDIO_BAN = re.compile(
    r"""(?i)\b(
        onlyfans|fansly|creator|creators|patreon|influencer|webcam|camgirl|model|models|
        webseries|ullu|kooku|cineprime|primeshots|rabbit|hotshots|besharams|voovi|hunters|moodx|fliz|
        episode|uncut\s*webseries|web\s*series|photoshoot|photo\s*shoot|casting|interview|
        backstage|behind\s*the\s*scenes|bts|official|trailer|movie|film|salomelons|ari\s*kytsya|
        kiarablay|nandana|nandana\s*krishnan|anamika\s*desai|subway\s*girl
    )\b""", re.VERBOSE
)

# Positive scoring for authentic leaked phone recordings
PHONE_LEAK_KEYWORDS = [
    (r"(?i)\b(video\s*call|videocall|call\s*leak|call\s*recording)\b", 60),
    (r"(?i)\b(phone\s*cam|phonecam|phone\s*leak|phone\s*recording|recorded\s*on\s*phone|cell\s*phone)\b", 50),
    (r"(?i)\b(mms\s*leak|leaked\s*mms|desi\s*mms|viral\s*mms|pakistani\s*mms)\b", 40),
    (r"(?i)\b(whatsapp|snapchat|snap|telegram|leaked\s*tape)\b", 35),
    (r"(?i)\b(hotel\s*room|hotel|hostel|oyo|guest\s*house)\b", 30),
    (r"(?i)\b(hidden\s*cam|spy\s*cam|hidden\s*camera|spycam|secret\s*camera|caught\s*on\s*cam)\b", 30),
    (r"(?i)\b(private\s*leak|secret\s*recording|personal\s*video|private\s*video|private\s*room)\b", 25),
    (r"(?i)\b(girlfriend|gf|bhabhi|wife|biwi|lover|devar|college\s*girl|school\s*girl)\b", 20),
    (r"(?i)\b(mirror\s*selfie|selfie\s*video|bedroom\s*recording|bathroom\s*leak)\b", 20),
]

def score_phone_leak(item):
    name = item.get("name", "")
    tags = " ".join(item.get("tags", []))
    txt = f"{name} {tags}"
    if CREATOR_OR_STUDIO_BAN.search(txt) or WESTERN_PORNSTAR_PAT.search(txt):
        return -1000
    score = 0
    for pat, pts in PHONE_LEAK_KEYWORDS:
        if re.search(pat, txt):
            score += pts
    return score

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

def to_meta(item):
    raw_name = html.unescape(item.get("name", "")).strip()
    # Strip site branding and artifact tags from titles
    clean_name = re.sub(r"\s*[-–|]\s*Masti\s*Raja\s*$", "", raw_name, flags=re.IGNORECASE)
    clean_name = re.sub(r"\s*\[High Bitrate Desi MMS\]\s*$", "", clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r"\s*\[480p\+\s*Desi MMS\]\s*$", "", clean_name, flags=re.IGNORECASE)
    clean_name = clean_name.strip()
    
    poster = item.get("poster") or item.get("thumbnail") or ""
    tags = item.get("tags") or item.get("genres") or []
    qual = item.get("quality", "1080p+")
    runtime = str(item.get("runtime", "HD"))
    return {
        "id": item["id"],
        "type": "movie",
        "name": clean_name,
        "poster": poster,
        "background": poster,
        "logo": item.get("logo") or poster,
        "description": f"{qual} · {runtime} · {', '.join(tags[:5])}",
        "genres": tags,
        "releaseInfo": qual,
        "runtime": runtime,
        "behaviorHints": {"defaultVideoId": item["id"]},
    }

def rank_key(it, special_id=None):
    if special_id and it.get("id") == special_id:
        return (-1, 0, 0, 0)
    qual = str(it.get("quality", "")).upper()
    res = str(it.get("resolution", "")).lower()
    ori = str(it.get("orientation", "")).lower()

    if "4K" in qual or "2160" in res:
        res_rank = 0
    elif "1080" in qual or "1080" in res:
        res_rank = 1
    elif "720" in qual or "720" in res:
        res_rank = 2
    else:
        res_rank = 3

    ori_rank = 0 if ori == "vertical" else 1

    year = 0
    for y in [2026, 2025, 2024, 2023, 2022, 2021]:
        if str(y) in str(it.get("releaseInfo", "")) or str(y) in it.get("name", ""):
            year = y
            break
    year_rank = -year

    try:
        likes = int(it.get("likes", 0))
    except Exception:
        likes = 0

    return (res_rank, ori_rank, year_rank, -likes)

def make_semver_timestamp():
    dt = datetime.datetime.now()
    date_part = dt.strftime("%y%m%d")
    patch_part = str(int(dt.strftime("%H%M")))
    ver = f"6.{date_part}.{patch_part}"
    assert not re.search(r"(^|\.)0\d", ver), f"Leading zero in version: {ver}"
    return ver

# ─── 3. EXECUTE REBUILD ──────────────────────────────────────────────────────
def rebuild():
    print("=" * 70)
    print("STARTING VIDI 4K CLEAN REBUILD (VERTICAL SOLO ONLY)")
    print("=" * 70)

    # A. PURGE NON-CONFORMING CATALOG FOLDERS & FILES
    cat_movie_dir = REPO_ROOT / "catalog" / "movie"
    allowed_dirs = set(TARGET_CATALOG_IDS + ["xfhq_search"])

    for entry in cat_movie_dir.iterdir():
        if entry.is_dir():
            if entry.name not in allowed_dirs:
                print(f"Purging unwanted catalog dir: {entry.name}")
                shutil.rmtree(entry)
        elif entry.is_file() and entry.suffix == ".json":
            stem = entry.stem
            if stem not in allowed_dirs:
                print(f"Purging unwanted catalog file: {entry.name}")
                entry.unlink()

    # B. LOAD EXISTING CLEAN ITEMS FROM TARGET CATALOGS
    print("\n--- Loading existing clean items ---")
    catalogs_items = defaultdict(list)
    assigned_ids = set()

    # Special Item: HaleyQuinnLA Twerk video at rank 0 of xfhq_thick_booty
    haley_item = {
        "id": "pb_haleyquinnla_bathroom_twerk",
        "name": "HaleyQuinnLA Twerks In Her Bathroom",
        "poster": "https://pimpbunny.com/contents/videos_screenshots/524000/524982/preview_720p.mp4.jpg",
        "thumbnail": "https://pimpbunny.com/contents/videos_screenshots/524000/524982/preview_720p.mp4.jpg",
        "stream_url": "https://savad213.github.io/vidi-4k/media/haleyquinnla_bathroom_twerk.mp4",
        "quality": "720p HD",
        "orientation": "vertical",
        "resolution": "404x720",
        "runtime": "0:33",
        "tags": ["Twerking", "BigAss", "PhatBooty", "Bathroom", "Solo"]
    }
    catalogs_items["xfhq_thick_booty"].append(haley_item)
    assigned_ids.add(haley_item["id"])

    for cid in TARGET_CATALOG_IDS:
        base_file = cat_movie_dir / f"{cid}.json"
        cat_items = []
        if base_file.exists():
            cat_items.extend(json.loads(base_file.read_text(encoding="utf-8")).get("metas", []))
        cat_dir = cat_movie_dir / cid
        if cat_dir.exists():
            for p in sorted(cat_dir.glob("skip=*.json"), key=lambda x: int(x.stem.split("=")[1])):
                cat_items.extend(json.loads(p.read_text(encoding="utf-8")).get("metas", []))

        is_solo_cat = cid in ["xfhq_thick_booty", "xfhq_shower_wet", "xfhq_solo_strip", "xfhq_phone_selfie"]
        is_mms_cat = cid in ["xfhq_desi_mms", "xfhq_desi_pakistan"]
        for it in cat_items:
            if it["id"] in assigned_ids:
                continue
            if is_solo_cat:
                ok, _ = check_solo(it)
            elif is_mms_cat:
                if score_phone_leak(it) <= 0:
                    continue
                ok, _ = check_universal(it)
            else:
                ok, _ = check_universal(it)
            if ok:
                assigned_ids.add(it["id"])
                catalogs_items[cid].append(it)

    for cid in TARGET_CATALOG_IDS:
        print(f"  {cid:22}: {len(catalogs_items[cid])} existing clean items")

    # C. LOAD SOURCE DATASETS
    print("\n--- Loading pool sources for expansion ---")
    tease = json.loads((REPO_ROOT / "vidi_tease.json").read_text(encoding="utf-8"))["items"]
    vidi_all_raw = json.loads((REPO_ROOT / "vidi_all.json").read_text(encoding="utf-8"))["items"]

    emmy_items = []
    emmy_path = REPO_ROOT / "emmyelfie_xfree_1080plus.json"
    if emmy_path.exists():
        emmy_raw = json.loads(emmy_path.read_text(encoding="utf-8"))
        for it in emmy_raw:
            if it.get("h", 0) >= it.get("w", 0) and it.get("video") and it.get("poster"):
                tags = [t.strip("#") for t in it.get("tags", "").split()]
                slug = it.get("slug", "").replace("-", " ").title()
                emmy_items.append({
                    "id": f"xfhq_emmy_{it['id']}",
                    "name": f"Emmy Elfie: {slug}",
                    "title": f"Emmy Elfie: {slug} [1080p Vertical]",
                    "tags": tags + ["Solo", "Emmy Elfie", "Vertical", "Tease"],
                    "poster": it.get("poster"),
                    "thumbnail": it.get("poster"),
                    "logo": it.get("poster"),
                    "stream_url": it.get("video"),
                    "url": it.get("video"),
                    "orientation": "vertical",
                    "quality": "1080p+",
                    "resolution": f"{it.get('w', 1080)}x{it.get('h', 1920)}",
                    "duration": it.get("duration", 30),
                    "runtime": f"0:{it.get('duration', 30):02d}",
                    "likes": 250
                })

    all_tease_pool = tease + vidi_all_raw + emmy_items
    paki = json.loads((REPO_ROOT / "pakistani_all.json").read_text(encoding="utf-8"))["items"]
    desi = json.loads((REPO_ROOT / "desi_all.json").read_text(encoding="utf-8"))["items"]
    masti = json.loads((REPO_ROOT / "mastiraja_all.json").read_text(encoding="utf-8"))["items"]
    harvested_path = REPO_ROOT / "harvested_creators.json"
    harvested = json.loads(harvested_path.read_text(encoding="utf-8")) if harvested_path.exists() else []

    # D. ROUTE NEW TEASE ITEMS INTO TARGET ROWS
    shower_tags = {"Shower", "Bath", "Soapy"}
    shower_kws = re.compile(r"(?i)\b(shower|bath|soapy|bathtub|showerhead)\b")

    thick_tags = {"BigAss", "Twerking", "Ass", "ThickBooty", "BigButt", "Booty", "Thick", "Curvy"}
    thick_kws = re.compile(r"(?i)\b(booty|twerk|thick|bubble\s*butt|curves|curvy|phat|big\s*ass)\b")

    strip_tags = {"Striptease", "Teasing", "Lingerie", "Undress", "Solo", "Dancing"}
    strip_kws = re.compile(r"(?i)\b(strip|striptease|tease|teasing|lingerie|undress|dance|dancing)\b")

    phone_tags = {"Selfie", "NakedSelfie", "Mirror", "Onlyfans", "OnlyfansModels", "Amateurs"}
    phone_kws = re.compile(r"(?i)\b(selfie|mirror|phone|snap|snapchat|bedroom|baddie|amateur|tiktok|onlyfans)\b")

    added_counts = Counter()

    for it in all_tease_pool:
        if it["id"] in assigned_ids:
            continue
        ok, _ = check_solo(it)
        if not ok:
            continue
        tags = set(it.get("tags", []))
        name = it.get("name", "")
        txt = f"{name} {' '.join(tags)}"

        if tags.intersection(shower_tags) or shower_kws.search(txt):
            catalogs_items["xfhq_shower_wet"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_shower_wet"] += 1
        elif tags.intersection(thick_tags) or thick_kws.search(txt):
            catalogs_items["xfhq_thick_booty"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_thick_booty"] += 1
        elif tags.intersection(strip_tags) or strip_kws.search(txt):
            catalogs_items["xfhq_solo_strip"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_solo_strip"] += 1
        elif tags.intersection(phone_tags) or phone_kws.search(txt) or it.get("orientation") == "vertical":
            catalogs_items["xfhq_phone_selfie"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_phone_selfie"] += 1

    # D2. ROUTE HARVESTED CREATOR CLIPS (REDGIFS / ONLYFANS USERS)
    for it in harvested:
        if it["id"] in assigned_ids:
            continue
        ok, _ = check_solo(it)
        if not ok:
            continue
        tags = set(it.get("tags", []))
        name = it.get("name", "")
        txt = f"{name} {' '.join(tags)}"

        if tags.intersection(shower_tags) or shower_kws.search(txt):
            catalogs_items["xfhq_shower_wet"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_shower_wet"] += 1
        elif tags.intersection(thick_tags) or thick_kws.search(txt):
            catalogs_items["xfhq_thick_booty"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_thick_booty"] += 1
        elif tags.intersection(strip_tags) or strip_kws.search(txt):
            catalogs_items["xfhq_solo_strip"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_solo_strip"] += 1
        else:
            catalogs_items["xfhq_phone_selfie"].append(it)
            assigned_ids.add(it["id"])
            added_counts["xfhq_phone_selfie"] += 1

    # E. ROUTE PAKISTANI CANDIDATES (AUTHENTIC PHONE LEAKS ONLY)
    paki_pat = re.compile(r"(?i)\b(pakistan|pakistani|lahore|karachi|islamabad|rawalpindi|peshawar|punjabi|pathan|minahil|alina|imsha|alisha|ayesha|zartaj|marry|faisalabad|multan|gujranwala|sialkot)\b")

    for it in paki + masti + desi:
        if it["id"] in assigned_ids:
            continue
        st = it.get("stream_url") or it.get("url") or ""
        if not st or "cdn.fsiblogxx.com" in st:
            continue
        name = it.get("name", "")
        txt = f"{name} {' '.join(it.get('tags', []))}"
        if WESTERN_PORNSTAR_PAT.search(txt) or CREATOR_OR_STUDIO_BAN.search(txt):
            continue
        if paki_pat.search(txt) or any("pakistan" in t.lower() for t in it.get("tags", [])):
            if score_phone_leak(it) > 0:
                ok, _ = check_universal(it)
                if ok:
                    catalogs_items["xfhq_desi_pakistan"].append(it)
                    assigned_ids.add(it["id"])
                    added_counts["xfhq_desi_pakistan"] += 1

    # F. ROUTE AUTHENTIC DESI PHONE MMS LEAKS (ZERO CREATOR SLOP)
    for it in desi + masti + paki:
        if it["id"] in assigned_ids:
            continue
        st = it.get("stream_url") or it.get("url") or ""
        if not st or "cdn.fsiblogxx.com" in st:
            continue
        name = it.get("name", "")
        txt = f"{name} {' '.join(it.get('tags', []))}"
        if WESTERN_PORNSTAR_PAT.search(txt) or CREATOR_OR_STUDIO_BAN.search(txt):
            continue

        if score_phone_leak(it) > 0:
            ok, _ = check_universal(it)
            if ok:
                catalogs_items["xfhq_desi_mms"].append(it)
                assigned_ids.add(it["id"])
                added_counts["xfhq_desi_mms"] += 1

    print("\n--- Expansion results ---")
    for cid in TARGET_CATALOG_IDS:
        print(f"  {cid:22}: +{added_counts[cid]:4} new -> Total: {len(catalogs_items[cid]):4}")

    # G. RANK ITEMS IN EACH CATALOG
    print("\n--- Ranking items ---")
    for cid in ["xfhq_thick_booty", "xfhq_shower_wet", "xfhq_solo_strip", "xfhq_phone_selfie"]:
        catalogs_items[cid].sort(key=lambda x: rank_key(x, special_id=haley_item["id"]))

    for cid in ["xfhq_desi_mms", "xfhq_desi_pakistan"]:
        catalogs_items[cid].sort(
            key=lambda x: (
                -score_phone_leak(x),  # Purest phone leaks (calls, bedroom, hotel, snapchat) first
                0 if "720" in str(x.get("quality", "")) else 1,
                -x.get("likes", 0) if isinstance(x.get("likes"), int) else 0
            )
        )

    # H. WRITE META AND STREAM FILES FOR ANY NEW ITEMS
    print("\n--- Writing meta and stream JSON files ---")
    meta_dir = REPO_ROOT / "meta" / "movie"
    stream_dir = REPO_ROOT / "stream" / "movie"
    meta_dir.mkdir(parents=True, exist_ok=True)
    stream_dir.mkdir(parents=True, exist_ok=True)

    written_meta = 0
    written_stream = 0

    for cid in TARGET_CATALOG_IDS:
        for it in catalogs_items[cid]:
            vid_id = it["id"]
            m_path = meta_dir / f"{vid_id}.json"
            s_path = stream_dir / f"{vid_id}.json"

            if not m_path.exists():
                m_obj = {"meta": to_meta(it)}
                m_path.write_text(json.dumps(m_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
                written_meta += 1

            if not s_path.exists():
                st_url = it.get("stream_url") or it.get("url") or ""
                if not st_url or "cdn.fsiblogxx.com" in st_url:
                    continue
                s_obj = {
                    "streams": [
                        {
                            "url": st_url,
                            "name": "Direct Stream",
                            "title": f"{it.get('name', '')} [{it.get('quality', '1080p+')}]",
                            "behaviorHints": {"notWebReady": False}
                        }
                    ]
                }
                s_path.write_text(json.dumps(s_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
                written_stream += 1

    print(f"Newly written meta files: {written_meta}, stream files: {written_stream}")

    # I. WRITE PAGINATED CATALOG FILES
    print("\n--- Writing paginated catalog JSON files ---")
    all_active_metas = []

    for cat_def in TARGET_CATALOGS:
        cid = cat_def["id"]
        if cid == "xfhq_search":
            continue
        items = catalogs_items[cid]
        metas = [to_meta(it) for it in items]
        all_active_metas.extend(metas)

        # Base catalog (Page 0)
        base_json = cat_movie_dir / f"{cid}.json"
        base_json.write_text(
            json.dumps({"metas": metas[:PAGE_SIZE]}, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8"
        )

        cat_dir = cat_movie_dir / cid
        # Clean old skip files in this cat_dir
        if cat_dir.exists():
            for old_p in cat_dir.glob("skip=*.json"):
                old_p.unlink()
        else:
            cat_dir.mkdir(parents=True, exist_ok=True)

        for skip in range(PAGE_SIZE, len(metas), PAGE_SIZE):
            chunk = metas[skip : skip + PAGE_SIZE]
            skip_file = cat_dir / f"skip={skip}.json"
            skip_file.write_text(
                json.dumps({"metas": chunk}, separators=(",", ":"), ensure_ascii=False),
                encoding="utf-8"
            )

    # J. GENERATE XFHQ_SEARCH PRE-COMPUTED SEARCH FILES
    print("\n--- Indexing unified search catalog (xfhq_search) ---")
    search_dir = cat_movie_dir / "xfhq_search"
    search_dir.mkdir(parents=True, exist_ok=True)

    # Base search file
    (cat_movie_dir / "xfhq_search.json").write_text(
        json.dumps({"metas": all_active_metas[:PAGE_SIZE]}, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8"
    )

    # Get search queries to index
    search_queries = set()
    for f in search_dir.glob("search=*.json"):
        q = f.stem.replace("search=", "").strip()
        if q:
            search_queries.add(q)

    # Add core queries and requested creator handles
    core_queries = [
        "", "1080p", "4k", "shower", "bath", "twerk", "booty", "strip", "tease",
        "onlyfans", "selfie", "mirror", "amateur", "solo", "pakistani", "desi",
        "mms", "creators", "haley", "curvy", "thick", "soapy", "lingerie", "dance",
        "viral", "leak", "scandal", "call", "hotel", "bhabhi", "aunty", "college", "tape", "punjabi", "lahore", "karachi",
        "whitebat", "cutesylucy", "respectedcommander1", "galablack12", "toxicant",
        "kenalialuv", "scarlettcross", "sandrossi", "halibell", "hhhkcncm",
        "audreyandsadie", "leilacopperbottom", "theivoryfox", "drydiggler", "snarkvixen",
        "virginiabsbsbsns", "violetbrandani", "goatzillax", "laderlora225", "sofiamiller",
        "nudespair", "harry2000", "rorryree", "violetmoore", "lunawickedsoul",
        "cumslutqueen", "princessiggy", "pinkdroid462", "theemilylynne", "cyberlycrush",
        "idontwatchporn1", "populardick", "aaronsnowxxx", "phdprincess", "yamimommy",
        "thiccameron", "blondeadobo", "stupittard", "lilbraids", "needitforme", "applefriend"
    ]
    for q in core_queries:
        search_queries.add(q)

    for q in search_queries:
        q_clean = q.lower()
        matches = [
            m for m in all_active_metas
            if q_clean in (m.get("name", "") + " " + " ".join(m.get("genres", []))).lower()
        ][:PAGE_SIZE]
        search_file = search_dir / f"search={q}.json"
        search_file.write_text(
            json.dumps({"metas": matches}, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8"
        )

    # K. UPDATE CATALOG_POLICY.JSON
    print("\n--- Updating catalog_policy.json ---")
    policy_path = REPO_ROOT / "catalog_policy.json"
    policy_data = json.loads(policy_path.read_text(encoding="utf-8"))

    # Only retain xfhq_phone_selfie in additional_collections (prune archive and unverified)
    new_add_colls = {}
    if "xfhq_phone_selfie" in policy_data.get("additional_collections", {}):
        new_add_colls["xfhq_phone_selfie"] = policy_data["additional_collections"]["xfhq_phone_selfie"]
    policy_data["additional_collections"] = new_add_colls

    # Catalog names restricted to target catalogs
    policy_data["catalog_names"] = {
        c["id"]: c["name"] for c in TARGET_CATALOGS if c["id"] != "xfhq_search"
    }

    policy_path.write_text(
        json.dumps(policy_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # L. UPDATE MANIFEST.JSON
    print("\n--- Updating manifest.json ---")
    ver = make_semver_timestamp()
    total_active = sum(len(catalogs_items[cid]) for cid in TARGET_CATALOG_IDS)

    manifest = {
        "id": "com.savaa.stremio.solo",
        "version": ver,
        "name": "⭐ Vidi 4K: Solo, Tease & Desi MMS Suite",
        "description": (
            f"Curated Stremio Master Suite: {total_active} videos across {len(TARGET_CATALOG_IDS)} categories. "
            f"Direct 1080p+/4K Portrait Solo, OnlyFans Leaks, Striptease, Shower, Curvy Twerk & Authentic Desi/Pakistani Phone MMS Leaks. "
            f"100% Filtered & Verified Direct Streams."
        ),
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["xfhq", "masti_", "pb_", "paki_", "desi_", "rg_"],
        "catalogs": TARGET_CATALOGS,
        "behaviorHints": {"adult": True, "configurable": False}
    }

    (REPO_ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # M. GENERATE M3U PLAYLISTS
    print("\n--- Generating M3U Playlists ---")
    m3u_all = ["#EXTM3U", f"#PLAYLIST:Vidi 4K Master Solo Suite ({ver})"]
    m3u_4k = ["#EXTM3U", f"#PLAYLIST:Vidi 4K Ultra Suite ({ver})"]
    m3u_desi = ["#EXTM3U", f"#PLAYLIST:Vidi Desi & Pakistani MMS Suite ({ver})"]

    for cid in ["xfhq_thick_booty", "xfhq_shower_wet", "xfhq_solo_strip", "xfhq_phone_selfie"]:
        cname = next(c["name"] for c in TARGET_CATALOGS if c["id"] == cid)
        for it in catalogs_items[cid]:
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

    for cid in ["xfhq_desi_mms", "xfhq_desi_pakistan"]:
        cname = next(c["name"] for c in TARGET_CATALOGS if c["id"] == cid)
        for it in catalogs_items[cid]:
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

    print(f"\n✅ REBUILD COMPLETE! Version {ver} generated.")
    print(f"Total active videos: {total_active} across {len(TARGET_CATALOG_IDS)} categories.")
    for cid in TARGET_CATALOG_IDS:
        print(f"  {cid:22}: {len(catalogs_items[cid]):4} videos")

if __name__ == "__main__":
    rebuild()

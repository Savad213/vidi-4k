"""
Multi-threaded Harvester for LO's Creator Models & Preferred Tags
Extracts high-resolution vertical solo videos (1080p+) from RedGIFs.
Strictly verified adult solo creators matching LO's aesthetic and tags.
"""

import json
import time
import urllib.request
import urllib.parse
import ssl
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).resolve().parent

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_auth_token():
    req = urllib.request.Request("https://api.redgifs.com/v2/auth/temporary", headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("token")

DISALLOWED_TAGS = {
    'pregnant', 'pregnantsolo', 'pregnanttits',
    'ebony', 'black', 'darkskin',
    'granny', 'mature', 'gilf', 'old',
    'hentai', 'anime', '3d', 'animation',
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

def is_clean_solo(gif):
    tags = [t.lower() for t in gif.get("tags", []) + gif.get("niches", [])]
    desc = gif.get("description", "")
    txt = f"{desc} {' '.join(tags)}"

    for t in tags:
        if t in DISALLOWED_TAGS:
            return False

    if SOLO_EXCLUSION_PATTERN.search(txt):
        return False

    return True

REQUESTED_CREATORS = [
    'lit1le_kitty', 'emili_lit1le', 'vickyltk', 'licalicalica', 'cceelinne',
    'anastasiis', 'manygirlz', 'juliet.bb', 'stella.cardo', 'amybounce',
    'leia_von', 'emilysweet', 'your_briana', 'marinettevip', 'japp_leack',
    'alinabecker', 'sophiemudd', 'hannahowo', 'ari kytsya', 'arikytsya',
    'maria.marry', 'mariamarry', 'jess fox', 'jessfox', 'lilygrace',
    'virginlily', 'wellass', 'comatozze', 'fantasybabe', 'blackwidof',
    'littlereislin', 'kisscat', 'mila daisy', 'miladaisy', 'amalie pearl',
    'amaliepearl', 'luxury girl', 'luxurygirl', 'arisha mills', 'arishamills',
    'bella mur', 'bellamur', 'ivana montana', 'ivanamontana', 'diana rider',
    'dianarider', 'sonya blaze', 'sonyablaze', 'anny walker', 'annywalker',
    'verlonis', 'elina lizz', 'elinalizz', 'yummy mira', 'yummymira',
    'daliamorgan', 'californiababe', 'alexa poshspicy', 'alexaposhspicy',
    'skye wood', 'skyewood', 'savannah watson', 'savannahwatson', 'slimthick vic',
    'slimthickvic', 'hazel moore', 'hazelmoore', 'katrina colt', 'katrinacolt',
    'cicii doll', 'ciciidoll', 'nicoly rio', 'nicolyrio',
    'olivia bay', 'oliviabay', 'hot pearl', 'hotpearl', 'sugary kitty',
    'sugarykitty', 'alexa flexy', 'alexaflexy',
    'sophie rain', 'sophierain', 'sweetie fox', 'sweetiefox',
    'kalinka fox', 'kalinkafox', 'alice delish', 'alicedelish',
    'byoru', 'shirogane sama', 'shiroganesama', 'carrykey',
    'lady melamori', 'astasiadream', 'katerina roxy', 'peachmilky',
    'hana bunny', 'fegalvao', 'kerolay chaves', 'martina olvr',
    'sky bri', 'skybri', 'breckie hill', 'breckiehill', 'faith ordway',
    'daisy keech', 'sommer ray', 'mikayla demaiter', 'corinna kopf',
    'katja krasavice', 'julia rose', 'lauren burch', 'julia burch',
    'strawberry tabby', 'bellabb', 'dva_pew', 'xenon', 'oichi',
    'helly valentine',
    # Top verified RedGifs curvy solo favorites
    'whitebat', 'cutesylucy', 'respectedcommander1', 'galablack12', 'toxicant',
    'kenalialuv', 'halibell', 'leilacopperbottom', 'theivoryfox', 'goatzillax',
    'princessiggy', 'pinkdroid462', 'theemilylynne', 'cyberlycrush', 'phdprincess',
    'yamimommy', 'thiccameron', 'blondeadobo', 'lilbraids'
]

PREFERRED_TAG_QUERIES = [
    # Booty, Twerk & Motion
    'twerk', 'twerking', 'booty shake', 'booty bounce', 'ass jiggle', 'booty clap',
    'slow mo twerk', 'booty wiggle', 'twerk solo', 'bed twerk', 'mirror twerk',
    'bubble butt shake',
    # Wardrobe & Fit Checks
    'scrunch leggings', 'gym leggings', 'yoga pants', 'booty shorts', 'spandex',
    'thong tease', 'try on haul', 'bikini try on', 'lingerie try on', 'swimsuit try on',
    'underbutt', 'micro thong',
    # Tease & Striptease
    'slow tease', 'striptease', 'slow strip', 'undressing', 'clothing peel',
    'edging tease', 'skirt flip', 'skirt lift', 'towel drop', 'robe tease',
    # Shower, Bath, Wet & Oil
    'shower tease', 'steamy shower', 'shower solo', 'wet look', 'wet skin',
    'dripping wet', 'soapy bath', 'bubble bath', 'body oil tease', 'oiled booty',
    'nuru massage',
    # Posing, Mirror & Angles
    'mirror tease', 'mirror booty', 'back arch', 'bending over', 'kneeling tease',
    'vertical pov', 'gfe solo', 'bed tease', 'morning routine', 'baddie selfie'
]

def fetch_feed(query_or_user, is_user, token):
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    
    if is_user:
        url = f"https://api.redgifs.com/v2/users/{urllib.parse.quote(query_or_user)}/search?count=60"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("gifs", [])
        except Exception:
            pass
            
    # Fallback to general search
    search_url = f"https://api.redgifs.com/v2/gifs/search?search_text={urllib.parse.quote(query_or_user)}&count=60&order=trending"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("gifs", [])
    except Exception as e:
        print(f"Error fetching {query_or_user}: {e}")
        return []

def run_harvest():
    print("=== Step 1: Getting RedGIFs Auth Token ===")
    token = get_auth_token()
    print("Auth Token obtained successfully.")

    out_file = REPO_ROOT / "harvested_creators.json"
    harvested = []
    seen_ids = set()
    if out_file.exists():
        try:
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            for it in existing:
                harvested.append(it)
                gid = it.get("id", "").replace("rg_", "")
                if gid:
                    seen_ids.add(gid)
            print(f"Loaded {len(harvested)} existing items from {out_file.name}")
        except Exception as e:
            print(f"Error loading existing {out_file.name}: {e}")

    # Build work queue
    tasks = []
    for u in REQUESTED_CREATORS:
        tasks.append((u, True))
    for q in PREFERRED_TAG_QUERIES:
        tasks.append((q, False))

    print(f"\n=== Step 2: Processing {len(tasks)} queries in parallel (10 threads) ===")
    
    new_added = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_task = {executor.submit(fetch_feed, t[0], t[1], token): t for t in tasks}
        for future in as_completed(future_to_task):
            item_name, is_user = future_to_task[future]
            try:
                gifs = future.result()
            except Exception as e:
                print(f"Task failed for {item_name}: {e}")
                continue

            count_for_task = 0
            for g in gifs:
                gid = g.get("id")
                if not gid or gid in seen_ids:
                    continue
                w = g.get("width", 0)
                h = g.get("height", 0)
                if h < w:  # Strictly vertical
                    continue
                if not is_clean_solo(g):
                    continue

                hd_url = g.get("urls", {}).get("hd") or g.get("urls", {}).get("sd")
                poster_url = g.get("urls", {}).get("poster") or g.get("urls", {}).get("thumbnail")
                if not hd_url or not poster_url:
                    continue

                dur = int(float(g.get("duration") or 0))
                runtime = f"{dur // 60}:{dur % 60:02d}" if dur >= 60 else f"0:{dur:02d}"
                tags = g.get("tags", [])
                user_name = g.get("userName", item_name)
                title_desc = ', '.join(tags[:3]) if tags else 'Vertical Solo'
                name = f"{user_name}: {title_desc}"

                item = {
                    "id": f"rg_{gid}",
                    "name": name,
                    "title": f"{name} [1080p Vertical]",
                    "user": user_name,
                    "stream_url": hd_url,
                    "url": hd_url,
                    "poster": poster_url,
                    "thumbnail": poster_url,
                    "logo": poster_url,
                    "quality": "1080p+",
                    "resolution": f"{w}x{h}",
                    "orientation": "vertical",
                    "duration": dur,
                    "runtime": runtime,
                    "likes": g.get("likes", 0),
                    "tags": tags + g.get("niches", []) + ["Vertical", "Onlyfans", "Solo"]
                }
                harvested.append(item)
                seen_ids.add(gid)
                count_for_task += 1
                new_added += 1

            if count_for_task > 0:
                print(f"[{item_name}] added {count_for_task} vertical clips")

    out_file.write_text(json.dumps(harvested, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Finished harvesting! Newly added: {new_added}. Total library: {len(harvested)} clips.")

if __name__ == "__main__":
    run_harvest()

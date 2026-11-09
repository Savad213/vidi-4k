"""
Mass Deep Harvester for High-Quality Vertical Tease
Harvests thousands of native 1080p/4K vertical solo tease, strip, shower & booty flaunt clips
from RedGIFs API across verified solo creators, niches, and multi-page search queries.
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

def log(msg):
    print(msg, flush=True)

def get_auth_token():
    req = urllib.request.Request("https://api.redgifs.com/v2/auth/temporary", headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("token")

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
    'whitebat', 'cutesylucy', 'respectedcommander1', 'galablack12', 'toxicant',
    'kenalialuv', 'scarlettcross', 'sandrossi', 'halibell', 'hhhkcncm',
    'audreyandsadie', 'leilacopperbottom', 'theivoryfox', 'drydiggler', 'snarkvixen',
    'virginiabsbsbsns', 'violetbrandani', 'goatzillax', 'laderlora225', 'sofiamiller',
    'nudespair', 'harry2000', 'rorryree', 'violetmoore', 'lunawickedsoul',
    'cumslutqueen', 'princessiggy', 'pinkdroid462', 'theemilylynne', 'cyberlycrush',
    'idontwatchporn1', 'populardick', 'aaronsnowxxx', 'phdprincess', 'yamimommy',
    'thiccameron', 'blondeadobo', 'stupittard', 'lilbraids', 'needitforme', 'applefriend'
]

VERTICAL_QUERIES = [
    # Strip & Tease
    'lingerie striptease', 'solo striptease', 'slow striptease', 'undress slow',
    'sensual tease', 'striptease tease', 'peeling lingerie', 'silk robe tease',
    'sensual solo dance', 'bedroom tease solo',
    # Curvy Booty & Twerk
    'curvy twerk', 'thick onlyfans', 'thick booty dance', 'bubble butt twerk',
    'twerk tease', 'booty flaunt', 'natural hourglass', 'thick thighs',
    'phat ass twerk', 'thick dancer',
    # Shower & Wet Bath
    'shower tease', 'sensual shower', 'soapy shower tease', 'wet bath solo',
    'oil tease', 'bath tease',
    # Mirror & Phonecam Selfies
    'mirror selfie nude', 'baddie selfie', 'phone selfie nude', 'onlyfans mirror selfie',
    'morning stretch tease', 'bikini try on'
]

NICHES = [
    'thick-booty', 'phat-ass-white-girls', 'curvy-chicks', 'tik-tok', 'amateur-girls'
]

def fetch_json(url, token):
    h = dict(HEADERS)
    h["Authorization"] = f"Bearer {token}"
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            time.sleep(0.2)
    return {}

def harvest_deep():
    log("=" * 70)
    log("MASS HARVEST: HIGH QUALITY VERTICAL TEASE")
    log("=" * 70)

    token = get_auth_token()
    log(f"RedGIFs Auth Token obtained: {token[:10]}...")

    harvested_path = REPO_ROOT / "harvested_creators.json"
    existing_items = json.loads(harvested_path.read_text(encoding="utf-8")) if harvested_path.exists() else []
    seen_ids = set(it["id"].replace("rg_", "") for it in existing_items)
    log(f"Existing in harvested_creators.json: {len(existing_items)} clips")

    target_urls = []

    # 1. Creators - pages 1 and 2
    for u in REQUESTED_CREATORS:
        target_urls.append((f"https://api.redgifs.com/v2/users/{u}/search?count=50&page=1", u))
        target_urls.append((f"https://api.redgifs.com/v2/users/{u}/search?count=50&page=2", u))
        target_urls.append((f"https://api.redgifs.com/v2/gifs/search?search_text={u}&count=40&order=trending", u))

    # 2. Vertical Queries - pages 1 to 3 with trending & best orders
    for q in VERTICAL_QUERIES:
        enc_q = urllib.parse.quote(q)
        for p in range(1, 4):
            target_urls.append((f"https://api.redgifs.com/v2/gifs/search?search_text={enc_q}&count=40&page={p}&order=trending", q))
            target_urls.append((f"https://api.redgifs.com/v2/gifs/search?search_text={enc_q}&count=40&page={p}&order=best", q))

    # 3. Niches - pages 1 to 3
    for n in NICHES:
        for p in range(1, 4):
            target_urls.append((f"https://api.redgifs.com/v2/gifs/search?niches={n}&count=40&page={p}&order=trending", n))
            target_urls.append((f"https://api.redgifs.com/v2/gifs/search?niches={n}&count=40&page={p}&order=best", n))

    log(f"Total API feed endpoints to fetch: {len(target_urls)} (8 workers)...")

    new_clips = []
    
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_json, u[0], token): u for u in target_urls}
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 50 == 0 or done == len(target_urls):
                log(f"  Fetched {done}/{len(target_urls)} API endpoints... (Found {len(new_clips)} new vertical clips)")
            data = f.result()
            gifs = data.get("gifs", [])
            for g in gifs:
                gid = g.get("id")
                if not gid or gid in seen_ids:
                    continue
                w = g.get("width", 0)
                h = g.get("height", 0)
                # Strict portrait vertical: height must exceed or equal width
                if h < w:
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
                user_name = g.get("userName", "SoloCreator")
                name = f"{user_name}: {', '.join(tags[:3]) if tags else 'Solo Tease'}"

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
                    "tags": tags + g.get("niches", []) + ["Vertical", "Solo", "Tease"]
                }
                new_clips.append(item)
                seen_ids.add(gid)

    log(f"\nHarvest finished! Extracted {len(new_clips)} brand new high quality vertical tease clips.")

    existing_items.extend(new_clips)
    harvested_path.write_text(json.dumps(existing_items, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    log(f"Saved total {len(existing_items)} clips to {harvested_path.name}.")

if __name__ == '__main__':
    harvest_deep()

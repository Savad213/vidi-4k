"""
Harvest high-resolution vertical solo videos for LO's 41 requested creator handles
plus similar top trending vertical creators from RedGIFs.
"""

import json
import time
import urllib.request
import ssl
import re
from pathlib import Path
from collections import defaultdict

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

SIMILAR_SEARCH_QUERIES = [
    'curvy twerk', 'thick onlyfans', 'shower tease', 'mirror selfie nude',
    'lingerie striptease', 'thick booty dance', 'sensual shower', 'baddie selfie'
]

def harvest():
    print("=== Step 1: Getting RedGIFs Auth Token ===")
    token = get_auth_token()
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    print("Token OK!")

    harvested = []
    seen_ids = set()

    # A. Harvest requested creators
    print("\n=== Step 2: Harvesting Requested Creators ===")
    for u in REQUESTED_CREATORS:
        url = f"https://api.redgifs.com/v2/users/{u}/search?count=50"
        gifs = []
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                gifs = data.get("gifs", [])
        except Exception:
            search_url = f"https://api.redgifs.com/v2/gifs/search?search_text={u}&count=40"
            try:
                req2 = urllib.request.Request(search_url, headers=headers)
                with urllib.request.urlopen(req2, context=ctx, timeout=8) as resp2:
                    data2 = json.loads(resp2.read().decode("utf-8"))
                    gifs = data2.get("gifs", [])
            except Exception as e:
                print(f"Error {u}: {e}")

        added_for_user = 0
        for g in gifs:
            gid = g.get("id")
            if not gid or gid in seen_ids:
                continue
            # Vertical check: height >= width
            w = g.get("width", 0)
            h = g.get("height", 0)
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
            name = f"{g.get('userName', u)}: {', '.join(tags[:3]) if tags else 'Solo Tease'}"

            item = {
                "id": f"rg_{gid}",
                "name": name,
                "title": f"{name} [1080p Vertical]",
                "user": g.get("userName", u),
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
            added_for_user += 1

        print(f"Creator {u:20}: added {added_for_user} vertical clips")
        time.sleep(0.1)

    # B. Harvest similar creators & niche feeds
    print("\n=== Step 3: Harvesting Similar Vertical Solo Feeds ===")
    for q in SIMILAR_SEARCH_QUERIES:
        search_url = f"https://api.redgifs.com/v2/gifs/search?search_text={urllib.parse.quote(q)}&count=40&order=trending"
        gifs = []
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                gifs = data.get("gifs", [])
        except Exception as e:
            print(f"Search error {q}: {e}")

        added_for_q = 0
        for g in gifs:
            gid = g.get("id")
            if not gid or gid in seen_ids:
                continue
            w = g.get("width", 0)
            h = g.get("height", 0)
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
                "tags": tags + g.get("niches", []) + ["Vertical", "Onlyfans", "Solo"]
            }
            harvested.append(item)
            seen_ids.add(gid)
            added_for_q += 1

        print(f"Feed '{q:22}': added {added_for_q} vertical clips")
        time.sleep(0.1)

    out_file = REPO_ROOT / "harvested_creators.json"
    out_file.write_text(json.dumps(harvested, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Total harvested clean vertical clips: {len(harvested)}")
    print(f"Saved to {out_file.name}")

if __name__ == "__main__":
    import urllib.parse
    harvest()

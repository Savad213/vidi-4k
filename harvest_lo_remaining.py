"""
Deep RedGIFs Harvester for LO's Remaining Missing Creator Models
Includes rate-limit handling (HTTP 429 backoff) and clean vertical solo/creator filtering.
"""

import json
import time
import urllib.request
import urllib.parse
import ssl
import re
from pathlib import Path

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
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
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
    dude|dudes|man|men|male|males|boyfriend|bf|husband|uncle|boss|driver|
    balls|bwc|bbc|lund|loda|
    analplug|buttplug|strapon|sexmachine|
    dildo|giantdildo|hugeanaldildo|sybian
)\b""", re.VERBOSE)

def is_clean_item(g):
    tags = [t.lower() for t in g.get("tags", []) + g.get("niches", [])]
    desc = g.get("description", "")
    txt = f"{desc} {' '.join(tags)}"

    for t in tags:
        if t in DISALLOWED_TAGS:
            return False

    if SOLO_EXCLUSION_PATTERN.search(txt):
        return False

    return True

REMAINING_MODELS = [
    'jess fox', 'jessfox', 'lilygrace', 'virginlily', 'vickyltk',
    'licalicalica', 'cceelinne', 'anastasiis', 'manygirlz', 'juliet.bb',
    'stella.cardo', 'emilysweet', 'your_briana', 'hannah owo', 'hannahowo',
    'sophie mudd', 'sophiemudd', 'alina becker', 'alinabecker',
    'rebecca mcleod', 'fantasybabe', 'marinettevip', 'wellass', 'adele'
]

def harvest():
    print("=== Getting RedGIFs Auth Token ===", flush=True)
    token = get_auth_token()
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"

    out_file = REPO_ROOT / "harvested_creators.json"
    harvested = []
    seen_ids = set()

    if out_file.exists():
        try:
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            for it in existing:
                harvested.append(it)
                gid = it.get("id", "").replace("xfhq_rg_", "").replace("rg_", "")
                if gid:
                    seen_ids.add(gid)
            print(f"Loaded {len(harvested)} existing items. Seen IDs: {len(seen_ids)}", flush=True)
        except Exception as e:
            print(f"Error loading {out_file.name}: {e}", flush=True)

    total_added = 0
    print("\n=== Harvesting Remaining Missing Models with Rate-Limit Backoff ===", flush=True)
    for model_name in REMAINING_MODELS:
        model_added = 0
        for page in range(1, 3):
            search_url = f"https://api.redgifs.com/v2/gifs/search?search_text={urllib.parse.quote(model_name)}&count=30&page={page}&order=trending"
            
            gifs = []
            for attempt in range(3):
                try:
                    req = urllib.request.Request(search_url, headers=headers)
                    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        gifs = data.get("gifs", [])
                        break
                except urllib.error.HTTPError as he:
                    if he.code == 429:
                        print(f"  [429 Rate Limit on {model_name}] Backing off 6s...", flush=True)
                        time.sleep(6)
                    else:
                        break
                except Exception as e:
                    break

            if not gifs:
                time.sleep(1.2)
                continue

            for g in gifs:
                gid = g.get("id")
                if not gid or gid in seen_ids:
                    continue

                w = g.get("width", 0)
                h = g.get("height", 0)
                if h < w:  # Keep strictly vertical
                    continue

                if not is_clean_item(g):
                    continue

                hd_url = g.get("urls", {}).get("hd") or g.get("urls", {}).get("sd")
                poster_url = g.get("urls", {}).get("poster") or g.get("urls", {}).get("thumbnail")
                if not hd_url or not poster_url:
                    continue

                dur = int(float(g.get("duration") or 0))
                runtime = f"{dur // 60}:{dur % 60:02d}" if dur >= 60 else f"0:{dur:02d}"
                tags = g.get("tags", [])
                user_str = g.get("userName", model_name)
                name = f"{user_str}: {', '.join(tags[:3]) if tags else 'Vertical Tease'}"

                item = {
                    "id": f"xfhq_rg_{gid}",
                    "name": name,
                    "title": f"{name} [1080p Vertical]",
                    "user": user_str,
                    "stream_url": hd_url,
                    "video": hd_url,
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
                    "tags": tags + g.get("niches", []) + ["Vertical", "Creator", user_str]
                }
                harvested.append(item)
                seen_ids.add(gid)
                model_added += 1
                total_added += 1

            time.sleep(1.5)

        print(f"  {model_name:20s}: +{model_added:2d} clips (Total: {total_added})", flush=True)

    out_file.write_text(json.dumps(harvested, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Finished! Added {total_added} new clips. Total items in harvested_creators: {len(harvested)}", flush=True)

if __name__ == "__main__":
    harvest()

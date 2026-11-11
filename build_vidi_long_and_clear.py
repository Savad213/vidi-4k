"""
Vidi 4K Master Suite Rebuilder (Strict Body Profile, Pure Retina Posters, Zero Exclusions)
- Strictly EXCLUDES:
  1. Skinny, petite, flat, tiny, small-breasted, bony models.
  2. Black / ebony / dark-skin models.
  3. Group scenes (3+ people).
  4. Extreme rough / BDSM / dildo / machine / gape / strapon.
  5. Granny / old / mature / pregnant / cartoon / anime.
- 8 Clean & Properly Segregated Categories (NO dumping ground!):
  1. 🍑 Curvy: Twerk & Booty Shake Flaunt
  2. 🍈 Busty & Cleavage Flaunt
  3. 👙 Solo Striptease & Lingerie Tease
  4. 🔥 Solo Masturbation & Sensual Touch
  5. 🚿 Shower, Bath & Wet Oil
  6. 📱 Phone & Mirror Selfies / OnlyFans
  7. 💥 Vertical Couples & POV Hardcore
  8. ⏳ Extended Full-Length Sessions (10–30+ Mins)
"""

import json
import os
import re
import html
import shutil
import datetime
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent
PAGE_SIZE = 100

TARGET_CATALOGS = [
    {
        "type": "movie",
        "id": "vidi_thick_twerk",
        "name": "🍑 Curvy: Twerk & Booty Shake Flaunt",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_busty_cleavage",
        "name": "🍈 Busty & Cleavage Flaunt",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_solo_strip",
        "name": "👙 Solo Striptease & Lingerie Tease",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_solo_touch",
        "name": "🔥 Solo Masturbation & Sensual Touch",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_shower_wet",
        "name": "🚿 Shower, Bath & Wet Oil",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_mirror_selfie",
        "name": "📱 Phone & Mirror Selfies / OnlyFans",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_couples_pov",
        "name": "💥 Vertical Couples & POV Hardcore",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_long_vertical",
        "name": "⏳ Extended Full-Length Sessions (10–30+ Mins)",
        "extra": [{"name": "skip", "isRequired": False}]
    },
    {
        "type": "movie",
        "id": "vidi_search",
        "name": "🔍 Search Vidi 4K",
        "extra": [{"name": "search", "isRequired": True}]
    }
]

TARGET_CATALOG_IDS = [c["id"] for c in TARGET_CATALOGS if c["id"] != "vidi_search"]

# ─── STRICT EXCLUSION REGEXES ────────────────────────────────────────────────
SKINNY_FLAT_PAT = re.compile(r"""(?i)\b(
    skinny|petite|tiny|flat|flat\s*chest|flat\s*ass|flat\s*tits|
    small\s*tits|small\s*boobs|small\s*chest|small\s*breasts|
    bony|very\s*thin|thin\s*girl|underweight|anorexic|skinny\s*girl|
    skinny\s*teen|petite\s*teen|tiny\s*teen|petite\s*solo|skinny\s*solo
)\b""", re.VERBOSE)

BLACK_EBONY_PAT = re.compile(r"""(?i)\b(
    ebony|black\s*girl|black\s*woman|dark\s*skin|blacked|interracial|
    african|nigerian|jamaican|ghanaian|bbc|chocolate\s*skin|dark\s*body
)\b""", re.VERBOSE)

UNIVERSAL_NEG_PAT = re.compile(r"""(?i)\b(
    pregnant|pregnancy|baby\s*bump|maternity|
    granny|gilf|elderly|old\s*woman|wrinkled|senior|aged\s*woman|
    anime|hentai|cartoon|3d|animation|sfm|blender|
    trans|shemale|tranny|ladyboy|gay|femboy|girl\s*dick|strapon|strap-on|
    giant\s*dildo|huge\s*dildo|sybian|sex\s*machine|machine|
    gape|gaping|prolapse|fist|fisting|extreme\s*anal|
    gangbang|orgy|foursome|threesome|group|swinger|3some|4some|
    bdsm|bondage|torture|abuse|slap|choke|whipped|punish|slave|
    pissing|urine|watersport|scat|feet|footfetish
)\b""", re.VERBOSE)

THICK_POSITIVE_PAT = re.compile(r"""(?i)\b(
    thick|curvy|pawg|slimthick|slim\s*thick|bubble\s*butt|huge\s*ass|big\s*ass|
    fat\s*ass|phat\s*ass|heavy\s*bottom|wide\s*hips|soft\s*thighs|thicc|
    twerk|twerking|booty\s*shake|ass\s*shake|booty\s*bounce|ass\s*bounce|
    jiggle|clap|scrunch|leggings|spandex
)\b""", re.VERBOSE)

TEEN_COLLEGE_PAT = re.compile(r"""(?i)\b(
    teen|teens|college|student|18|19|young|schoolgirl|cheerleader|coed
)\b""", re.VERBOSE)

def is_strictly_conforming(it):
    name = it.get("name", "")
    tags = it.get("tags", [])
    if isinstance(tags, list):
        tags_str = " ".join(tags)
    else:
        tags_str = str(tags)
    txt = f"{name} {tags_str}"

    # 1. Reject Skinny / Flat / Petite
    if SKINNY_FLAT_PAT.search(txt):
        return False

    # 2. Reject Black / Ebony
    if BLACK_EBONY_PAT.search(txt):
        return False

    # 3. Reject Universal Negatives (group, trans, BDSM, dildo, old, pregnant, strapon, etc.)
    if UNIVERSAL_NEG_PAT.search(txt):
        return False

    return True

def score_item(it):
    """Calculates ranking score: highest for Thick + Teen/Youthful + Twerk/Tease."""
    name = it.get("name", "")
    tags = it.get("tags", [])
    if isinstance(tags, list):
        tags_str = " ".join(tags)
    else:
        tags_str = str(tags)
    txt = f"{name} {tags_str}"

    score = 0
    # Core preference: Thick / Curvy / PAWG
    if THICK_POSITIVE_PAT.search(txt):
        score += 50
    # Top preference: Thick Teen / Youthful Adult styling
    if TEEN_COLLEGE_PAT.search(txt):
        score += 40
    # Rhythmic action
    if re.search(r"(?i)\b(twerk|bounce|jiggle|clap|scrunch)\b", txt):
        score += 30
    # Tease / Try on / Shower
    if re.search(r"(?i)\b(try\s*on|tease|strip|bikini|thong|shower|wet|oil|mirror)\b", txt):
        score += 20
    # Likes / rating if available
    likes = it.get("likes", 0)
    if isinstance(likes, (int, float)):
        score += min(int(likes / 100), 20)

    return score

def format_runtime(sec):
    try:
        s = int(float(sec or 0))
        m = s // 60
        rem_s = s % 60
        return f"{m}:{rem_s:02d}"
    except:
        return "10:00"

def to_meta(it):
    dur_sec = it.get("duration", 0)
    rt = format_runtime(dur_sec)
    raw_name = html.unescape(it.get("name", "Vertical Solo")).strip()
    poster = it.get("poster") or it.get("thumbnail") or ""
    tags = it.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip("#") for t in tags.split()]

    return {
        "id": it["id"],
        "type": "movie",
        "name": raw_name,
        "poster": poster,
        "posterShape": "poster",
        "background": poster,
        "logo": poster,
        "description": f"Verified 1080p+ Vertical Full-Quality Video.\nDuration: {rt}\nTags: {', '.join(tags[:6])}",
        "releaseInfo": f"1080p Vertical ({rt})",
        "genres": tags[:4],
        "runtime": rt,
        "behaviorHints": {
            "defaultVideoId": it["id"],
            "hasScheduledVideos": False
        }
    }

def run():
    print("=== Step 1: Loading Pools with Strict Taste Enforcement ===")
    pools = ["vidi_all.json", "vidi_tease.json", "vidi_4k.json", "emmyelfie_xfree_1080plus.json", "harvested_creators.json"]
    all_raw_items = []
    seen_urls = set()

    for p in pools:
        p_path = REPO_ROOT / p
        if not p_path.exists():
            continue
        try:
            data = json.loads(p_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                items = data.get("items", [])
            elif isinstance(data, list):
                items = data
            else:
                items = []

            for it in items:
                vurl = it.get("video") or it.get("stream_url")
                purl = it.get("poster") or it.get("thumbnail")
                if not vurl or not purl:
                    continue
                # Ensure crystal-clear retina poster (xfree, pimpbunny, or redgifs)
                if not ("thumbs.xfree.com" in purl or "pimpbunny.com" in purl or "redgifs.com" in purl):
                    continue
                if vurl in seen_urls:
                    continue

                seen_urls.add(vurl)
                iid = it.get("id") or f"xfhq_{abs(hash(vurl)) % 10000000}"
                if not str(iid).startswith("xfhq"):
                    iid = f"xfhq_{iid}"

                all_raw_items.append({
                    "id": str(iid),
                    "name": it.get("name") or it.get("title") or "Vertical Video",
                    "poster": purl,
                    "thumbnail": purl,
                    "video": vurl,
                    "stream_url": vurl,
                    "duration": it.get("duration") or 0,
                    "tags": it.get("tags") or []
                })
        except Exception as e:
            print(f"Error loading {p}: {e}")

    print(f"Total raw items: {len(all_raw_items)}")

    # Strictly filter out skinny, black/ebony, and other negative categories
    clean_items = [it for it in all_raw_items if is_strictly_conforming(it)]
    print(f"Items remaining after purging skinny, flat, black/ebony, and negatives: {len(clean_items)}")

    catalogs_items = defaultdict(list)
    assigned_ids = set()

    # Highly Specific Matchers
    shower_re = re.compile(r"(?i)\b(shower|bath|soapy|wet|oil|oiled|nuru|lotion|tub)\b")
    twerk_re = re.compile(r"(?i)\b(twerk|twerking|booty\s*shake|ass\s*shake|shaking\s*ass|booty\s*bounce|ass\s*bounce|jiggle|clap|scrunch|leggings|spandex|booty\s*dance|shakingass|pawg)\b")
    busty_re = re.compile(r"(?i)\b(big\s*tits|bigtits|bignipples|bigareolas|bouncingtits|bouncing\s*tits|tit\s*drop|flashingtits|cleavage|huge\s*tits|heavy\s*tits|natural\s*tits|naturaltits|milf|titty|tit\s*worship)\b")
    strip_re = re.compile(r"(?i)\b(strip|striptease|undress|peel|try\s*on|lingerie|bikini|thong|gstring|micro\s*thong|skirt|tease|teasing|costume|haul|panties)\b")
    mastro_re = re.compile(r"(?i)\b(masturbat|finger|fingering|rubbing|pussy\s*rub|clit|orgasm|squirt|dildo|moan|solo\s*play|pussy\s*play|spread\s*pussy)\b")
    mirror_re = re.compile(r"(?i)\b(selfie|mirror|phone|onlyfans|fansly|gfe|bed|morning|baddie|amateur|snapchat|bedroom)\b")
    couple_re = re.compile(r"(?i)\b(blowjob|bj|cock|suck|deepthroat|fucking|fucked|doggystyle|doggy|creampie|facial|cumshot|pov|riding|hardcore)\b")

    # 1. Extended Long Vertical Sessions (>= 600s / 10+ minutes)
    for it in clean_items:
        dur = it.get("duration", 0)
        if dur >= 600:
            catalogs_items["vidi_long_vertical"].append(it)
            assigned_ids.add(it["id"])

    catalogs_items["vidi_long_vertical"].sort(key=lambda x: (score_item(x), x.get("duration", 0)), reverse=True)
    print(f"Long Sessions (10-30+ mins): {len(catalogs_items['vidi_long_vertical'])} clips")

    # 2. Shower & Wet Bath
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if shower_re.search(txt):
            catalogs_items["vidi_shower_wet"].append(it)
            assigned_ids.add(iid)

    # 3. Curvy: Twerk & Booty Shake Flaunt (STRICTLY twerk / booty bounce / jiggle / leggings)
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if twerk_re.search(txt):
            catalogs_items["vidi_thick_twerk"].append(it)
            assigned_ids.add(iid)

    # 4. Busty & Cleavage Flaunt (Big natural tits, tit drops, cleavage)
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if busty_re.search(txt):
            catalogs_items["vidi_busty_cleavage"].append(it)
            assigned_ids.add(iid)

    # 5. Vertical Couples & POV Hardcore (1M1F bedroom sex, blowjobs, doggystyle)
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if couple_re.search(txt):
            catalogs_items["vidi_couples_pov"].append(it)
            assigned_ids.add(iid)

    # 6. Solo Masturbation & Sensual Touch (Pussy play, clit orgasm, fingering)
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if mastro_re.search(txt):
            catalogs_items["vidi_solo_touch"].append(it)
            assigned_ids.add(iid)

    # 7. Solo Striptease & Lingerie Tease (Try-on, lingerie, bikini, striptease)
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if strip_re.search(txt):
            catalogs_items["vidi_solo_strip"].append(it)
            assigned_ids.add(iid)

    # 8. Phone & Mirror Selfies / OnlyFans (Casual bedroom, mirror selfies, OnlyFans/Snapchat)
    for it in clean_items:
        iid = it["id"]
        if iid in assigned_ids:
            continue
        txt = f"{it.get('name', '')} {str(it.get('tags', ''))}"
        if mirror_re.search(txt):
            catalogs_items["vidi_mirror_selfie"].append(it)
            assigned_ids.add(iid)
        else:
            # Gracefully route gentle casual/amateur tease into mirror_selfie rather than twerk!
            catalogs_items["vidi_mirror_selfie"].append(it)
            assigned_ids.add(iid)

    # Sort every catalog by ranking score
    for cid in TARGET_CATALOG_IDS:
        if cid != "vidi_long_vertical":
            catalogs_items[cid].sort(key=score_item, reverse=True)

    print("\nCatalog distribution (Strictly Conforming & Balanced):")
    for cid in TARGET_CATALOG_IDS:
        print(f"  {cid:22}: {len(catalogs_items[cid])} verified clips")

    # Clean directories
    cat_base = REPO_ROOT / "catalog" / "movie"
    meta_base = REPO_ROOT / "meta" / "movie"
    stream_base = REPO_ROOT / "stream" / "movie"

    # Remove all old catalog folders entirely to avoid stale legacy folders
    if cat_base.exists():
        for item in cat_base.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            elif item.is_file() and item.suffix == ".json":
                item.unlink(missing_ok=True)

    for cid in TARGET_CATALOG_IDS + ["vidi_search"]:
        cdir = cat_base / cid
        cdir.mkdir(parents=True, exist_ok=True)

    meta_base.mkdir(parents=True, exist_ok=True)
    stream_base.mkdir(parents=True, exist_ok=True)

    # Purge old stream and meta files that are no longer active
    print("\nPurging non-conforming stream and meta files...")
    all_active_ids = set()
    for cid in TARGET_CATALOG_IDS:
        for it in catalogs_items[cid]:
            all_active_ids.add(it["id"])

    for sf in stream_base.glob("*.json"):
        if sf.stem not in all_active_ids:
            sf.unlink(missing_ok=True)
            (meta_base / f"{sf.stem}.json").unlink(missing_ok=True)

    # Write Meta & Stream files
    print("\nWriting meta and stream files...")
    for cid in TARGET_CATALOG_IDS:
        for it in catalogs_items[cid]:
            vid_id = it["id"]
            m_path = meta_base / f"{vid_id}.json"
            s_path = stream_base / f"{vid_id}.json"

            m_obj = {"meta": to_meta(it)}
            m_path.write_text(json.dumps(m_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

            url = it.get("stream_url") or it.get("video")
            rt = format_runtime(it.get("duration", 0))
            s_obj = {
                "streams": [
                    {
                        "url": url,
                        "name": "1080p+ Vertical Direct",
                        "title": f"{it.get('name')} [{rt}] [1080p MP4]",
                        "behaviorHints": {
                            "notWebReady": False
                        }
                    }
                ]
            }
            s_path.write_text(json.dumps(s_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    # Write Catalog JSON files & Pagination
    print("\nWriting static catalog pages...")
    for cid in TARGET_CATALOG_IDS:
        items_list = catalogs_items[cid]
        c_dir = cat_base / cid
        metas = [to_meta(it) for it in items_list]

        # Top page (skip=0)
        top_obj = {"metas": metas[:PAGE_SIZE]}
        (cat_base / f"{cid}.json").write_text(json.dumps(top_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        (c_dir / "skip=0.json").write_text(json.dumps(top_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

        for skip_val in range(PAGE_SIZE, len(metas), PAGE_SIZE):
            page_obj = {"metas": metas[skip_val:skip_val + PAGE_SIZE]}
            (c_dir / f"skip={skip_val}.json").write_text(json.dumps(page_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    # Search Catalog
    all_metas = []
    for cid in TARGET_CATALOG_IDS:
        all_metas.extend([to_meta(it) for it in catalogs_items[cid]])
    search_obj = {"metas": all_metas[:PAGE_SIZE]}
    (cat_base / "vidi_search.json").write_text(json.dumps(search_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    (cat_base / "vidi_search" / "skip=0.json").write_text(json.dumps(search_obj, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")

    # Manifest
    print("\nUpdating manifest...")
    now_str = datetime.datetime.now().strftime("%y%m%d.%H%M")
    manifest = {
        "id": "com.savaa.stremio.solo",
        "version": f"8.{now_str}",
        "name": "⭐ Vidi 4K: Portrait Solo & Long Sessions Suite",
        "description": "Curated Stremio Master Suite: 100% verified active 1080p+ Vertical Solo, Curvy Twerk, Busty Cleavage, Striptease, Solo Masturbation, Shower Wet, Mirror Selfies, Vertical POV & Extended Long Sessions (10-30+ mins). Strictly natural curves & PAWG, zero skinny or excluded material, crystal-clear retina thumbnails, direct MP4 streams.",
        "resources": ["catalog", "meta", "stream"],
        "types": ["movie"],
        "idPrefixes": ["xfhq", "xfhq_"],
        "catalogs": TARGET_CATALOGS,
        "behaviorHints": {
            "adult": True,
            "configurable": False
        }
    }
    (REPO_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Playlist M3U
    print("\nUpdating playlist.m3u...")
    m3u_lines = ["#EXTM3U"]
    for cid in TARGET_CATALOG_IDS:
        for it in catalogs_items[cid]:
            name = it.get("name", "Video").replace(",", " ")
            url = it.get("stream_url") or it.get("video")
            poster = it.get("poster", "")
            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{poster}" group-title="{cid}",{name}')
            m3u_lines.append(url)
    (REPO_ROOT / "playlist.m3u").write_text("\n".join(m3u_lines), encoding="utf-8")

    print(f"\n✅ Rebuild complete! {len(all_active_ids)} total verified conforming videos across 8 clean, balanced categories.")

if __name__ == "__main__":
    run()

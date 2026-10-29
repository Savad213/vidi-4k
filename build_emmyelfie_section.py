"""Build the Emmyelfie catalog from verified XFree profile metadata."""

import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from check_links import probe_stream


ROOT = Path(__file__).parent
CATALOG_ID = "xfhq_emmyelfie"
SOURCE = ROOT / "emmyelfie_xfree_1080plus.json"
PAGE_SIZE = 100
AGE_AMBIGUOUS = re.compile(
    r"(?i)\b(teen|teens|underage|minor|schoolgirl|schoolboy|young\s+girl|young\s+boy)\b"
)


def candidate(record):
    """Accept only high-resolution clips with no age-ambiguous labels."""
    if not str(record.get("id", "")).isdigit():
        return False
    if AGE_AMBIGUOUS.search(record.get("slug", "") + " " + record.get("tags", "")):
        return False
    if max(int(record.get("w") or 0), int(record.get("h") or 0)) < 1920:
        return False
    if not str(record.get("video", "")).startswith("https://cdn.xfree.com/"):
        return False
    if not str(record.get("poster", "")).startswith("https://thumbs.xfree.com/"):
        return False
    return True


def meta_for(record):
    video_id = "xfhq" + record["id"]
    quality = "4K UHD" if max(record["w"], record["h"]) >= 3840 else "1080p FHD"
    seconds = int(record.get("duration") or 0)
    runtime = f"{seconds // 60}:{seconds % 60:02d}"
    title = record["slug"].replace("-", " ").strip().capitalize()
    tags = [tag.strip() for tag in record["tags"].split("#") if tag.strip()]
    summary = f"{quality} Vertical · {record['w']}x{record['h']} · {runtime} · emmyelfie"
    return {
        "id": video_id, "type": "movie", "name": title,
        "poster": record["poster"], "posterShape": "poster",
        "background": record["poster"], "description": summary,
        "genres": tags, "runtime": runtime,
    }, {"streams": [{
        "url": record["video"], "name": "xfree " + quality,
        "title": summary, "behaviorHints": {"notWebReady": False},
    }]}


def main():
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    eligible = list({record["id"]: record for record in records if candidate(record)}.values())
    with ThreadPoolExecutor(max_workers=24) as pool:
        results = list(pool.map(
            probe_stream,
            (("xfhq" + record["id"], record["video"], None) for record in eligible),
        ))
    # A single low-concurrency retry handles transient CDN disconnects.
    transient = {"URLError", "RemoteDisconnected", "TimeoutError"}
    for index, result in enumerate(results):
        if str(result[2]) in transient:
            record = eligible[index]
            results[index] = probe_stream(("xfhq" + record["id"], record["video"], None))
    verified = [
        record for record, (_, alive, _, content_type, _) in zip(eligible, results)
        if alive and not (content_type or "").lower().startswith("text/html")
    ]
    if not verified:
        raise RuntimeError("No profile streams responded; catalog and manifest left unchanged")
    verified.sort(key=lambda record: (
        0 if max(record["w"], record["h"]) >= 3840 else 1,
        -int(record.get("duration") or 0),
    ))

    metas = []
    for record in verified:
        meta, stream = meta_for(record)
        video_id = meta["id"]
        meta_path = ROOT / "meta" / "movie" / f"{video_id}.json"
        stream_path = ROOT / "stream" / "movie" / f"{video_id}.json"
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))["meta"]
        else:
            meta_path.write_text(json.dumps({"meta": meta}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if not stream_path.is_file():
            stream_path.write_text(json.dumps(stream, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        metas.append(meta)

    catalog_dir = ROOT / "catalog" / "movie"
    page_dir = catalog_dir / CATALOG_ID
    page_dir.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(metas), PAGE_SIZE):
        path = (catalog_dir / f"{CATALOG_ID}.json") if start == 0 else (page_dir / f"skip={start}.json")
        path.write_text(json.dumps({"metas": metas[start:start + PAGE_SIZE]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["catalogs"] = [catalog for catalog in manifest["catalogs"] if catalog["id"] != CATALOG_ID]
    manifest["catalogs"].insert(4, {
        "type": "movie", "id": CATALOG_ID, "name": "Emmyelfie Profile (4K & 1080p+)",
        "extra": [{"name": "skip", "isRequired": False}],
    })
    parts = manifest["version"].split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    manifest["version"] = ".".join(parts)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    statuses = Counter(str(result[2]) for result in results)
    print(f"profile_high_quality={len(eligible)} verified={len(verified)} pages={(len(metas) + PAGE_SIZE - 1) // PAGE_SIZE} version={manifest['version']} probe_statuses={dict(statuses)}")


if __name__ == "__main__":
    main()

"""Keep one browse listing per exact source without removing playback records."""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from catalog_policy import apply_policy

PAGE_SIZE = 100


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def make_timestamp_version(major=6, dt=None):
    """Build a semver version with %y%m%d and %H%M patch, stripping leading zeros."""
    import datetime
    if dt is None:
        dt = datetime.datetime.now()
    date_part = dt.strftime("%y%m%d")
    patch_part = str(int(dt.strftime("%H%M")))  # strip leading zero: e.g. "0401" -> "401"
    ver = f"{major}.{date_part}.{patch_part}"
    if re.search(r"(^|\.)0\d", ver):
        raise ValueError(f"CRITICAL: Invalid semver version '{ver}' with leading zero. Stremio rejects this!")
    assert all(p.isdigit() and (p == "0" or not p.startswith("0")) for p in ver.split(".")), f"Invalid semver version: {ver}"
    return ver


def source_groups(root):
    parent = {}
    first = {}

    def find(key):
        parent.setdefault(key, key)
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for path in sorted((root / "stream").glob("*/*.json")):
        key = (path.parent.name, path.stem)
        find(key)
        for stream in load(path).get("streams", []):
            if stream.get("url"):
                identity = ("url", stream["url"])
            elif stream.get("infoHash"):
                identity = ("torrent", stream["infoHash"].lower(), stream.get("fileIdx"))
            else:
                continue
            fingerprint = hashlib.sha256(repr(identity).encode()).digest()
            if fingerprint in first:
                parent[find(key)] = find(first[fingerprint])
            else:
                first[fingerprint] = key
    return find


def catalog_items(root, catalog):
    base = root / "catalog" / catalog["type"] / catalog["id"]
    json_path = base.with_suffix(".json")
    if not json_path.exists():
        return []
    items = load(json_path).get("metas", [])
    pages = sorted(base.glob("skip=*.json"), key=lambda p: int(p.stem.split("=")[1]))
    for page in pages:
        if int(page.stem.split("=")[1]) > 0:
            items.extend(load(page).get("metas", []))
    # Some older builds left videos reachable only through search responses.
    # Include them before assigning owners so cleanup preserves their sources.
    known = {str(item["id"]) for item in items}
    for path in sorted(base.glob("search=*.json")):
        for item in load(path).get("metas", []):
            if str(item["id"]) not in known:
                known.add(str(item["id"]))
                items.append(item)
    return items


def deduplicate(root):
    root = Path(root).resolve()
    manifest_path = root / "manifest.json"
    manifest = load(manifest_path)
    find = source_groups(root)
    original = {c["id"]: catalog_items(root, c) for c in manifest["catalogs"]}
    blocked = apply_policy(root, manifest, original, find, load)
    # Prefer dedicated collections; broad collections receive only unassigned items.
    broad = {"xfhq_curated_favorites": -3, "xfhq_phone_selfie": -2,
             "xfhq_unverified_dimensions": -1, "xfhq_archive_references": -1,
             "xfhq_4k_uhd": 1, "xfhq_luxury_domestic": 2}
    priority = sorted(manifest["catalogs"], key=lambda c: broad.get(c["id"], 0))
    selected = defaultdict(list)
    assigned = set()
    before = set()
    for catalog in priority:
        for item in original[catalog["id"]]:
            identity = find((item.get("type", catalog["type"]), str(item["id"])))
            before.add(identity)
            if identity not in assigned:
                assigned.add(identity)
                selected[catalog["id"]].append(item)
    if before != assigned:
        raise RuntimeError("Source preservation failed")

    for catalog in manifest["catalogs"]:
        items = selected[catalog["id"]]
        base = root / "catalog" / catalog["type"] / catalog["id"]
        save(base.with_suffix(".json"), {"metas": items[:PAGE_SIZE]})
        # Old URLs return empty pages instead of serving stale duplicate listings.
        offsets = {int(p.stem.split("=")[1]) for p in base.glob("skip=*.json")}
        offsets.update(range(PAGE_SIZE, len(items) + PAGE_SIZE, PAGE_SIZE))
        for skip in sorted(offsets):
            save(base / f"skip={skip}.json", {"metas": items[skip:skip + PAGE_SIZE]})
        # Retain existing search vocabulary, restricting each result to its owner.
        allowed = {find((m.get("type", catalog["type"]), str(m["id"]))): m for m in items}
        for path in sorted(base.glob("search=*.json")):
            matches = []
            seen = set()
            for old in load(path).get("metas", []):
                identity = find((old.get("type", catalog["type"]), str(old["id"])))
                if identity in allowed and identity not in seen:
                    seen.add(identity)
                    matches.append(allowed[identity])
            save(path, {"metas": matches[:PAGE_SIZE]})

    manifest["catalogs"] = [c for c in manifest["catalogs"] if selected[c["id"]]]
    manifest["description"] = ("Existing video collections with one browse listing per source. "
        "Resolution and orientation are source-reported, not measured. "
        "Archive references and static links may require a separate player or refreshed access; playback is unverified.")
    manifest["version"] = make_timestamp_version(major=6)
    if re.search(r"(^|\.)0\d", manifest["version"]):
        raise ValueError(f"CRITICAL: Invalid semver version '{manifest['version']}' with leading zero. Stremio rejects this!")
    assert all(p.isdigit() and (p == "0" or not p.startswith("0")) for p in manifest["version"].split(".")), f"Invalid semver version: {manifest['version']}"
    save(manifest_path, manifest)
    result = {"catalogs": len(manifest["catalogs"]),
              "before_listings": sum(map(len, original.values())),
              "after_listings": sum(map(len, selected.values())),
              "unique_sources_preserved": len(before),
              "excluded_source_groups": len(blocked),
              "duplicate_listings_removed": sum(map(len, original.values())) - len(before)}
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    deduplicate(parser.parse_args().root)

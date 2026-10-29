"""Add 10-minute solo and couples catalogs without rebuilding existing sections."""

import ast
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from check_links import probe_stream


ROOT = Path(__file__).parent
MIN_SECONDS = 10 * 60
PAGE_SIZE = 100
CATALOGS = (
    ("xfhq_long_solo", "Long Solo Videos (10 min+, 1080p+)"),
    ("xfhq_long_couples", "Long Couples Videos (10 min+, 1080p+)"),
)
COUPLE_TAGS = {
    "Couples", "AmateurCouple", "RealCouple", "Fucking",
    "Missionary", "Cowgirl", "Doggystyle",
}
# Reject titles whose age cannot safely be inferred from the source's adult label.
AGE_AMBIGUOUS = re.compile(r"(?i)\b(underage|minor|schoolgirl|schoolboy|teen|teens|young\s+girl|young\s+boy)\b")


def existing_filters():
    """Reuse the suite's actual filters without executing its destructive build."""
    source = ast.parse((ROOT / "build_full_suite.py").read_text(encoding="utf-8"))
    names = {"DISALLOWED_TAGS", "UNIVERSAL_NEGATIVE_PATTERNS", "SOLO_EXCLUSION_PATTERN"}
    nodes = [
        node for node in source.body
        if (isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        )) or (isinstance(node, ast.FunctionDef) and node.name in {"check_universal", "check_solo"})
    ]
    scope = {"re": re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "content filters", "exec"), scope)
    return scope


def load_candidates():
    # Preserve the main pool's precedence, as the full suite does.
    by_id = {
        item["id"]: item
        for item in json.loads((ROOT / "vidi.json").read_text(encoding="utf-8"))["items"]
    }
    for item in json.loads((ROOT / "vidi_all.json").read_text(encoding="utf-8"))["items"]:
        by_id.setdefault(item["id"], item)

    filters = existing_filters()
    check_universal = filters["check_universal"]
    check_solo = filters["check_solo"]
    solo = []
    couples = []
    for item in by_id.values():
        try:
            duration = float(item.get("duration") or 0)
        except (ValueError, TypeError):
            continue
        if duration < MIN_SECONDS or item.get("quality") not in {"4K", "1080p+"}:
            continue
        if AGE_AMBIGUOUS.search(item.get("name", "")):
            continue
        item_id = item["id"]
        meta_path = ROOT / "meta" / "movie" / f"{item_id}.json"
        stream_path = ROOT / "stream" / "movie" / f"{item_id}.json"
        if not meta_path.is_file() or not stream_path.is_file():
            continue
        tags = set(item.get("tags", []))
        if "Solo" in tags:
            # Solo is the explicit request. This one tag was blocked by the
            # older suite even though it is common in its solo source pool.
            filters["DISALLOWED_TAGS"].discard("masturbation")
            original_patterns = filters["UNIVERSAL_NEGATIVE_PATTERNS"]
            filters["UNIVERSAL_NEGATIVE_PATTERNS"] = [
                entry for entry in original_patterns if entry[0] != "BUBBLEBUTT_MAST"
            ]
            solo_ok = check_solo(item)[0]
            filters["UNIVERSAL_NEGATIVE_PATTERNS"] = original_patterns
            filters["DISALLOWED_TAGS"].add("masturbation")
            if solo_ok:
                solo.append(item)
                continue
        text = item.get("name", "") + " " + " ".join(tags)
        if (tags & COUPLE_TAGS or re.search(r"(?i)\bcouples?\b", text)) and check_universal(item)[0]:
            couples.append(item)
    return solo, couples


def verified(items):
    candidates = []
    for item in items:
        try:
            stream = json.loads((ROOT / "stream" / "movie" / f"{item['id']}.json").read_text(encoding="utf-8"))["streams"][0]
            url = stream.get("url", "")
            if url and not stream.get("behaviorHints", {}).get("proxyHeaders"):
                candidates.append((item, (item["id"], url, None)))
        except (KeyError, IndexError, ValueError):
            continue
    with ThreadPoolExecutor(max_workers=24) as pool:
        results = list(pool.map(probe_stream, (info for _, info in candidates)))
    accepted = []
    failure = Counter()
    for (item, _), (_, alive, status, content_type, _) in zip(candidates, results):
        if alive and not (content_type or "").lower().startswith("text/html"):
            accepted.append(item)
        else:
            failure[str(status)] += 1
    return accepted, failure


def sort_key(item):
    # Highest resolution first, then longest duration and popularity.
    return (
        0 if item.get("quality") == "4K" else 1,
        -float(item.get("duration") or 0),
        -int(item.get("likes") or 0),
    )


def write_catalog(catalog_id, items):
    catalog_dir = ROOT / "catalog" / "movie"
    page_dir = catalog_dir / catalog_id
    page_dir.mkdir(parents=True, exist_ok=True)
    metas = [
        json.loads((ROOT / "meta" / "movie" / f"{item['id']}.json").read_text(encoding="utf-8"))["meta"]
        for item in sorted(items, key=sort_key)
    ]
    for start in range(0, len(metas), PAGE_SIZE):
        target = (catalog_dir / f"{catalog_id}.json") if start == 0 else (page_dir / f"skip={start}.json")
        target.write_text(json.dumps({"metas": metas[start:start + PAGE_SIZE]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(metas)


def main():
    solo, couples = load_candidates()
    solo, solo_failures = verified(solo)
    couples, couples_failures = verified(couples)
    counts = {
        CATALOGS[0][0]: write_catalog(CATALOGS[0][0], solo),
        CATALOGS[1][0]: write_catalog(CATALOGS[1][0], couples),
    }
    if not all(counts.values()):
        raise RuntimeError("One long-video section has no reachable entries; manifest left unchanged")

    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["catalogs"] = [c for c in manifest["catalogs"] if c["id"] not in counts]
    for offset, (catalog_id, name) in enumerate(CATALOGS):
        manifest["catalogs"].insert(4 + offset, {
            "type": "movie", "id": catalog_id, "name": name,
            "extra": [{"name": "skip", "isRequired": False}],
        })
    parts = manifest["version"].split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    manifest["version"] = ".".join(parts)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"version": manifest["version"], "counts": counts,
                      "failed_probes": {CATALOGS[0][0]: dict(solo_failures), CATALOGS[1][0]: dict(couples_failures)}}, indent=2))


if __name__ == "__main__":
    main()

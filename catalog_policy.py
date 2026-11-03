"""Apply existing collection rules without retrieving or changing media."""
import hashlib
import re


def normalized_words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def excluded(text, rules):
    words = normalized_words(text)
    blocked = set(rules.get("excluded_phrase_hashes", []))
    for size in rules.get("phrase_lengths", []):
        for start in range(len(words) - size + 1):
            phrase = " ".join(words[start:start + size])
            if hashlib.sha256(phrase.encode()).hexdigest() in blocked:
                return True
    return False


def apply_policy(root, manifest, original, find, load):
    path = root / "catalog_policy.json"
    if not path.exists():
        return set()
    rules = load(path)
    blocked = set()
    # Check every alias, so a clean-looking duplicate cannot bypass exclusions.
    for path in (root / "meta").glob("*/*.json"):
        meta = load(path).get("meta", {})
        text = " ".join(str(meta.get(k, "")) for k in ("name", "description"))
        if excluded(text, rules):
            blocked.add(find((path.parent.name, path.stem)))
    for catalog in manifest["catalogs"]:
        for item in original[catalog["id"]]:
            if excluded(str(item.get("name", "")), rules):
                blocked.add(find((item.get("type", catalog["type"]), str(item["id"]))))
    for cid, ids in rules.get("additional_collections", {}).items():
        catalog = next((c for c in manifest["catalogs"] if c["id"] == cid), None)
        if catalog is None:
            catalog = {"type": "movie", "id": cid, "name": cid,
                       "extra": [{"name": "skip"}, {"name": "search"}]}
            manifest["catalogs"].append(catalog)
            original[cid] = []
        known = {str(item["id"]) for item in original[cid]}
        for ident in ids:
            path = root / "meta" / catalog["type"] / f"{ident}.json"
            if ident not in known and path.exists():
                item = load(path).get("meta")
                if item:
                    original[cid].append(item)
                    known.add(ident)
    for catalog in manifest["catalogs"]:
        catalog["name"] = rules.get("catalog_names", {}).get(catalog["id"], catalog["name"])
        original[catalog["id"]] = [m for m in original[catalog["id"]]
            if find((m.get("type", catalog["type"]), str(m["id"]))) not in blocked]
    return blocked

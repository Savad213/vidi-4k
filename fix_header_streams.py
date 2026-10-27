"""Drop catalog items whose stream only plays with a custom Referer header.

Vidi and Stremio Web/iPhone cannot send custom request headers, so a stream that
returns 403 without them shows a thumbnail but never plays. This script probes every
catalog item's stream WITHOUT headers and keeps only the ones that answer 200/206 with
media. Desi Creators and Pakistani are refilled from earlier items that did play.
"""
import ast
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

P = Path(__file__).resolve().parent
CAT = P / "catalog" / "movie"
STR = P / "stream" / "movie"
PAGE = 100
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"


def git(*a):
    return subprocess.run(["git", "-C", str(P), *a], capture_output=True, text=True, encoding="utf-8").stdout


def probe(url):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request(url, headers={"Range": "bytes=0-1023", "User-Agent": UA}), timeout=25
        )
        head = r.read(64)
        ctype = r.headers.get("Content-Type", "")
        return r.status in (200, 206) and (ctype.startswith("video") or b"ftyp" in head or "octet" in ctype)
    except Exception:
        return False


def stream_url(i):
    f = STR / f"{i}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))["streams"][0]["url"]
    except Exception:
        return None


def load_all(cid):
    metas = json.loads((CAT / f"{cid}.json").read_text(encoding="utf-8"))["metas"]
    d = CAT / cid
    if d.exists():
        for f in sorted(d.glob("skip=*.json"), key=lambda x: int(re.search(r"=(\d+)", x.name).group(1))):
            metas += json.loads(f.read_text(encoding="utf-8"))["metas"]
    return metas


def write_catalog(cid, metas, terms):
    d = CAT / cid
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    (CAT / f"{cid}.json").write_text(
        json.dumps({"metas": metas[:PAGE]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    for skip in range(PAGE, len(metas), PAGE):
        (d / f"skip={skip}.json").write_text(
            json.dumps({"metas": metas[skip : skip + PAGE]}, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    for t in terms:
        hit = [m for m in metas if t.lower() in (m["name"] + " " + " ".join(m.get("genres", []))).lower()][:PAGE]
        if hit:
            (d / f"search={t}.json").write_text(
                json.dumps({"metas": hit}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
            )


def main():
    manifest = json.loads((P / "manifest.json").read_text(encoding="utf-8"))
    src = (P / "build_full_suite.py").read_text(encoding="utf-8")
    terms = ast.literal_eval(re.search(r"COMMON_SEARCH_TERMS\s*=\s*(\[.*?\])", src, re.S).group(1))
    cids = [c["id"] for c in manifest["catalogs"]]
    cats = {c: load_all(c) for c in cids}

    # earlier items that played (last release before the overhaul) for the two Desi rows
    refill = {}
    for cid in ("xfhq_desi_creators", "xfhq_desi_pakistan"):
        try:
            refill[cid] = json.loads(git("show", f"9dd9e75d:catalog/movie/{cid}.json"))["metas"]
        except Exception:
            refill[cid] = []

    ids = {m["id"] for ms in cats.values() for m in ms} | {m["id"] for ms in refill.values() for m in ms}
    urls = {i: stream_url(i) for i in ids}
    with ThreadPoolExecutor(24) as ex:
        ok = dict(zip(urls, ex.map(lambda i: bool(urls[i]) and probe(urls[i]), urls)))

    report = {}
    for cid in cids:
        before = cats[cid]
        keep = [m for m in before if ok.get(m["id"])]
        if cid in refill:
            have = {m["id"] for m in keep}
            for m in refill[cid]:
                if ok.get(m["id"]) and m["id"] not in have:
                    keep.append(m)
                    have.add(m["id"])
        write_catalog(cid, keep, terms)
        report[cid] = {"before": len(before), "after": len(keep)}

    new_ver = sys.argv[1] if len(sys.argv) > 1 else manifest["version"]
    if re.search(r"(^|\.)0\d", new_ver):
        raise ValueError(f"CRITICAL: Invalid semver version '{new_ver}' with leading zero. Stremio rejects this!")
    manifest["version"] = new_ver
    (P / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (P / "header_fix_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

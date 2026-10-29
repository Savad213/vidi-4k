import urllib.request
import json
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Projects\vidi-4k")

with open(REPO_ROOT / "catalog/movie/xfhq_missax_4k.json", "r", encoding="utf-8") as f:
    metas = json.load(f)["metas"]

print(f"=== TESTING 100% OF MISSAX 4K VIDEOS ({len(metas)} FILMS) ===")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

passed = 0
failed = 0

for i, m in enumerate(metas):
    mid = m["id"]
    name = m["name"]
    
    # Read stream file
    s_file = REPO_ROOT / f"stream/movie/{mid}.json"
    if not s_file.exists():
        print(f"[{i+1}/{len(metas)}] [FAIL - MISSING STREAM FILE] {name}")
        failed += 1
        continue
        
    with open(s_file, "r", encoding="utf-8") as sf:
        s_data = json.load(sf)
        streams = s_data.get("streams", [])
        
    if not streams or not streams[0].get("url"):
        print(f"[{i+1}/{len(metas)}] [FAIL - NO URL] {name}")
        failed += 1
        continue
        
    url = streams[0]["url"]
    
    # Test range request for live bytes
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Range': 'bytes=0-65535'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            chunk = resp.read()
            status = resp.status
            if status in (200, 206) and len(chunk) > 0:
                print(f"[{i+1}/{len(metas)}] [PASS {status}] {name} -> Read {len(chunk)} bytes from {resp.url[:45]}...")
                passed += 1
            else:
                print(f"[{i+1}/{len(metas)}] [FAIL STATUS {status}] {name}")
                failed += 1
    except Exception as e:
        print(f"[{i+1}/{len(metas)}] [FAIL EXCEPTION] {name}: {e}")
        failed += 1

print(f"\nFINAL VERIFICATION RESULTS: {passed}/{len(metas)} PASSED, {failed} FAILED")

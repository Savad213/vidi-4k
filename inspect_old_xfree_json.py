import json, os

p = r"C:\Users\SM.DESKTOP-P1R0508.000\Desktop\DESKTOP\StremioPowerSetup\xfree-hq\xfree_hq.json"
if os.path.exists(p):
    data = json.load(open(p, "r", encoding="utf-8"))
    print("Keys:", data.keys())
    posts = data.get("posts", {})
    print(f"Total posts in xfree_hq.json: {len(posts)}")
    # Look at 2 sample posts
    first_key = list(posts.keys())[0]
    print("Sample post:", json.dumps(posts[first_key], indent=2))
else:
    print("File not found")

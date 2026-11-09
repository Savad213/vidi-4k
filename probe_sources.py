import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
            pages = re.findall(r'/page/(\d+)/?', html)
            page_nums = [int(p) for p in pages]
            max_p = max(page_nums) if page_nums else 1
            if 'mastiraja.tv' in url:
                links = re.findall(r'href=["\'](https://mastiraja\.tv/[a-zA-Z0-9\-]+/)["\']', html)
                valid = [l for l in links if not any(x in l for x in ['/category/', '/tag/', '/author/', '/page/', '/wp-', '/feed/'])]
            else:
                links = re.findall(r'href=["\'](https://fsiblog\.co\.im/watch/[^"\'?#]+)', html)
                valid = links
            print(f"{url} -> HTTP {r.status} | Found {len(valid)} video links | Max visible page: {max_p}")
    except Exception as e:
        print(f"{url} -> Error: {e}")

if __name__ == '__main__':
    print("--- Mastiraja Checks ---")
    check('https://mastiraja.tv/category/pakistani-sex/')
    check('https://mastiraja.tv/category/pakistani-sex/page/10/')
    check('https://mastiraja.tv/category/pakistani-sex/page/25/')
    check('https://mastiraja.tv/category/viral-leaks/')
    check('https://mastiraja.tv/category/viral-leaks/page/10/')
    check('https://mastiraja.tv/category/viral-leaks/page/25/')
    check('https://mastiraja.tv/category/viral-leaks/page/50/')
    check('https://mastiraja.tv/tag/pakistani/')
    check('https://mastiraja.tv/tag/mms/')

    print("\n--- FSIBlog Checks ---")
    check('https://fsiblog.co.im/tag/pakistani/')
    check('https://fsiblog.co.im/tag/pakistani-mms/')
    check('https://fsiblog.co.im/tag/viral-leaks/')
    check('https://fsiblog.co.im/tag/viral-leaks/page/10')
    check('https://fsiblog.co.im/tag/viral-leaks/page/25')
    check('https://fsiblog.co.im/tag/desi-mms/page/10')
    check('https://fsiblog.co.im/tag/desi-mms/page/25')

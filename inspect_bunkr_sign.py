import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://dl.bunkr.cr/file/31777725", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
h = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')

idx = h.find('SIGN_SERVICE_URL')
print(h[idx:idx+1500])

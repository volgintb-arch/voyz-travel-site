"""The phone version is the website itself (assets/mobile.css). This script only keeps the old /app/ links alive:
it replaces the former app with a tiny redirect page and removes the app files.  Run after build_site.py:  python build_app.py"""
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
STUB = ('<!doctype html><html><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>VOYZ</title>'
        '<script>var h=location.hash,m=h.match(/^#\\/tour\\/([\\w-]+)/);location.replace(m?"../tours/"+m[1]+"/":/^#\\/tours/.test(h)?"../tours/":"../")</script>'
        '<noscript><meta http-equiv="refresh" content="0;url=../"></noscript></head><body></body></html>')
for d in ('app', 'en/app'):
    for f in ('app.js', 'app.css'):
        p = os.path.join(ROOT, d, f)
        if os.path.exists(p): os.remove(p)
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    open(os.path.join(ROOT, d, 'index.html'), 'w', encoding='utf-8').write(STUB)
print('old app links redirect to the website')

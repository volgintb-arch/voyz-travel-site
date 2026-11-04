"""Builds app/index.html (mobile app, iOS style) from the same data as the website.
Run after build_site.py:  python build_app.py"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
base, extra = load('data/tours.json'), load('data/tours_extra.json')
tours = base['tours'] + extra['tours']
for t in tours:
    t.setdefault('organization_note', extra['defaults']['organization_note'])
    if t['slug'] != 'grand-expedition': t['faq'] = t['faq'] + extra['defaults']['faq_common']
keep = ['slug', 'badge', 'title', 'headline', 'card_title', 'summary', 'hero', 'hero_pos', 'card_img', 'season', 'months', 'seasons', 'facts', 'lakes', 'days',
        'fit_yes', 'fit_no', 'difficulty', 'difficulty_note', 'organization', 'organization_note', 'faq', 'map']
data = [{k: t[k] for k in keep if k in t} for t in tours]
html = '''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#F2F2F7" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="VOYZ"><meta name="apple-mobile-web-app-status-bar-style" content="default">
<title>VOYZ — туры по Кыргызстану</title><meta name="description" content="Приложение VOYZ: туры на внедорожниках по Кыргызстану на весь год.">
<script>(function(){try{if(/[?&]preview/.test(location.search)||matchMedia("(max-width:1024px)").matches)return;var h=location.hash,m=h.match(/^#\\/tour\\/([\\w-]+)/);location.replace(m?"../tours/"+m[1]+"/":/^#\\/tours/.test(h)?"../tours/":"../")}catch(e){}})()</script>
<link rel="stylesheet" href="app.css"></head><body><div class="phone"></div>
<script>window.VOYZ={tours:%s}</script><script src="../assets/config.js"></script><script src="app.js"></script></body></html>''' % json.dumps(data, ensure_ascii=False, separators=(',', ':'))
os.makedirs(os.path.join(ROOT, 'app'), exist_ok=True)
open(os.path.join(ROOT, 'app/index.html'), 'w', encoding='utf-8').write(html)

# phones opening the website are sent to the app (they can opt out with "Полная версия")
redirect = ('<script>(function(){try{if(sessionStorage.getItem("voyz_full")||/[?&]full=1/.test(location.search))return;'
            'if(matchMedia("(max-width:1024px)").matches){var p=location.pathname.replace(/index\\.html$/,""),m=p.match(/tours\\/([^\\/]+)\\/$/),'
            'h=m&&m[1]!=="privacy"?"#/tour/"+m[1]:/tours\\/$/.test(p)?"#/tours":"";'
            'if(/privacy|credits/.test(p))return;'
            'var base=m?"../../":/tours\\/$/.test(p)?"../":"";location.replace(base+"app/"+h)}}catch(e){}})()</script>')
for rel in ['index.html', 'tours/index.html'] + ['tours/%s/index.html' % t['slug'] for t in tours]:
    p = os.path.join(ROOT, rel); s = open(p, encoding='utf-8').read()
    if 'voyz_full' not in s:
        s = s.replace('<title>', redirect + '<title>', 1); open(p, 'w', encoding='utf-8').write(s)
print('app built:', len(data), 'tours,', round(os.path.getsize(os.path.join(ROOT, 'app/index.html')) / 1e3), 'KB')

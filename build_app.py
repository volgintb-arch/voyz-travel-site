"""Builds the mobile app pages: app/index.html (RU) and en/app/index.html (EN), from the same data as the website.
Also inserts the phone/tablet redirect into every website page.  Run after build_site.py:  python build_app.py"""
import json, os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
def read(p): return open(os.path.join(ROOT, p), encoding='utf-8').read()
def write(p, s):
    f = os.path.join(ROOT, p); os.makedirs(os.path.dirname(f), exist_ok=True); open(f, 'w', encoding='utf-8').write(s)

SITE_URL = re.search(r"SITE_URL = '([^']+)'", read('build_site.py')).group(1)
base, extra, EN = load('data/tours.json'), load('data/tours_extra.json'), load('data/en.json')
tours = base['tours'] + extra['tours']
for t in tours:
    t.setdefault('organization_note', extra['defaults']['organization_note'])
    if t['slug'] != 'grand-expedition': t['faq'] = t['faq'] + extra['defaults']['faq_common']
keep = ['slug', 'badge', 'title', 'headline', 'card_title', 'summary', 'hero', 'hero_pos', 'card_img', 'season', 'months', 'seasons', 'facts', 'lakes', 'days',
        'points', 'fit_yes', 'fit_no', 'difficulty', 'difficulty_note', 'organization', 'organization_note', 'faq', 'map']
data = [{k: t[k] for k in keep if k in t} for t in tours]
CYR = re.compile('[А-Яа-яЁё]')
def tr(o):
    if isinstance(o, str): return EN.get(o, o) if CYR.search(o) else o
    if isinstance(o, list): return [tr(x) for x in o]
    if isinstance(o, dict): return {k: tr(v) for k, v in o.items()}
    return o

app_ui = {}
need = load('data/en_app_need.json')
for line in open(os.path.join(ROOT, 'data/en_app.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if line: i, _, v = line.partition('|'); app_ui[need[int(i)]] = v
UI = dict(EN); UI.update(app_ui)

PAGE = '''<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<script>(function(){try{if(/[?&]preview/.test(location.search)||matchMedia("(max-width:1024px)").matches)return;var h=location.hash,m=h.match(/^#\\/tour\\/([\\w-]+)/);location.replace(m?"../tours/"+m[1]+"/":/^#\\/tours/.test(h)?"../tours/":"../")}catch(e){}})()</script>
<meta name="robots" content="noindex,follow"><link rel="canonical" href="%(canon)s">
<meta name="theme-color" content="#F2F2F7" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="VOYZ"><meta name="apple-mobile-web-app-status-bar-style" content="default">
<title>%(title)s</title><meta name="description" content="%(desc)s">
<meta property="og:title" content="%(title)s"><meta property="og:description" content="%(desc)s"><meta property="og:type" content="website"><meta property="og:image" content="%(site)s/assets/og/home-%(lang)s.jpg">
<link rel="icon" href="%(up)sfavicon.ico" sizes="48x48"><link rel="icon" href="%(up)sfavicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="%(up)sassets/icons/apple-touch-icon.png"><link rel="manifest" href="%(up)ssite.webmanifest">
<link rel="stylesheet" href="app.css?v=%(ver)s"></head><body><div class="phone"></div>
<script>window.VOYZ={tours:%(data)s};window.VOYZ_UI=%(ui)s</script><script src="%(up)sassets/config.js?v=%(ver)s"></script><script src="%(up)sassets/jeep.js?v=%(ver)s"></script><script src="app.js?v=%(ver)s"></script></body></html>'''

VER = str(int(__import__('time').time()))
css, js = read('app/app.css'), read('app/app.js')
# --- Russian app (app/)
write('app/index.html', PAGE % dict(lang='ru', canon=SITE_URL + '/', title='VOYZ — туры по Кыргызстану на внедорожниках', desc='Мобильная версия сайта VOYZ: туры на внедорожниках по Кыргызстану на весь год.',
      site=SITE_URL, up='../', ver=VER, data=json.dumps(data, ensure_ascii=False, separators=(',', ':')), ui='{}'))
# --- English app (en/app/): same code, asset paths one level deeper, data + UI translated
write('en/app/app.css', css.replace('../assets/', '../../assets/'))
write('en/app/app.js', js.replace('../assets/', '../../assets/'))
write('en/app/index.html', PAGE % dict(lang='en', canon=SITE_URL + '/en/', title='VOYZ — 4x4 tours in Kyrgyzstan', desc='The VOYZ mobile website: 4x4 tours across Kyrgyzstan all year round.',
      site=SITE_URL, up='../../', ver=VER, data=json.dumps(tr(data), ensure_ascii=False, separators=(',', ':')), ui=json.dumps(UI, ensure_ascii=False, separators=(',', ':'))))

# --- phone/tablet redirect for every website page (crawlers and link-preview bots are never redirected)
BOT = 'bot|crawl|spider|slurp|yandex|bing|duckduck|baidu|facebookexternalhit|twitter|telegram|whatsapp|vkshare|viber|skype|preview|lighthouse'
def redirect(depth, en, hash_):
    tgt = '../' * depth + ('en/' if en else '') + 'app/' + hash_
    return ('<script>(function(){try{if(sessionStorage.getItem("voyz_full")||/[?&]full=1/.test(location.search))return;'
            'if(/%s/i.test(navigator.userAgent))return;if(matchMedia("(max-width:1024px)").matches)location.replace("%s")}catch(e){}})()</script>' % (BOT, tgt))
pages = [('index.html', 0, ''), ('tours/index.html', 1, '#/tours')] + [('tours/%s/index.html' % t['slug'], 2, '#/tour/' + t['slug']) for t in tours]
for rel, depth, h in pages:
    for en in (False, True):
        p = ('en/' if en else '') + rel; s = read(p)
        # site pages inside en/ are one folder deeper than their RU twins
        s = s.replace('<title>', redirect(depth + (1 if en else 0), en, h) + '<title>', 1)
        write(p, s)
print('app built (ru + en):', len(data), 'tours;', round(os.path.getsize(os.path.join(ROOT, 'en/app/index.html')) / 1e3), 'KB')

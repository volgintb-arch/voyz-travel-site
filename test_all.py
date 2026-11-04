import json, re, sys, urllib.request
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright
B = 'http://localhost:8765'
CYR = re.compile('[А-Яа-яЁё]')
paths = ['', 'tours/', 'privacy/', 'credits/'] + ['tours/%s/' % s for s in ('grand-expedition', 'put-karavanov', 'krysha-mira', 'sary-chelek', 'vesna-issyk-kul', 'osen-son-kul', 'zima-issyk-kul')]
problems = []
def bad(msg): problems.append(msg); print('  !!', msg)

with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    # ---------- 1. SEO tags on every page, both languages
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    for lang in ('', 'en/'):
        for path in paths:
            url = '%s/%s%s' % (B, lang, path); r = pg.goto(url, wait_until='networkidle')
            info = pg.evaluate('''() => { const q = s => document.querySelector(s), m = (n, a='name') => (q(`meta[${a}="${n}"]`)||{}).content;
              return {status: 0, lang: document.documentElement.lang, title: document.title, desc: m('description'), canon: (q('link[rel=canonical]')||{}).href, robots: m('robots'),
              hreflang: [...document.querySelectorAll('link[rel=alternate][hreflang]')].map(l => l.hreflang), ogt: m('og:title','property'), ogd: m('og:description','property'), ogi: m('og:image','property'), ogu: m('og:url','property'), ogl: m('og:locale','property'),
              twc: m('twitter:card'), twi: m('twitter:image'), h1: document.querySelectorAll('h1').length, icons: [...document.querySelectorAll('link[rel~=icon],link[rel=apple-touch-icon],link[rel=manifest]')].map(l=>l.getAttribute('href')),
              ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { const j = JSON.parse(s.textContent); return (j['@graph']||[j]).map(x=>x['@type']) } catch(e) { return 'INVALID' } }),
              visible: document.body.innerText}}''')
            tag = '%s%s' % (lang, path or '(home)')
            if not r.ok: bad('%s HTTP %s' % (tag, r.status))
            if info['lang'] != ('en' if lang else 'ru'): bad('%s html lang=%s' % (tag, info['lang']))
            for k in ('title', 'desc', 'canon', 'ogt', 'ogd', 'ogi', 'ogu', 'twc', 'twi'):
                if not info[k]: bad('%s missing %s' % (tag, k))
            if sorted(info['hreflang']) != ['en', 'ru', 'x-default']: bad('%s hreflang %s' % (tag, info['hreflang']))
            if info['h1'] != 1: bad('%s has %d <h1>' % (tag, info['h1']))
            if 'INVALID' in str(info['ld']) or not info['ld']: bad('%s JSON-LD problem %s' % (tag, info['ld']))
            if len(info['title']) > 75: bad('%s title long (%d)' % (tag, len(info['title'])))
            if info['desc'] and len(info['desc']) > 200: bad('%s description long (%d)' % (tag, len(info['desc'])))
            if lang and CYR.search(info['visible']): bad('%s visible Cyrillic: %s' % (tag, CYR.search(info['visible']).group(0) + '…' + info['visible'][max(0, CYR.search(info['visible']).start() - 30):CYR.search(info['visible']).start() + 40].replace('\n', ' ')))
            if lang and (CYR.search(info['title']) or CYR.search(info['desc'] or '') or CYR.search(info['ogt'] or '')): bad('%s Cyrillic in meta' % tag)
            if path == '' and lang == '': print('  home sample:', info['title'], '|', info['canon'], '|', info['ogl'], '|', info['ld'])
    if errs: bad('JS errors: %s' % errs[:3])
    # asset links resolve
    for href in ('/favicon.ico', '/favicon.svg', '/assets/icons/apple-touch-icon.png', '/site.webmanifest', '/assets/og/home-en.jpg', '/sitemap.xml', '/robots.txt', '/404.html'):
        try: urllib.request.urlopen(B + href, timeout=10)
        except Exception as e: bad('asset %s -> %s' % (href, e))
    # ---------- 2. sitemap
    root = ET.fromstring(urllib.request.urlopen(B + '/sitemap.xml').read()); ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    locs = [u.find('s:loc', ns).text for u in root.findall('s:url', ns)]
    print('  sitemap urls:', len(locs), '| expected', 2 * len(paths))
    if len(locs) != 2 * len(paths): bad('sitemap count')
    # ---------- 3. redirects: phone -> app (right language), bots stay, desktop stays
    mob = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    for u, want in (('/', '/app/'), ('/tours/zima-issyk-kul/', '/app/#/tour/zima-issyk-kul'), ('/en/', '/en/app/'), ('/en/tours/', '/en/app/#/tours'), ('/en/tours/krysha-mira/', '/en/app/#/tour/krysha-mira')):
        q = mob.new_page(); q.goto(B + u, wait_until='networkidle'); q.wait_for_timeout(600)
        got = q.url.replace(B, ''); print('  phone %-26s -> %s' % (u, got))
        if got != want: bad('redirect %s -> %s (wanted %s)' % (u, got, want))
        q.close()
    bot = b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, user_agent='Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
    q = bot.new_page(); q.goto(B + '/', wait_until='networkidle'); q.wait_for_timeout(600)
    print('  Googlebot-mobile stays on:', q.url.replace(B, ''));
    if '/app' in q.url: bad('bot redirected into the app')
    # ---------- 4. English app: no Cyrillic after exploring every screen
    ap = mob.new_page(); ap.goto(B + '/en/app/', wait_until='networkidle'); ap.wait_for_timeout(1500); seen = []
    def scan(label):
        t = ap.evaluate("document.querySelector('.phone').innerText + ' ' + [...document.querySelectorAll('[placeholder],[aria-label],[alt]')].map(e => (e.placeholder||'')+' '+(e.getAttribute('aria-label')||'')+' '+(e.alt||'')).join(' ')")
        m = CYR.search(t)
        if m: bad('EN app %s: Cyrillic near "%s"' % (label, t[max(0, m.start() - 30):m.start() + 40].replace('\n', ' ')))
    scan('home'); ap.goto(B + '/en/app/#/tours'); ap.wait_for_timeout(700); scan('tours')
    ap.click('.seg button[data-v=winter]'); ap.wait_for_timeout(500); scan('tours/winter')
    ap.goto(B + '/en/app/#/calendar'); ap.wait_for_timeout(700); scan('calendar'); ap.click('.mon[data-m="1"]'); ap.wait_for_timeout(400); scan('calendar/Jan')
    ap.goto(B + '/en/app/#/request'); ap.wait_for_timeout(700); scan('request')
    ap.click('form[data-form] button[type=submit]'); ap.wait_for_timeout(500); scan('request/validation')
    ap.goto(B + '/en/app/#/tour/grand-expedition'); ap.wait_for_timeout(1500); scan('tour')
    ap.click('.cta .btn'); ap.wait_for_timeout(900); scan('sheet')
    ap.fill('.sheet input[name=name]', 'Test'); ap.fill('.sheet input[name=contact]', '@t'); ap.click('.sheet [data-toggle]'); ap.click('.sheet button[type=submit]'); ap.wait_for_timeout(700); scan('sheet/sent')
    print('  EN app screens scanned')
    # ---------- 5. vertical rhythm: gaps between consecutive sections on desktop
    d = ctx.new_page(); d.goto(B + '/', wait_until='networkidle'); d.wait_for_timeout(1200)
    gaps = d.evaluate('''() => { const s = [...document.querySelectorAll('section')]; return s.map(e => { const c = getComputedStyle(e), r = e.getBoundingClientRect(); return [e.id || e.className.split(' ').slice(0,2).join('.'), Math.round(r.height), c.paddingTop, c.paddingBottom, c.backgroundColor] }) }''')
    for g in gaps: print('   ', g)
    adj = [(gaps[i][0], gaps[i + 1][0]) for i in range(len(gaps) - 1) if gaps[i][4] == gaps[i + 1][4] and gaps[i][4] != 'rgba(0, 0, 0, 0)' and 'hero' not in gaps[i + 1][0]]
    print('  adjacent sections with the same background:', adj)
    if adj: bad('same-background neighbours: %s' % adj)
    b.close()
print('\nPROBLEMS:', len(problems)); [print(' -', x) for x in problems]

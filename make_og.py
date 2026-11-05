"""Open Graph / Twitter share images (1200x630) for every page and language.
Run: python make_og.py   (after changing tour titles or photos)"""
import json, os, io, html, pathlib
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
base, extra, EN = load('data/tours.json'), load('data/tours_extra.json'), load('data/en.json')
tours = base['tours'] + extra['tours']
logo = open(os.path.join(ROOT, 'assets/logo.svg'), encoding='utf-8').read().replace('<svg ', '<svg style="height:40px;width:auto" ', 1)
OUT = os.path.join(ROOT, 'assets/og'); os.makedirs(OUT, exist_ok=True)

OVR = {'Туда, куда не доезжает автобус': 'Go where no bus goes', 'Наши туры': 'Our tours',
       'Авторские туры на внедорожниках · небольшие группы · на весь год': 'Authentic 4x4 tours · small groups · all year round',
       'Весна, лето, осень и зима · Кыргызстан на внедорожниках': 'Spring, summer, autumn and winter · Kyrgyzstan by 4x4'}
def tr(lang, s): return (OVR.get(s) or EN.get(s, s)) if lang == 'en' else s
items = [('home', 'alakul', 'Туда, куда не доезжает автобус', 'Экспедиции по Кыргызстану', 'Авторские туры на внедорожниках · небольшие группы · на весь год'),
         ('tours', 'kelsuu', 'Наши туры', 'Каталог', 'Весна, лето, осень и зима · Кыргызстан на внедорожниках')]
for t in tours:
    n = t['days'][-1]['n']
    items.append((t['slug'], t['hero'], t['title'], t['badge'], '%s %s · %s · %s' % (n, 'дней', t['facts'][1][0] + ' ' + t['facts'][1][1], t['season'])))

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:U;src:url('assets/fonts/Unbounded-Black.ttf');font-weight:900}
@font-face{font-family:U;src:url('assets/fonts/Unbounded-Bold.ttf');font-weight:700}
*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;position:relative;overflow:hidden;background:#0B0B0B;font-family:system-ui,'Segoe UI',sans-serif;color:#fff}
.bg{position:absolute;inset:0;background:url('%(img)s') center/cover}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%%,rgba(0,0,0,.05) 38%%,rgba(0,0,0,.82) 100%%)}
.logo{position:absolute;left:56px;top:48px;color:#fff;line-height:0}.logo svg{fill:#fff}
.tag{position:absolute;right:56px;top:48px;background:#D8FC00;color:#000;font:700 22px/1 U;text-transform:uppercase;padding:14px 22px 12px;border-radius:99px}
.t{position:absolute;left:56px;right:56px;bottom:112px;font:900 %(fs)spx/1.02 U;text-transform:uppercase;letter-spacing:-.01em}
.s{position:absolute;left:56px;right:56px;bottom:50px;font:600 28px/1.2 system-ui,'Segoe UI',sans-serif;color:rgba(255,255,255,.88)}
.s:before{content:"";display:inline-block;width:46px;height:6px;border-radius:3px;background:#D8FC00;margin-right:18px;vertical-align:middle}
</style></head><body><div class="bg"></div><div class="sh"></div><div class="logo">%(logo)s</div><div class="tag">%(tag)s</div><div class="t">%(title)s</div><div class="s">%(sub)s</div></body></html>'''

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 630})
    for key, imgk, title, tag, sub in items:
        for lang in ('ru', 'en'):
            tt, tg = tr(lang, title), tr(lang, tag)
            if key not in ('home', 'tours'):
                n = [t for t in tours if t['slug'] == key][0]['days'][-1]['n']
                sb = '%s %s · %s · %s' % (n, 'days' if lang == 'en' else 'дней', tr(lang, tours[[t['slug'] for t in tours].index(key)]['facts'][1][0] + ' ' + tours[[t['slug'] for t in tours].index(key)]['facts'][1][1]), tr(lang, tours[[t['slug'] for t in tours].index(key)]['season']))
            else: sb = tr(lang, sub)
            fs = 84 if len(tt) < 22 else 66 if len(tt) < 34 else 56
            doc = TPL % dict(img='assets/img/%s-l.webp' % imgk, logo=logo, tag=html.escape(tg), title=html.escape(tt), sub=html.escape(sb), fs=fs)
            f = os.path.join(ROOT, '_og.html'); open(f, 'w', encoding='utf-8').write(doc)
            pg.goto(pathlib.Path(f).as_uri()); pg.wait_for_timeout(500)
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
            im.save(os.path.join(OUT, '%s-%s.jpg' % (key, lang)), quality=86, optimize=True)
    b.close()
os.remove(os.path.join(ROOT, '_og.html'))
print(len(os.listdir(OUT)), 'share images,', round(sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) / 1e6, 1), 'MB')

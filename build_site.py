"""Static site generator: data/*.json -> plain HTML pages (RU at /, EN at /en/).
Run: python build_site.py      (then: python build_app.py, python make_og.py if titles changed)

Languages: the site is written in Russian; English comes from data/en.json (Russian string -> English string),
applied to the generated HTML, so one template serves both languages.
SEO: canonical + hreflang (ru, en, x-default), Open Graph / Twitter cards, JSON-LD, sitemap.xml, robots.txt, manifest."""
import json, os, html, re, datetime

H = html.escape
ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------------- launch settings (change these when the real domain goes live) ----------------
SITE_URL = 'https://volgintb-arch.github.io/voyz-travel-site'   # no trailing slash; e.g. 'https://voyz.ru'
INDEXABLE = False        # False = preview: pages carry noindex. Set True when the site is ready for search engines.
VERIFY = {'google-site-verification': '', 'yandex-verification': '', 'msvalidate.01': ''}   # paste verification codes here
BRAND = 'VOYZ Travel'
TODAY = datetime.date.today().isoformat()
VER = str(int(__import__('time').time()))   # cache-busting suffix for css/js, new on every build

def load(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
BASE, EXTRA, CR = load('data/tours.json'), load('data/tours_extra.json'), load('data/credits.json')
EN_PATH = os.path.join(ROOT, 'data/en.json')
EN = load('data/en.json') if os.path.exists(EN_PATH) else {}
HAS_EN = os.path.exists(EN_PATH)
DEF = EXTRA['defaults']
TOURS = BASE['tours'] + EXTRA['tours']
for t in TOURS:
    t.setdefault('organization_note', DEF['organization_note'])
    if t['slug'] != 'grand-expedition': t['faq'] = t['faq'] + DEF['faq_common']
G = TOURS[0]                       # flagship tour (home hero, map)
MONTHS = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
SEASONS = [('spring', 'Весна'), ('summer', 'Лето'), ('autumn', 'Осень'), ('winter', 'Зима')]

# per-build state (set in build())
LANG, PFX, CUR = 'ru', '', {'path': '', 'og': 'home', 'ld': []}

def img(k, size='l', root=''): return '%sassets/img/%s-%s.webp' % (root, k, size)
def tour_url(t, root): return '%s%stours/%s/' % (root, PFX, t['slug'])
def rootfor(depth): return '../' * (depth + (1 if LANG == 'en' else 0))
def tt(s): return EN.get(s, s) if LANG == 'en' else s        # translate a plain string at build time

# ---------------- <head>: meta, social, structured data ----------------
def page_url(lang, path): return '%s/%s%s' % (SITE_URL, 'en/' if lang == 'en' else '', path)

def org_ld():
    return {"@type": "TravelAgency", "@id": SITE_URL + "/#org", "name": BRAND, "url": SITE_URL + "/",
            "logo": SITE_URL + "/assets/icons/icon-512.png", "image": SITE_URL + "/assets/og/home-%s.jpg" % LANG,
            "description": tt('Авторские путешествия по Кыргызстану на внедорожниках. Небольшие группы, продуманные маршруты, поездки в любое время года.'),
            "areaServed": [{"@type": "Country", "name": "Kyrgyzstan"}, {"@type": "Place", "name": "Europe"}, {"@type": "Place", "name": "Asia"}],
            "knowsLanguage": ["ru", "en"], "slogan": tt('Кыргызстан. За пределами привычного.')}

def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def head(title, desc, root, extra_ld=None, keywords=''):
    path, ogk = CUR['path'], CUR['og']
    url = page_url(LANG, path)
    og_img = '%s/assets/og/%s-%s.jpg' % (SITE_URL, ogk, LANG)
    robots = ('index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1' if INDEXABLE else 'noindex,nofollow')
    ld = {"@context": "https://schema.org", "@graph": [org_ld(), {"@type": "WebSite", "@id": SITE_URL + "/#site", "url": SITE_URL + "/", "name": BRAND, "inLanguage": LANG, "publisher": {"@id": SITE_URL + "/#org"}}] + (extra_ld or [])}
    verify = ''.join(f'<meta name="{k}" content="{v}">' for k, v in VERIFY.items() if v)
    loc, alt = ('ru_RU', 'en_US') if LANG == 'ru' else ('en_US', 'ru_RU')
    kw = f'<meta name="keywords" content="{H(keywords)}">' if keywords else ''
    return f'''<!doctype html><html lang="{LANG}" prefix="og: https://ogp.me/ns#"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{H(title)}</title><meta name="description" content="{H(desc)}">{kw}
<meta name="robots" content="{robots}"><meta name="googlebot" content="{robots}"><meta name="author" content="{BRAND}"><meta name="format-detection" content="telephone=no">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ru" href="{page_url('ru', path)}"><link rel="alternate" hreflang="en" href="{page_url('en', path)}"><link rel="alternate" hreflang="x-default" href="{page_url('en', path)}">
<meta property="og:site_name" content="{BRAND}"><meta property="og:type" content="website"><meta property="og:title" content="{H(title)}"><meta property="og:description" content="{H(desc)}">
<meta property="og:url" content="{url}"><meta property="og:locale" content="{loc}"><meta property="og:locale:alternate" content="{alt}">
<meta property="og:image" content="{og_img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{H(title)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{H(title)}"><meta name="twitter:description" content="{H(desc)}"><meta name="twitter:image" content="{og_img}"><meta name="twitter:image:alt" content="{H(title)}">
<meta name="theme-color" content="#0B0B0B"><meta name="application-name" content="{BRAND}"><meta name="apple-mobile-web-app-title" content="VOYZ">{verify}
<link rel="icon" href="{root}favicon.ico" sizes="48x48"><link rel="icon" href="{root}favicon.svg" type="image/svg+xml"><link rel="icon" href="{root}assets/icons/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{root}assets/icons/apple-touch-icon.png"><link rel="manifest" href="{root}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mulish:wght@500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css?v={VER}"><link rel="stylesheet" href="{root}assets/v2.css?v={VER}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head><body>'''

def lang_switch(root):
    p = CUR['path']
    base = '../' * (len([x for x in p.split('/') if x]) + (1 if LANG == 'en' else 0))
    ru, en = base + p, base + 'en/' + p
    return f'<span class="lang" role="group" aria-label="Language"><a href="{ru or "./"}" hreflang="ru" lang="ru"{" aria-current=true" if LANG == "ru" else ""}>RU</a><a href="{en}" hreflang="en" lang="en"{" aria-current=true" if LANG == "en" else ""}>EN</a></span>'

def header(root, cur=''):
    nav = [('tours/', 'Туры'), ('#year', 'Туры на весь год'), ('#faq', 'Вопросы')]
    def href(h): return root + PFX + h if h == 'tours/' else (h if cur == 'home' else root + PFX + 'index.html' + h)
    links = ''.join(f'<a href="{href(h)}"{" aria-current=page" if (cur == "tours" and h == "tours/") else ""}>{t}</a>' for h, t in nav)
    sw = lang_switch(root)
    return f'''<header class="hdr"><div class="wrap"><a class="logo-link" href="{root}{PFX}index.html" aria-label="VOYZ Travel"><img src="{root}assets/logo.svg" alt="VOYZ" width="118" height="16"></a>
<nav class="nav" aria-label="Основное">{links}{sw}<a class="btn sm" href="#request" data-open-form="header">Подобрать тур</a></nav>
<button class="burger" data-menu aria-label="Меню"><span></span></button></div></header>
<div class="mnav" role="dialog" aria-label="Меню"><button class="x" data-menu aria-label="Закрыть">×</button>{links}{sw}<a href="#request" data-open-form="menu" style="color:var(--lime)">Оставить заявку</a></div>'''

def form(tour_name='', idp='f', source='page', root=''):
    months = ''.join(f'<option>{m}</option>' for m in ['Весна', 'Лето', 'Осень', 'Зима', 'Пока не знаю'])
    people = ''.join(f'<option>{p}</option>' for p in ['1', '2', '3', '4', '5', '6', '7', '8', 'Больше 8'])
    return f'''<form class="form" data-request data-tour="{H(tour_name)}" data-source="{source}" novalidate>
<div class="fields" style="display:flex;flex-direction:column;gap:16px">
<div class="two"><div class="field"><label for="{idp}n">Как вас зовут</label><input id="{idp}n" name="name" autocomplete="name" placeholder="Имя" required></div>
<div class="field"><label for="{idp}c">Как с вами связаться</label><input id="{idp}c" name="contact" autocomplete="tel" placeholder="Telegram, телефон или почта" required></div></div>
<div class="two"><div class="field"><label for="{idp}m">Когда хотите поехать</label><select id="{idp}m" name="month"><option value="">Выберите сезон</option>{months}</select></div>
<div class="field"><label for="{idp}p">Сколько вас человек</label><select id="{idp}p" name="people"><option value="">Выберите</option>{people}</select></div></div>
<div class="field"><label for="{idp}t">Пожелания</label><textarea id="{idp}t" name="comment" placeholder="Что важно для вас в поездке: опыт, дети, сроки, вопросы"></textarea></div>
<label class="consent"><input type="checkbox" name="consent" required><span>Согласен на обработку персональных данных и с <a href="{root}{PFX}privacy/">политикой конфиденциальности</a></span></label>
<button class="btn" type="submit">Получить программу и расчёт <span class="arrow">→</span></button>
</div><div class="ok" role="status"></div></form>'''

def modal(root, tour=''):
    return f'''<div class="modal" role="dialog" aria-modal="true" aria-label="Заявка"><div class="box"><button class="close" aria-label="Закрыть">×</button>
<p class="tag" style="margin-bottom:18px">Заявка</p><h2 class="h2" style="font-size:clamp(26px,calc(3.4*var(--vw)),40px);margin-bottom:12px">Расскажем всё <span class="hl">и посчитаем</span></h2>
<p class="body dim" style="margin-bottom:24px">Оставьте контакты — вернёмся с программой и расчётом под вашу группу и даты.</p>{form(tour, 'm', 'modal', root)}</div></div>'''

def mbar(label='Оставить заявку'): return f'<div class="mbar"><a class="btn" href="#request" data-open-form="mobile-bar">{label}</a></div>'

def footer(root, modal_html='', mbar_html=''):
    links = ''.join(f'<li><a href="{tour_url(t, root)}">{H(t["title"])}</a></li>' for t in TOURS)
    return f'''<footer class="ftr"><div class="wrap"><div class="cols">
<div><div class="logo-lg"><img src="{root}assets/logo.svg" alt="VOYZ" width="220" height="29"></div>
<p class="body dim" style="margin-top:20px;max-width:26em">Авторские путешествия по Кыргызстану на внедорожниках. Небольшие группы, продуманные маршруты и честный разговор о том, что вас ждёт.</p></div>
<div><p class="meta dim">Туры</p><ul>{links}<li><a href="{root}{PFX}tours/">Все туры</a></li></ul></div>
<div><p class="meta dim">Связаться</p><ul><li><a href="#request" data-open-form="footer">Оставить заявку</a></li>
<li><a data-contact="telegram" hidden>Telegram</a></li><li><a data-contact="whatsapp" hidden>WhatsApp</a></li><li><a data-contact="phone" hidden>Позвонить</a></li><li><a data-contact="email" hidden>Написать на почту</a></li>
<li><a href="https://voyz.ru" rel="noopener">voyz.ru</a></li></ul></div></div>
<div class="bot meta dim"><span>© VOYZ Travel</span><span><a href="{root}{PFX}privacy/">Политика конфиденциальности</a></span></div></div></footer>
{modal_html}{mbar_html}<script src="{root}assets/config.js?v={VER}"></script><script src="{root}assets/site.js?v={VER}"></script><script src="{root}assets/scale.js?v={VER}"></script><script src="{root}assets/v2.js?v={VER}"></script></body></html>'''

# ---------------- blocks ----------------
def facts_bar(t): return '<div class="facts rv">' + ''.join(f'<div><div class="num">{H(a)}</div><p class="meta">{H(b)}</p></div>' for a, b in t['facts']) + '</div>'

def map_block(root):
    sd = open(os.path.join(ROOT, 'assets/map/overlay-d.svg'), encoding='utf-8').read()
    sm = open(os.path.join(ROOT, 'assets/map/overlay-m.svg'), encoding='utf-8').read()
    return f'''<div class="mapbox rv"><div class="d"><img src="{root}assets/map/map-d.webp" alt="Карта маршрута по Кыргызстану" width="1920" height="1080" loading="lazy">{sd}</div>
<div class="m"><img src="{root}assets/map/map-m.webp" alt="Карта маршрута по Кыргызстану" width="2160" height="1542" loading="lazy">{sm}</div></div>
<div class="legend meta rv"><span><i></i>Переезды на внедорожниках</span><span><i class="r"></i>Возвращение в Бишкек</span><span><i class="h"></i>Верхом и пешком</span></div>
<p class="meta dim" style="margin-top:14px">Схема показывает порядок маршрута, это не дорожная карта.</p>'''

def lakes_block(t, root):
    n = len(t['lakes'])
    return f'<div class="lakes n{n}">' + ''.join(f'''<div class="lake rv"><img src="{img(l['img'], 'm', root)}" alt="{H(l['name'])}" style="object-position:{l['pos']}" loading="lazy" width="900" height="1200"><div class="in"><span class="tag">{H(l['alt'])}</span><h3 class="h2" style="font-size:clamp(24px,calc(2.6*var(--vw)),40px)">{H(l['name'])}</h3><p class="body" style="font-size:16px;color:rgba(255,255,255,.9)">{H(l['text'])}</p></div></div>''' for l in t['lakes']) + '</div>'

def days_block(t, root):
    out = []
    for d in t['days']:
        sub = f'<div class="sub"><img src="{img(d["img2"], "m", root)}" alt="" loading="lazy"></div>' if d.get('img2') else ''
        note = f'<p class="note">{H(d["note"])}</p>' if d.get('note') else ''
        moments = ''.join(f'<li>{H(m)}</li>' for m in d['moments'])
        out.append(f'''<article class="day rv" id="day-{d['n']}"><div class="pics"><div class="main"><img src="{img(d['img'], 'm', root)}" srcset="{img(d['img'], 'm', root)} 900w, {img(d['img'], 'l', root)} 1900w" sizes="(max-width:900px) 100vw, calc(55*var(--vw))" alt="{H(d['caption'])}" style="object-position:{d['pos']}" loading="lazy"></div>{sub}<span class="cap">{H(d['caption'])}</span></div>
<div class="stack" style="--gap:22px"><div class="dn" aria-hidden="true">{d['n']:02d}</div><p class="tag">День {d['n']}</p><h3 class="h2" style="font-size:clamp(24px,calc(2.8*var(--vw)),42px)">{H(d['title'])}</h3><p class="meta route">{H(d['route'])}</p><p class="body">{H(d['text'])}</p><ul class="moments">{moments}</ul>{note}<div class="stay"><b>Ночёвка</b><span>{H(d['stay'])}</span></div></div></article>''')
    return '<div class="days">' + ''.join(out) + '</div>'

def steps_block():
    s = [('Заявка', 'Оставляете контакты, удобный сезон и число людей. Это ни к чему не обязывает.'),
         ('Программа и расчёт', 'Присылаем программу и расчёт под вашу группу и даты, отвечаем на вопросы.'),
         ('Подтверждение', 'Согласуем состав услуг, оформляем разрешения, если они нужны.'),
         ('Выезд', 'Встречаем и едем: внедорожники, небольшая группа, горы.')]
    return '<div class="steps">' + ''.join(f'<div class="step rv"><div class="num">{i + 1}</div><h3 class="h3" style="margin-bottom:10px">{a}</h3><p class="body dim" style="font-size:16px">{b}</p></div>' for i, (a, b) in enumerate(s)) + '</div>'

def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def faq_block(items):
    return '<div class="faq">' + ''.join(f'<details><summary>{H(q)}</summary><p>{H(a)}</p></details>' for q, a in items) + '</div>'

def ctaband(root=''):
    return f'''<section class="sec ctaband" style="background-image:url({root}assets/img/song_sunset-l.webp)"><div class="wrap"><h2 class="h2">Выберите сезон. <span class="hl">Остальное мы подскажем.</span></h2><a class="btn" href="#request" data-open-form="cta-band">Подобрать тур <span class="arrow">→</span></a></div></section>'''

def request_block(tour_name, root, idp='r', cls='light white'):
    return ctaband(root) + f'''<section class="sec {cls}" id="request"><div class="wrap req"><div class="side stack" style="--gap:22px"><span class="tag">Заявка</span>
<h2 class="h2">Хотите поехать? <span class="hl">Давайте поговорим</span></h2>
<p class="body dim">Оставьте контакты — вернёмся с программой и расчётом под вашу группу и даты. Если пока сомневаетесь, тоже напишите: расскажем, подходит ли вам такой формат.</p>
<div class="card"><p class="h3" style="margin-bottom:8px">Что будет дальше</p><p class="body dim" style="font-size:16px">Мы свяжемся с вами, ответим на вопросы и пришлём программу с расчётом. Состав услуг и стоимость согласовываем отдельно.</p></div>
<div class="contact-btns" data-if-contacts><a class="btn ghost sm" data-contact="telegram" data-topic="{H(tour_name)}" hidden>Telegram</a><a class="btn ghost sm" data-contact="whatsapp" data-topic="{H(tour_name)}" hidden>WhatsApp</a><a class="btn ghost sm" data-contact="phone" hidden>Позвонить</a><a class="btn ghost sm" data-contact="email" data-topic="{H(tour_name)}" hidden>Написать</a></div></div>
<div>{form(tour_name, idp, 'section', root)}</div></div></section>'''

VIDEOS = {'home': 'hero', 'grand-expedition': 'hero', 'put-karavanov': 'song', 'vesna-issyk-kul': 'jeti', 'osen-son-kul': 'serp'}
def hero_bg(img_key, pos, alt, root, vkey=None):
    im = f'<img src="{img(img_key, "l", root)}" alt="{H(alt)}" style="object-position:{pos}" fetchpriority="high">'
    if not vkey: return f'<div class="bg">{im}</div>'
    return f'<div class="bg">{im}<video class="hv" muted loop playsinline preload="auto" poster="{root}assets/video/{vkey}.jpg"><source src="{root}assets/video/{vkey}.mp4" type="video/mp4"></video></div>'

def marquee():
    words = ['Кель-Суу', 'Сон-Куль', 'Ала-Куль', 'Иссык-Куль', 'Таш-Рабат', 'Алай', 'Сары-Челек', 'Джети-Огуз', 'Барскоон', 'Сказка']
    one = ''.join(f'<span>{w}</span><i>×</i>' for w in words)
    return f'<div class="marquee" aria-hidden="true"><div class="track">{one}{one}</div></div>'

SEAS_TXT = [('spring', 'Весна', 'Каньоны и первые цветы'), ('summer', 'Лето', 'Озёра и высокогорье'), ('autumn', 'Осень', 'Золотой Сон-Куль'), ('winter', 'Зима', 'Снег и горячие источники')]
def yplate(root):
    cells = ''.join(f'<a class="yp yp-{k}" href="{root}{PFX}tours/"><b>{n}</b><span>{d}</span></a>' for k, n, d in SEAS_TXT)
    return f'<section class="yplate" aria-label="Сезоны"><div class="ylab"><span>Туры на весь год</span></div><div class="yrow">{cells}</div></section>'

def reel_block(root):
    clips = [('issyk', 'Иссык-Куль'), ('bars', 'Водопады Барскоона'), ('aksai', 'Каньоны Ак-Сай'), ('serp', 'Серпантин «33 попугая»'), ('song', 'Юрты Сон-Куля'), ('jeti', 'Джети-Огуз')]
    return '<div class="reel">' + ''.join(f'<figure class="vcard rv"><video muted loop playsinline preload="none" poster="{root}assets/video/{k}.jpg"><source src="{root}assets/video/{k}.mp4" type="video/mp4"></video><figcaption class="cap">{n}</figcaption></figure>' for k, n in clips) + '</div>'

SPN = dict(SEASONS)
def splates(t):
    ks = t['seasons']
    if len(ks) == 1: return f'<span class="sp sp-{ks[0]}"><b>{SPN[ks[0]]}</b> {H(t["season"])}</span>'
    return ''.join(f'<span class="sp sp-{k}"><b>{SPN[k]}</b></span>' for k in ks) + f'<span class="chip">{H(t["season"])}</span>'
def ctitle(t): return ' · '.join(t['points']) if t.get('points') else t['card_title']

def tcard(t, root, big=False):
    chips = ''.join(f'<span class="chip">{H(a)} {H(b)}</span>' for a, b in t['facts'][:3])
    return f'''<a class="tcard rv" href="{tour_url(t, root)}" data-seasons="{' '.join(t['seasons'])}" data-months="{' '.join(str(m) for m in t['months'])}"><img src="{img(t['card_img'], 'l' if big else 'm', root)}" alt="{H(t['title'])}" loading="lazy"><div class="in"><span class="tag">{H(t['badge'])}</span><h2 class="h2" style="font-size:clamp(26px,calc(2.8*var(--vw)),44px)">{H(t['title'])}</h2><p class="body" style="font-size:16px;color:rgba(255,255,255,.9)">{H(ctitle(t))}</p><div style="display:flex;flex-wrap:wrap;gap:8px">{chips}{splates(t)}</div></div></a>'''

def calendar_block(root):
    head_ = '<div class="cal-head"><span></span><span class="months">' + ''.join(f'<span>{m}</span>' for m in MONTHS) + '</span></div>'
    rows = ''
    for t in TOURS:
        cells = ''.join(f'<i class="{"on" if (i + 1) in t["months"] else ""}"></i>' for i in range(12))
        rows += f'<a class="cal-row" href="{tour_url(t, root)}"><span class="cal-name">{H(t["title"])}<small>{H(t["season"])}</small></span><span class="cal-bar">{cells}</span></a>'
    return f'<div class="cal rv" role="table" aria-label="Календарь туров">{head_}{rows}</div>'

# ---------------- pages ----------------
KW_RU = 'туры по Кыргызстану, джип-тур Кыргызстан, экспедиции на внедорожниках, Иссык-Куль, Сон-Куль, Кель-Суу, Ала-Куль, Тянь-Шань, юрты, небольшие группы'
KW_EN = 'Kyrgyzstan tours, Kyrgyzstan 4x4 expedition, jeep tour Kyrgyzstan, Central Asia adventure travel, Song-Kul, Kel-Suu, Ala-Kul, Issyk-Kul, Tian Shan, yurt stay, small group tour'
def kw(): return KW_RU if LANG == 'ru' else KW_EN

def page_home():
    R = rootfor(0)
    why = [('1', 'Маленькая группа', 'От 4 до 8 человек. Вы не потеряетесь в толпе и не зависите от большого автобуса.'),
           ('2', 'Два внедорожника', 'Трассы, горные дороги и бездорожье: туда, куда не доедет экскурсионный транспорт.'),
           ('3', 'Маршруты на весь год', 'Весенние каньоны, летние озёра, осенний Сон-Куль и зимний Каракол: у каждого сезона своя поездка.'),
           ('4', 'Честно о нагрузке', 'Рассказываем заранее: где долгие переезды, где конные и пешие участки, что зависит от погоды.')]
    whyh = ''.join(f'<div class="card rv"><div class="ico">{n}</div><h3 class="h3">{a}</h3><p class="body dim" style="font-size:16px">{b}</p></div>' for n, a, b in why)
    others = ''.join(tcard(t, R) for t in TOURS[1:])
    items = {"@type": "ItemList", "name": tt('Туры VOYZ'), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": page_url(LANG, 'tours/%s/' % t['slug']), "name": t['title']} for i, t in enumerate(TOURS)]}
    body = head('VOYZ Travel — туры на внедорожниках по Кыргызстану', 'Авторские экспедиции по Кыргызстану на внедорожниках на весь год: Ала-Куль, Кель-Суу, Сон-Куль, Алай, Сары-Челек, зимний Иссык-Куль.', R, [items, faq_ld(G['faq'][:6])], kw()) + header(R, 'home') + f'''
<section class="hero">{hero_bg(G['hero'], G['hero_pos'], 'Озеро Кель-Суу между скал', R, VIDEOS['home'])}
<div class="wrap"><span class="tag">Экспедиции по Кыргызстану</span><h1 class="h1" style="margin-top:22px">Туда, куда не&nbsp;доезжает <span class="hl">автобус</span></h1>
<p class="body lead">Авторские туры на внедорожниках по Тянь-Шаню и Памиро-Алаю: высокогорные озёра, красные каньоны, ночи в юртах. Небольшая группа, продуманный маршрут, поездки в любое время года.</p>
<div class="cta"><a class="btn" href="tours/">Смотреть все туры <span class="arrow">→</span></a><a class="btn ghost" href="#request" data-open-form="hero">Подобрать тур</a></div>
<div class="facts rv"><div><div class="num">{len(TOURS)}</div><p class="meta">маршрутов</p></div><div><div class="num">12</div><p class="meta">месяцев в году</p></div><div><div class="num">2</div><p class="meta">внедорожника</p></div><div><div class="num">4–8</div><p class="meta">человек в группе</p></div></div></div></section>
{yplate(R)}
<section class="sec light" id="why"><div class="wrap"><span class="tag">Почему VOYZ</span><h2 class="h2" style="margin-top:22px;max-width:16ch">Не просто посмотреть. <span class="hl">Почувствовать.</span></h2>
<p class="body dim" style="max-width:36em;margin-top:22px">Дороги за горизонт, озёра между скал, ночи под звёздным небом. Каждая поездка открывает другой Кыргызстан.</p><div class="why">{whyh}</div></div></section>

<section class="sec" id="reel"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">В движении</span><h2 class="h2">Дорога, <span class="hl">которую хочется проехать</span></h2></div><p class="body dim">Короткие кадры с маршрутов: вода, скалы, серпантины и юрты. Так выглядит поездка до того, как вы в неё отправились.</p></div>{reel_block(R)}</div></section>

<section class="sec light white" id="tours"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">Флагман</span><h2 class="h2">{G['title']}</h2></div><p class="body dim">{H(G['summary'])}</p></div>
<a class="feat rv" href="{tour_url(G, R)}"><div class="ph"><img src="{img(G['card_img'], 'l', R)}" alt="Кель-Суу" loading="lazy"><span class="tag">{H(G['badge'])}</span></div>
<div class="tx"><p class="meta dim">{H(G['kicker'])}</p><ul class="pts">{''.join(f'<li>{H(x)}</li>' for x in G['points'])}</ul><p class="body dim" style="font-size:16px">{H(G['summary'])}</p>
<div class="row">{''.join(f'<span class="chip">{H(a)} {H(b)}</span>' for a, b in G['facts'])}</div>
<div class="sline">{splates(G)}<span class="body dim" style="font-size:16px">Старт и финиш — Бишкек.</span></div><span class="btn" style="align-self:flex-start">Подробнее о туре <span class="arrow">→</span></span></div></a><div class="hhead"><span class="meta dim">Все маршруты</span><span class="hnav"><button type="button" data-hnav="-1" aria-label="Назад">←</button><button type="button" data-hnav="1" aria-label="Вперёд">→</button></span></div>
<div class="hrow" id="trow" tabindex="0">{''.join(tcard(t, R).replace('class="tcard rv"', 'class="tcard"', 1) for t in TOURS)}</div></div></section>

<section class="sec light" id="year"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">Туры на весь год</span><h2 class="h2">Для каждого сезона <span class="hl">своя поездка</span></h2></div><p class="body dim">Весной каньоны без толп, летом высокогорные озёра, осенью золотой свет на Сон-Куле, зимой снег и горячие источники. Выберите время, а маршрут мы подскажем.</p></div>
{calendar_block(R)}</div></section>

<section class="sec light white" id="now"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">По сезону</span><h2 class="h2">Сейчас в сезоне <span class="hl" id="nowm"></span></h2></div><p class="body dim">Эти маршруты можно проехать в ближайшие недели. Остальные ждут своего сезона: весь год в каталоге.</p></div>
<div class="grid" id="nowgrid">{''.join(tcard(t, R).replace('class="tcard rv"', 'class="tcard rv" hidden', 1) for t in TOURS)}</div><noscript><style>#nowgrid [hidden]{{display:block!important}}</style></noscript></div></section>

<section class="sec light" id="lakes"><div class="wrap"><span class="tag">Три озера</span><h2 class="h2" style="margin-top:22px;max-width:18ch">Ради таких мест <span class="hl">отправляются в экспедиции</span></h2>{lakes_block(G, R)}</div></section>

<section class="sec light white" id="route"><div class="wrap"><span class="tag">Маршрут флагмана</span><h2 class="h2" style="margin-top:22px">Один маршрут. <span class="hl">Разные миры</span></h2>{map_block(R)}</div></section>

<section class="sec light" id="faq"><div class="wrap faqwrap"><div class="faqhead"><span class="tag dark">Вопросы</span><h2 class="h2" style="margin-top:22px">Частые <span class="hl">вопросы</span></h2><p class="body dim" style="margin-top:20px">Если не нашли ответ, напишите нам: расскажем честно, подходит ли вам такой формат.</p><a class="btn" href="#request" data-open-form="faq" style="margin-top:26px">Задать вопрос <span class="arrow">→</span></a></div><div>{faq_block(G['faq'][:6])}</div></div></section>

{request_block('Подбор тура', R)}'''
    return body + footer(R, modal(R, 'Подбор тура'), mbar('Подобрать тур'))

def page_tours():
    R = rootfor(1)
    chips = '<div class="filters" role="group" aria-label="Сезон"><button class="fchip on" data-season="all">Все</button>' + ''.join(f'<button class="fchip" data-season="{k}">{v}</button>' for k, v in SEASONS) + '</div>'
    cards = ''.join(tcard(t, R, big=True) for t in TOURS)
    items = {"@type": "ItemList", "name": tt('Туры VOYZ'), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": page_url(LANG, 'tours/%s/' % t['slug']), "name": t['title']} for i, t in enumerate(TOURS)]}
    bc = crumbs([(tt('Главная'), page_url(LANG, '')), (tt('Туры'), page_url(LANG, 'tours/'))])
    body = head('Туры по Кыргызстану на внедорожниках — VOYZ Travel', 'Каталог авторских экспедиций VOYZ по Кыргызстану на весь год: весна, лето, осень и зима, небольшие группы, юрты, высокогорные озёра.', R, [bc, items], kw()) + header(R, 'tours') + f'''
<section class="phead ink"><div class="wrap split"><div class="stack"><span class="tag">Каталог</span><h1 class="h1" style="font-size:clamp(40px,calc(6*var(--vw)),96px)">Наши <span class="hl">туры</span></h1></div>
<p class="body dim">Авторские экспедиции по Кыргызстану: внедорожники, горы, озёра и юрты. Небольшие группы и маршруты на любой сезон.</p></div></section>
<section class="sec light"><div class="wrap"><div class="cal-wrap">{calendar_block(R)}</div>{chips}<div class="grid" id="tgrid" style="margin-top:20px">{cards}
<div class="tcard custom rv" data-seasons="spring summer autumn winter"><div class="in"><span class="tag dark">Под вас</span><div class="stack"><h2 class="h2" style="font-size:clamp(26px,calc(2.8*var(--vw)),44px)">Свой маршрут на внедорожниках</h2><p class="body" style="font-weight:700">Хотите другую длительность, даты или состав: компания друзей, семья, корпоративная поездка? Соберём маршрут под вас.</p></div><a class="btn dark" href="#request" data-open-form="catalog-custom" style="align-self:flex-start">Обсудить маршрут <span class="arrow">→</span></a></div></div>
</div></div></section>{request_block('Свой маршрут', R, 'c')}'''
    return body + footer(R, modal(R, 'Свой маршрут'), mbar())

def page_tour(t):
    R = rootfor(2)
    meta = ''.join(f'<div class="card rv" style="padding:22px 26px"><p class="meta dim">{H(a)}</p><p class="body" style="font-weight:800;margin-top:6px">{H(b)}</p></div>' for a, b in t['meta'])
    diff = ''.join(f'''<div class="card rv"><p class="h3">{H(x['name'])}</p><div class="dots">{''.join(f'<i class="{"on" if i < x["level"] else ""}"></i>' for i in range(5))}</div><p class="meta dim">{H(x['text'])}</p></div>''' for x in t['difficulty'])
    org = ''.join(f'<div class="card rv"><p class="h3">{H(a)}</p><p class="body dim" style="font-size:16px">{H(b)}</p></div>' for a, b in t['organization'])
    yes = ''.join(f'<li>{H(x)}</li>' for x in t['fit_yes']); no = ''.join(f'<li>{H(x)}</li>' for x in t['fit_no'])
    ndays = t['days'][-1]['n']
    trip = {"@type": "TouristTrip", "name": "VOYZ " + t['title'], "description": t['summary'], "touristType": tt('Небольшая группа'), "inLanguage": LANG,
            "provider": {"@id": SITE_URL + "/#org"}, "image": '%s/assets/og/%s-%s.jpg' % (SITE_URL, t['slug'], LANG), "url": page_url(LANG, 'tours/%s/' % t['slug']),
            "itinerary": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": d['n'], "name": d['title'], "description": d['route']} for d in t['days']]}}
    bc = crumbs([(tt('Главная'), page_url(LANG, '')), (tt('Туры'), page_url(LANG, 'tours/')), (t['title'], page_url(LANG, 'tours/%s/' % t['slug']))])
    has_map = t.get('map')
    sub = [('lakes', 'Главное')] + ([('route', 'Маршрут')] if has_map else []) + [('days', 'По дням'), ('fit', 'Для кого'), ('org', 'Организация'), ('faq', 'Вопросы')]
    subnav = ''.join(f'<a class="l" href="#{i}">{n}</a>' for i, n in sub)
    first, _, rest = t['title'].partition(' ')
    h1 = f'{H(first)} <span class="hl">{H(rest)}</span>' if rest else f'<span class="hl">{H(t["title"])}</span>'
    photo_note = f'<p class="meta dim" style="margin-top:14px;max-width:46em">{H(t["photo_note"])}</p>' if t.get('photo_note') else ''
    related = ''.join(tcard(x, R) for x in TOURS if x is not t)
    map_sec = f'<section class="sec light" id="route"><div class="wrap"><span class="tag">Маршрут</span><h2 class="h2" style="margin-top:22px">Один маршрут. <span class="hl">Разные миры</span></h2>{map_block(R)}</div></section>' if has_map else ''
    title = f'{t["title"]} — {ndays} дней на внедорожниках по Кыргызстану · VOYZ'
    body = head(title, t['summary'], R, [bc, trip, faq_ld(t['faq'])], kw()) + header(R, 'tour') + f'''
<section class="hero">{hero_bg(t['hero'], t['hero_pos'], t['title'], R, VIDEOS.get(t['slug']))}
<div class="wrap"><span class="tag">{H(t['badge'])}</span><h1 class="h1" style="margin-top:22px;font-size:clamp(34px,calc(6.4*var(--vw)),104px)">{h1}</h1>
<p class="body lead">{H(t['headline'])}.</p>
<div class="cta"><a class="btn" href="#request" data-open-form="tour-hero">Узнать стоимость и даты <span class="arrow">→</span></a><a class="btn ghost" href="#days">Смотреть программу</a></div>{facts_bar(t)}</div></section>
<nav class="subnav" aria-label="Разделы тура"><div class="wrap">{subnav}<a class="btn sm" href="#request" data-open-form="subnav">Оставить заявку</a></div></nav>

<section class="sec light {'white' if has_map else ''}" id="lakes"><div class="wrap"><div class="split"><div class="stack"><span class="tag">Главное</span><h2 class="h2">Что вы <span class="hl">увидите</span></h2></div><p class="body dim">{H(t['summary'])}</p></div>{lakes_block(t, R)}
<div class="metas">{meta}</div>{photo_note}</div></section>
{map_sec}
<section class="sec light white" id="days"><div class="wrap"><span class="tag">Программа</span><h2 class="h2" style="margin-top:22px">{ndays} дней <span class="hl">по порядку</span></h2><p class="body dim" style="max-width:38em;margin-top:20px">Мы не привязываем день к минутам: в горах ритм задают погода и дорога. Зато точно знаем, где вы окажетесь и что увидите.</p>{days_block(t, R)}</div></section>

<section class="sec light" id="fit"><div class="wrap"><span class="tag dark">Для кого</span><h2 class="h2" style="margin-top:22px">Это путешествие <span class="hl">не для всех</span></h2><p class="body dim" style="max-width:38em;margin-top:20px">Важно честно понимать, что вас ждёт: дороги, высота, условия ночёвок и погода.</p>
<div class="diff">{diff}</div><p class="meta dim" style="margin-top:14px">{H(t['difficulty_note'])}</p>
<div class="fit"><div class="card"><p class="h3">Вам подойдёт, если</p><ul>{yes}</ul></div><div class="card no"><p class="h3">Лучше выбрать другое, если</p><ul>{no}</ul></div></div></div></section>

<section class="sec" id="org"><div class="wrap"><span class="tag">Организация</span><h2 class="h2" style="margin-top:22px">Как мы <span class="hl">всё устроим</span></h2><div class="org">{org}</div>
<div class="orgnote rv"><p>{H(t['organization_note'])}</p><a class="btn dark" href="#request" data-open-form="org">Получить расчёт <span class="arrow">→</span></a></div></div></section>

<section class="sec light white" id="faq"><div class="wrap faqwrap"><div class="faqhead"><span class="tag dark">Вопросы</span><h2 class="h2" style="margin-top:22px">Что обычно <span class="hl">спрашивают</span></h2><p class="body dim" style="margin-top:20px">Не нашли свой вопрос? Напишите нам, мы ответим и подскажем, подойдёт ли вам этот маршрут.</p><a class="btn" href="#request" data-open-form="faq" style="margin-top:26px">Задать вопрос <span class="arrow">→</span></a></div><div>{faq_block(t['faq'])}</div></div></section>

<section class="sec light" id="more"><div class="wrap"><span class="tag">Другие маршруты</span><h2 class="h2" style="margin:22px 0 32px">Ещё <span class="hl">поездки</span></h2><div class="grid">{related}</div></div></section>

{request_block(t['title'], R)}'''
    return body + footer(R, modal(R, t['title']), mbar('Узнать стоимость и даты'))

def page_privacy():
    R = rootfor(1)
    bc = crumbs([(tt('Главная'), page_url(LANG, '')), (tt('Политика конфиденциальности'), page_url(LANG, 'privacy/'))])
    return head('Политика конфиденциальности — VOYZ Travel', 'Как мы обрабатываем данные из формы заявки.', R, [bc]) + header(R) + f'''<section class="phead ink"><div class="wrap prose"><h1 class="h2">Политика конфиденциальности</h1>
<p class="body dim" style="margin-top:18px">Краткая редакция для работы формы заявки. Перед запуском сайта её нужно согласовать с юристом и дополнить реквизитами компании.</p>
<h2 class="h3">Какие данные мы собираем</h2><p class="body">Имя, контакт для связи (Telegram, WhatsApp, телефон или почта), желаемый сезон поездки, число путешественников и комментарий — только то, что вы сами указали в форме заявки.</p>
<h2 class="h3">Зачем</h2><p class="body">Чтобы связаться с вами, ответить на вопросы и подготовить программу и расчёт тура.</p>
<h2 class="h3">Кому передаются данные</h2><p class="body">Мы не продаём и не передаём ваши данные третьим лицам, кроме случаев, когда это нужно для организации поездки (например, для оформления разрешений в пограничную зону) и только с вашего согласия.</p>
<h2 class="h3">Как отозвать согласие</h2><p class="body">Напишите нам любым удобным способом — мы удалим ваши данные.</p></div></section>''' + footer(R)

def page_credits():
    R = rootfor(1)
    used = []
    for t in TOURS:
        for k in [t['hero'], t['card_img']] + [l['img'] for l in t['lakes']] + [d[x] for d in t['days'] for x in ('img', 'img2') if d.get(x)]:
            if k not in used: used.append(k)
    rows = ''
    for k in used:
        if k not in CR: continue
        nm = re.sub(r'\s*\(\d+\)$', '', os.path.splitext(CR[k]['title'])[0])
        rows += f'<p class="body" style="font-size:16px"><b>{H(nm)}</b> — {H(CR[k]["artist"] or "автор не указан")}, {H(CR[k]["lic"])}, <a href="{H(CR[k]["page"])}" rel="noopener" target="_blank">источник</a></p>'
    rows += '<p class="body" style="font-size:16px"><b>Видео</b> — Pexels (свободная лицензия Pexels), подборка VOYZ по маршруту</p>'
    rows += '<p class="body" style="font-size:16px"><b>Кок-Мойнок, Ак-Сай</b> — фотографии из архива VOYZ Travel</p><p class="body" style="font-size:16px"><b>Карта</b> — рельеф SRTM / AWS Terrain Tiles; границы Natural Earth; озёра © участники OpenStreetMap (ODbL)</p>'
    bc = crumbs([(tt('Главная'), page_url(LANG, '')), (tt('Авторы фотографий'), page_url(LANG, 'credits/'))])
    return head('Авторы фотографий — VOYZ Travel', 'Благодарим авторов фотографий и данных.', R, [bc]) + header(R) + f'<section class="phead ink"><div class="wrap"><span class="tag">Благодарим</span><h1 class="h2" style="margin:22px 0 40px">Авторы фотографий</h1><div class="credits">{rows}</div></div></section>' + footer(R)

# ---------------- translation pass (RU -> EN) ----------------
CYR = re.compile('[А-Яа-яЁё]')
MISSING = set()

def tr_str(s):
    k = html.unescape(s).strip()
    if not CYR.search(k): return s
    if k in EN:
        lead = s[:len(s) - len(s.lstrip())]; trail = s[len(s.rstrip()):]
        return lead + html.escape(EN[k], quote=False) + trail
    MISSING.add(k); return s

def tr_json(o):
    if isinstance(o, str):
        if CYR.search(o) and o not in EN: MISSING.add(o)
        return EN.get(o, o) if CYR.search(o) else o
    if isinstance(o, list): return [tr_json(x) for x in o]
    if isinstance(o, dict): return {k: tr_json(v) for k, v in o.items()}
    return o

def translate(doc):
    blocks = []
    def stash(m):
        blocks.append(m.group(0)); return '\x00%d\x00' % (len(blocks) - 1)
    doc = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', stash, doc)
    doc = re.sub(r'>([^<>]+)<', lambda m: '>' + tr_str(m.group(1)) + '<', doc)
    def attr(m):
        v = html.unescape(m.group(2))
        if not CYR.search(v): return m.group(0)
        if v in EN: return m.group(1) + html.escape(EN[v], quote=True) + '"'
        MISSING.add(v); return m.group(0)
    doc = re.sub(r'(\b(?:alt|placeholder|title|aria-label|content|data-tour|data-topic)=")([^"]*)"', attr, doc)
    def back(m):
        b = blocks[int(m.group(1))]
        if 'application/ld+json' in b[:80]:
            mm = re.match(r'(<script[^>]*>)([\s\S]*)(</script>)', b)
            return mm.group(1) + json.dumps(tr_json(json.loads(mm.group(2))), ensure_ascii=False) + mm.group(3)
        return b
    return re.sub(r'\x00(\d+)\x00', back, doc)

# ---------------- build ----------------
def write(path, content):
    p = os.path.join(ROOT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(content)

PAGES = [('', 'home', lambda: page_home()), ('tours/', 'tours', lambda: page_tours()), ('privacy/', 'home', lambda: page_privacy()), ('credits/', 'home', lambda: page_credits())]

def build(lang):
    global LANG, PFX
    LANG, PFX = lang, ('en/' if lang == 'en' else '')
    pages = list(PAGES) + [('tours/%s/' % t['slug'], t['slug'], (lambda t=t: page_tour(t))) for t in TOURS]
    out = []
    for path, og, fn in pages:
        CUR.update(path=path, og=og)
        doc = fn()
        if lang == 'en': doc = translate(doc)
        write(PFX + path + 'index.html', doc); out.append(path)
    return out

paths = build('ru')
if HAS_EN:
    MISSING.clear(); build('en')
    if MISSING:
        json.dump(sorted(MISSING), open(os.path.join(ROOT, 'data/en_missing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('WARNING: %d untranslated strings -> data/en_missing.json' % len(MISSING))
else:
    LANG = 'ru'

# sitemap, robots, manifest, 404
def sm_url(path):
    alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l, path)}"/>' for l in ('ru', 'en')) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url("en", path)}"/>'
    pr = '1.0' if path == '' else ('0.9' if path in ('tours/',) else ('0.8' if path.startswith('tours/') else '0.3'))
    return ''.join(f'<url><loc>{page_url(l, path)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{pr}</priority>{alts}</url>' for l in ('ru', 'en'))
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + ''.join(sm_url(p) for p in paths) + '</urlset>')
write('robots.txt', 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE_URL)
write('site.webmanifest', json.dumps({"name": "VOYZ Travel", "short_name": "VOYZ", "description": "Туры на внедорожниках по Кыргызстану / 4x4 tours in Kyrgyzstan",
      "lang": "ru", "start_url": "./", "scope": "./", "display": "browser", "background_color": "#0B0B0B", "theme_color": "#0B0B0B",
      "icons": [{"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                {"src": "assets/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False, indent=1))
write('404.html', f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>404 — VOYZ Travel</title><link rel="icon" href="{SITE_URL}/favicon.ico"><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#0B0B0B;color:#fff;font-family:system-ui,sans-serif;text-align:center;padding:24px}}
h1{{font-size:clamp(64px,16vw,160px);margin:0;color:#D8FC00;letter-spacing:-.04em}}p{{opacity:.8;font-size:18px}}a{{display:inline-block;margin:8px;padding:16px 28px;border-radius:99px;background:#D8FC00;color:#000;font-weight:800;text-decoration:none}}</style></head>
<body><main><h1>404</h1><p>Такой страницы нет. / Page not found.</p><a href="{SITE_URL}/">На главную</a><a href="{SITE_URL}/en/">Home (EN)</a></main></body></html>''')
print('built', len(paths), 'pages x 2 languages,', len(TOURS), 'tours' + ('' if HAS_EN else ' (no en.json yet)'))

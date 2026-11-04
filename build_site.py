"""Static site generator: data/*.json -> plain HTML pages (good for SEO, deployable anywhere).
Run: python build_site.py   (every tour in data/tours.json + data/tours_extra.json gets its own page)"""
import json, os, html, re
H = html.escape
ROOT = os.path.dirname(os.path.abspath(__file__))
NOINDEX = True   # preview deployment: keep out of search engines; set False for the real launch
def load(p): return json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
BASE, EXTRA, CR = load('data/tours.json'), load('data/tours_extra.json'), load('data/credits.json')
LOGO = open(os.path.join(ROOT, 'assets/logo.svg'), encoding='utf-8').read()
DEF = EXTRA['defaults']
TOURS = BASE['tours'] + EXTRA['tours']
for t in TOURS:
    t.setdefault('organization_note', DEF['organization_note'])
    if t['slug'] != 'grand-expedition': t['faq'] = t['faq'] + DEF['faq_common']
G = TOURS[0]                       # flagship tour (home hero, map)
MONTHS = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
SEASONS = [('spring', 'Весна'), ('summer', 'Лето'), ('autumn', 'Осень'), ('winter', 'Зима')]

def img(k, size='l', root=''): return '%sassets/img/%s-%s.webp' % (root, k, size)
def tour_url(t, root): return '%stours/%s/' % (root, t['slug'])

def head(title, desc, root, og=None, extra=''):
    og = og or img(G['hero'], 'm', root)
    robots = '<meta name="robots" content="noindex,nofollow">' if NOINDEX else ''
    return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}
<title>{H(title)}</title><meta name="description" content="{H(desc)}">
<meta property="og:title" content="{H(title)}"><meta property="og:description" content="{H(desc)}"><meta property="og:type" content="website"><meta property="og:image" content="{og}">
<meta name="theme-color" content="#0B0B0B">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mulish:wght@500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css?v=1793788474"><link rel="stylesheet" href="{root}assets/v2.css?v=1793788474">{extra}</head><body>'''

def header(root, cur=''):
    nav = [('tours/', 'Туры'), ('#year', 'Туры на весь год'), ('#how', 'Как это работает'), ('#faq', 'Вопросы')]
    def href(h): return root + h if h == 'tours/' else (h if cur == 'home' else root + 'index.html' + h)
    links = ''.join(f'<a href="{href(h)}"{" aria-current=page" if (cur == "tours" and h == "tours/") else ""}>{t}</a>' for h, t in nav)
    return f'''<header class="hdr"><div class="wrap"><a class="logo-link" href="{root}index.html" aria-label="VOYZ Travel"><img src="{root}assets/logo.svg" alt="VOYZ" width="118" height="16"></a>
<nav class="nav" aria-label="Основное">{links}<a class="btn sm" href="#request" data-open-form="header">Подобрать тур</a></nav>
<button class="burger" data-menu aria-label="Меню"><span></span></button></div></header>
<div class="mnav" role="dialog" aria-label="Меню"><button class="x" data-menu aria-label="Закрыть">×</button>{links}<a href="#request" data-open-form="menu" style="color:var(--lime)">Оставить заявку</a></div>'''

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
<label class="consent"><input type="checkbox" name="consent" required><span>Согласен на обработку персональных данных и с <a href="{root}privacy/">политикой конфиденциальности</a></span></label>
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
<div><p class="meta dim">Туры</p><ul>{links}<li><a href="{root}tours/">Все туры</a></li></ul></div>
<div><p class="meta dim">Связаться</p><ul><li><a href="#request" data-open-form="footer">Оставить заявку</a></li>
<li><a data-contact="telegram" hidden>Telegram</a></li><li><a data-contact="whatsapp" hidden>WhatsApp</a></li><li><a data-contact="phone" hidden>Позвонить</a></li><li><a data-contact="email" hidden>Написать на почту</a></li>
<li><a href="https://voyz.ru" rel="noopener">voyz.ru</a></li></ul></div></div>
<div class="bot meta dim"><span>© VOYZ Travel</span><span><a href="{root}privacy/">Политика конфиденциальности</a> · <a href="{root}credits/">Авторы фотографий</a></span></div></div></footer>
{modal_html}{mbar_html}<script src="{root}assets/config.js?v=1793788474"></script><script src="{root}assets/site.js?v=1793788474"></script><script src="{root}assets/scale.js?v=1793788474"></script><script src="{root}assets/v2.js?v=1793788474"></script></body></html>'''

def write(path, content):
    p = os.path.join(ROOT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(content)

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

def faq_block(items, schema=True):
    h = '<div class="faq">' + ''.join(f'<details><summary>{H(q)}</summary><p>{H(a)}</p></details>' for q, a in items) + '</div>'
    if schema:
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
        h += '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    return h

def ctaband():
    return '''<section class="sec light lime ctaband"><div class="wrap"><h2 class="h2">Выберите сезон. <span class="hl">Остальное мы подскажем.</span></h2><a class="btn" href="#request" data-open-form="cta-band">Подобрать тур <span class="arrow">→</span></a></div></section>'''

def request_block(tour_name, root, idp='r', cls='light'):
    return ctaband() + f'''<section class="sec {cls}" id="request"><div class="wrap req"><div class="side stack" style="--gap:22px"><span class="tag">Заявка</span>
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

def reel_block(root):
    clips = [('issyk', 'Иссык-Куль'), ('bars', 'Водопады Барскоона'), ('aksai', 'Каньоны Ак-Сай'), ('serp', 'Серпантин «33 попугая»'), ('song', 'Юрты Сон-Куля'), ('jeti', 'Джети-Огуз')]
    return '<div class="reel">' + ''.join(f'<figure class="vcard rv"><video muted loop playsinline preload="none" poster="{root}assets/video/{k}.jpg"><source src="{root}assets/video/{k}.mp4" type="video/mp4"></video><figcaption class="cap">{n}</figcaption></figure>' for k, n in clips) + '</div>'

def season_labels(t): return ' · '.join(dict(SEASONS)[s] for s in t['seasons'])

def tcard(t, root, big=False):
    chips = ''.join(f'<span class="chip">{H(a)} {H(b)}</span>' for a, b in t['facts'][:3])
    return f'''<a class="tcard rv" href="{tour_url(t, root)}" data-seasons="{' '.join(t['seasons'])}"><img src="{img(t['card_img'], 'l' if big else 'm', root)}" alt="{H(t['title'])}" loading="lazy"><div class="in"><span class="tag">{H(t['badge'])}</span><h2 class="h2" style="font-size:clamp(26px,calc(2.8*var(--vw)),44px)">{H(t['title'])}</h2><p class="body" style="font-size:16px;color:rgba(255,255,255,.9)">{H(t['card_title'])}</p><div style="display:flex;flex-wrap:wrap;gap:8px">{chips}<span class="chip">{H(t['season'])}</span></div></div></a>'''

def calendar_block(root):
    head_ = '<div class="cal-head"><span></span><span class="months">' + ''.join(f'<span>{m}</span>' for m in MONTHS) + '</span></div>'
    rows = ''
    for t in TOURS:
        cells = ''.join(f'<i class="{"on" if (i + 1) in t["months"] else ""}"></i>' for i in range(12))
        rows += f'<a class="cal-row" href="{tour_url(t, root)}"><span class="cal-name">{H(t["title"])}<small>{H(t["season"])}</small></span><span class="cal-bar">{cells}</span></a>'
    return f'<div class="cal rv" role="table" aria-label="Календарь туров">{head_}{rows}</div>'

# ---------------- pages ----------------
def page_home():
    R = ''
    why = [('1', 'Маленькая группа', 'От 4 до 8 человек. Вы не потеряетесь в толпе и не зависите от большого автобуса.'),
           ('2', 'Два внедорожника', 'Трассы, горные дороги и бездорожье: туда, куда не доедет экскурсионный транспорт.'),
           ('3', 'Маршруты на весь год', 'Весенние каньоны, летние озёра, осенний Сон-Куль и зимний Каракол: у каждого сезона своя поездка.'),
           ('4', 'Честно о нагрузке', 'Рассказываем заранее: где долгие переезды, где конные и пешие участки, что зависит от погоды.')]
    whyh = ''.join(f'<div class="card rv"><div class="ico">{n}</div><h3 class="h3">{a}</h3><p class="body dim" style="font-size:16px">{b}</p></div>' for n, a, b in why)
    others = ''.join(tcard(t, R) for t in TOURS[1:])
    body = head('VOYZ Travel — туры на внедорожниках по Кыргызстану', 'Авторские экспедиции по Кыргызстану на внедорожниках на весь год: Ала-Куль, Кель-Суу, Сон-Куль, Алай, Сары-Челек, зимний Иссык-Куль.', R) + header(R, 'home') + f'''
<section class="hero">{hero_bg(G['hero'], G['hero_pos'], 'Озеро Кель-Суу между скал', R, VIDEOS['home'])}
<div class="wrap"><span class="tag">Экспедиции по Кыргызстану</span><h1 class="h1" style="margin-top:22px">Туда, куда не&nbsp;доезжает <span class="hl">автобус</span></h1>
<p class="body lead">Авторские туры на внедорожниках по Тянь-Шаню и Памиро-Алаю: высокогорные озёра, красные каньоны, ночи в юртах. Небольшая группа, продуманный маршрут, поездки в любое время года.</p>
<div class="cta"><a class="btn" href="tours/">Смотреть все туры <span class="arrow">→</span></a><a class="btn ghost" href="#request" data-open-form="hero">Подобрать тур</a></div>
<div class="facts rv"><div><div class="num">{len(TOURS)}</div><p class="meta">маршрутов</p></div><div><div class="num">12</div><p class="meta">месяцев в году</p></div><div><div class="num">2</div><p class="meta">внедорожника</p></div><div><div class="num">4–8</div><p class="meta">человек в группе</p></div></div></div></section>
{marquee()}
<section class="sec light" id="why"><div class="wrap"><span class="tag">Почему VOYZ</span><h2 class="h2" style="margin-top:22px;max-width:16ch">Не просто посмотреть. <span class="hl">Почувствовать.</span></h2>
<p class="body dim" style="max-width:36em;margin-top:22px">Дороги за горизонт, озёра между скал, ночи под звёздным небом. Каждая поездка открывает другой Кыргызстан.</p><div class="why">{whyh}</div></div></section>

<section class="sec light white" id="tours"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">Флагман</span><h2 class="h2">{G['title']}</h2></div><p class="body dim">{H(G['summary'])}</p></div>
<a class="feat rv" href="{tour_url(G, R)}"><div class="ph"><img src="{img(G['card_img'], 'l', R)}" alt="Кель-Суу" loading="lazy"><span class="tag">{H(G['badge'])}</span></div>
<div class="tx"><p class="meta dim">{H(G['kicker'])}</p><h3 class="h2" style="font-size:clamp(24px,calc(2.5*var(--vw)),38px)">{H(G['card_title'])}</h3><p class="body dim" style="font-size:16px">{H(G['summary'])}</p>
<div class="row">{''.join(f'<span class="chip">{H(a)} {H(b)}</span>' for a, b in G['facts'])}</div>
<p class="body dim" style="font-size:16px">Сезон: {H(G['season'])}. Старт и финиш — Бишкек.</p><span class="btn" style="align-self:flex-start">Подробнее о туре <span class="arrow">→</span></span></div></a></div></section>

<section class="sec" id="reel"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">В движении</span><h2 class="h2">Дорога, <span class="hl">которую хочется проехать</span></h2></div><p class="body dim">Короткие кадры с маршрутов: вода, скалы, серпантины и юрты. Так выглядит поездка до того, как вы в неё отправились.</p></div>{reel_block(R)}</div></section>

<section class="sec light white" id="year"><div class="wrap"><div class="split" style="margin-bottom:clamp(28px,calc(4*var(--vw)),48px)"><div class="stack"><span class="tag">Туры на весь год</span><h2 class="h2">Для каждого сезона <span class="hl">своя поездка</span></h2></div><p class="body dim">Весной каньоны без толп, летом высокогорные озёра, осенью золотой свет на Сон-Куле, зимой снег и горячие источники. Выберите время, а маршрут мы подскажем.</p></div>
{calendar_block(R)}<div class="grid" style="margin-top:28px">{others}</div></div></section>

<section class="sec light white" id="lakes"><div class="wrap"><span class="tag">Три озера</span><h2 class="h2" style="margin-top:22px;max-width:18ch">Ради таких мест <span class="hl">отправляются в экспедиции</span></h2>{lakes_block(G, R)}</div></section>

<section class="sec light" id="route"><div class="wrap"><span class="tag">Маршрут флагмана</span><h2 class="h2" style="margin-top:22px">Один маршрут. <span class="hl">Разные миры</span></h2>{map_block(R)}</div></section>

<section class="sec light white" id="how"><div class="wrap"><span class="tag dark">Как это работает</span><h2 class="h2" style="margin-top:22px">От заявки <span class="hl">до выезда</span></h2>{steps_block()}</div></section>

<section class="sec light white" id="faq" style="padding-top:0"><div class="wrap"><span class="tag dark">Вопросы</span><h2 class="h2" style="margin-top:22px">Частые <span class="hl">вопросы</span></h2>{faq_block(G['faq'][:6], schema=False)}</div></section>

{request_block('Подбор тура', R)}'''
    return body + footer(R, modal(R, 'Подбор тура'), mbar('Подобрать тур'))

def page_tours():
    R = '../'
    chips = '<div class="filters" role="group" aria-label="Сезон"><button class="fchip on" data-season="all">Все</button>' + ''.join(f'<button class="fchip" data-season="{k}">{v}</button>' for k, v in SEASONS) + '</div>'
    cards = ''.join(tcard(t, R, big=True) for t in TOURS)
    body = head('Туры по Кыргызстану на внедорожниках — VOYZ Travel', 'Каталог авторских экспедиций VOYZ по Кыргызстану на весь год.', R) + header(R, 'tours') + f'''
<section class="phead ink"><div class="wrap split"><div class="stack"><span class="tag">Каталог</span><h1 class="h1" style="font-size:clamp(40px,calc(6*var(--vw)),96px)">Наши <span class="hl">туры</span></h1></div>
<p class="body dim">Авторские экспедиции по Кыргызстану: внедорожники, горы, озёра и юрты. Небольшие группы и маршруты на любой сезон.</p></div></section>
<section class="sec light" style="padding-top:clamp(40px,calc(5*var(--vw)),72px)"><div class="wrap"><div class="cal-wrap">{calendar_block(R)}</div>{chips}<div class="grid" id="tgrid" style="margin-top:20px">{cards}
<div class="tcard custom rv" data-seasons="spring summer autumn winter"><div class="in"><span class="tag dark">Под вас</span><div class="stack"><h2 class="h2" style="font-size:clamp(26px,calc(2.8*var(--vw)),44px)">Свой маршрут на внедорожниках</h2><p class="body" style="font-weight:700">Хотите другую длительность, даты или состав: компания друзей, семья, корпоративная поездка? Соберём маршрут под вас.</p></div><a class="btn dark" href="#request" data-open-form="catalog-custom" style="align-self:flex-start">Обсудить маршрут <span class="arrow">→</span></a></div></div>
</div></div></section>{request_block('Свой маршрут', R, 'c', 'light white')}'''
    return body + footer(R, modal(R, 'Свой маршрут'), mbar())

def page_tour(t):
    R = '../../'
    meta = ''.join(f'<div class="card rv" style="padding:22px 26px"><p class="meta dim">{H(a)}</p><p class="body" style="font-weight:800;margin-top:6px">{H(b)}</p></div>' for a, b in t['meta'])
    diff = ''.join(f'''<div class="card rv"><p class="h3">{H(x['name'])}</p><div class="dots">{''.join(f'<i class="{"on" if i < x["level"] else ""}"></i>' for i in range(5))}</div><p class="meta dim">{H(x['text'])}</p></div>''' for x in t['difficulty'])
    org = ''.join(f'<div class="card rv"><p class="h3">{H(a)}</p><p class="body dim" style="font-size:16px">{H(b)}</p></div>' for a, b in t['organization'])
    yes = ''.join(f'<li>{H(x)}</li>' for x in t['fit_yes']); no = ''.join(f'<li>{H(x)}</li>' for x in t['fit_no'])
    ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": "VOYZ " + t['title'], "description": t['summary'], "touristType": "Небольшая группа", "itinerary": [{"@type": "TouristDestination", "name": d['route']} for d in t['days']]}
    has_map = t.get('map')
    sub = [('lakes', 'Главное')] + ([('route', 'Маршрут')] if has_map else []) + [('days', 'По дням'), ('fit', 'Для кого'), ('org', 'Организация'), ('faq', 'Вопросы')]
    subnav = ''.join(f'<a class="l" href="#{i}">{n}</a>' for i, n in sub)
    title_html = H(t['title'])
    first, _, rest = t['title'].partition(' ')
    h1 = f'{H(first)} <span class="hl">{H(rest)}</span>' if rest else f'<span class="hl">{title_html}</span>'
    photo_note = f'<p class="meta dim" style="margin-top:14px;max-width:46em">{H(t["photo_note"])}</p>' if t.get('photo_note') else ''
    related = ''.join(tcard(x, R) for x in TOURS if x is not t)
    map_sec = f'<section class="sec light" id="route"><div class="wrap"><span class="tag">Маршрут</span><h2 class="h2" style="margin-top:22px">Один маршрут. <span class="hl">Разные миры</span></h2>{map_block(R)}</div></section>' if has_map else ''
    body = head(f'{t["title"]} — {t["days"][-1]["n"]} дней на внедорожниках по Кыргызстану · VOYZ', t['summary'], R, og=img(t['hero'], 'm', R), extra='<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>') + header(R, 'tour') + f'''
<section class="hero">{hero_bg(t['hero'], t['hero_pos'], t['title'], R, VIDEOS.get(t['slug']))}
<div class="wrap"><span class="tag">{H(t['badge'])}</span><h1 class="h1" style="margin-top:22px;font-size:clamp(34px,calc(6.4*var(--vw)),104px)">{h1}</h1>
<p class="body lead">{H(t['headline'])}.</p>
<div class="cta"><a class="btn" href="#request" data-open-form="tour-hero">Узнать стоимость и даты <span class="arrow">→</span></a><a class="btn ghost" href="#days">Смотреть программу</a></div>{facts_bar(t)}</div></section>
<nav class="subnav" aria-label="Разделы тура"><div class="wrap">{subnav}<a class="btn sm" href="#request" data-open-form="subnav">Оставить заявку</a></div></nav>

<section class="sec light {'white' if has_map else ''}" id="lakes"><div class="wrap"><div class="split"><div class="stack"><span class="tag">Главное</span><h2 class="h2">Что вы <span class="hl">увидите</span></h2></div><p class="body dim">{H(t['summary'])}</p></div>{lakes_block(t, R)}
<div class="metas">{meta}</div>{photo_note}</div></section>
{map_sec}
<section class="sec light white" id="days"><div class="wrap"><span class="tag">Программа</span><h2 class="h2" style="margin-top:22px">{t['days'][-1]['n']} дней <span class="hl">по порядку</span></h2><p class="body dim" style="max-width:38em;margin-top:20px">Мы не привязываем день к минутам: в горах ритм задают погода и дорога. Зато точно знаем, где вы окажетесь и что увидите.</p>{days_block(t, R)}</div></section>

<section class="sec light" id="fit"><div class="wrap"><span class="tag dark">Для кого</span><h2 class="h2" style="margin-top:22px">Это путешествие <span class="hl">не для всех</span></h2><p class="body dim" style="max-width:38em;margin-top:20px">Важно честно понимать, что вас ждёт: дороги, высота, условия ночёвок и погода.</p>
<div class="diff">{diff}</div><p class="meta dim" style="margin-top:14px">{H(t['difficulty_note'])}</p>
<div class="fit"><div class="card"><p class="h3">Вам подойдёт, если</p><ul>{yes}</ul></div><div class="card no"><p class="h3">Лучше выбрать другое, если</p><ul>{no}</ul></div></div></div></section>

<section class="sec" id="org"><div class="wrap"><span class="tag">Организация</span><h2 class="h2" style="margin-top:22px">Как мы <span class="hl">всё устроим</span></h2><div class="org">{org}</div>
<div class="orgnote rv"><p>{H(t['organization_note'])}</p><a class="btn dark" href="#request" data-open-form="org">Получить расчёт <span class="arrow">→</span></a></div></div></section>

<section class="sec light white" id="faq"><div class="wrap"><span class="tag dark">Вопросы</span><h2 class="h2" style="margin-top:22px">Что обычно <span class="hl">спрашивают</span></h2>{faq_block(t['faq'])}</div></section>

<section class="sec light" id="more"><div class="wrap"><span class="tag">Другие маршруты</span><h2 class="h2" style="margin:22px 0 32px">Ещё <span class="hl">поездки</span></h2><div class="grid">{related}</div></div></section>

{request_block(t['title'], R, 'r', 'light white')}'''
    return body + footer(R, modal(R, t['title']), mbar('Узнать стоимость и даты'))

def page_privacy():
    R = '../'
    return head('Политика конфиденциальности — VOYZ Travel', 'Как мы обрабатываем данные из формы заявки.', R) + header(R) + f'''<section class="phead ink"><div class="wrap prose"><h1 class="h2">Политика конфиденциальности</h1>
<p class="body dim" style="margin-top:18px">Краткая редакция для работы формы заявки. Перед запуском сайта её нужно согласовать с юристом и дополнить реквизитами компании.</p>
<h2 class="h3">Какие данные мы собираем</h2><p class="body">Имя, контакт для связи (Telegram, WhatsApp, телефон или почта), желаемый сезон поездки, число путешественников и комментарий — только то, что вы сами указали в форме заявки.</p>
<h2 class="h3">Зачем</h2><p class="body">Чтобы связаться с вами, ответить на вопросы и подготовить программу и расчёт тура.</p>
<h2 class="h3">Кому передаются данные</h2><p class="body">Мы не продаём и не передаём ваши данные третьим лицам, кроме случаев, когда это нужно для организации поездки (например, для оформления разрешений в пограничную зону) и только с вашего согласия.</p>
<h2 class="h3">Как отозвать согласие</h2><p class="body">Напишите нам любым удобным способом — мы удалим ваши данные.</p></div></section>''' + footer(R)

def page_credits():
    R = '../'
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
    return head('Авторы фотографий — VOYZ Travel', 'Благодарим авторов фотографий и данных.', R) + header(R) + f'<section class="phead ink"><div class="wrap"><span class="tag">Благодарим</span><h1 class="h2" style="margin:22px 0 40px">Авторы фотографий</h1><div class="credits">{rows}</div></div></section>' + footer(R)

pages = [('index.html', page_home()), ('tours/index.html', page_tours()), ('privacy/index.html', page_privacy()), ('credits/index.html', page_credits())]
pages += [('tours/%s/index.html' % t['slug'], page_tour(t)) for t in TOURS]
for path, content in pages: write(path, content)
print('built', len(pages), 'pages,', len(TOURS), 'tours')

(function () {
  var D = window.VOYZ, C = window.VOYZ_CONFIG || {}, T = D.tours, $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var MONTHS = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
  var MFULL = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  var SEASONS = [['all', 'Все'], ['spring', 'Весна'], ['summer', 'Лето'], ['autumn', 'Осень'], ['winter', 'Зима']];
  var A = '../../assets/', V = A + 'video/';
  var VID = { 'grand-expedition': 'hero', 'put-karavanov': 'song', 'vesna-issyk-kul': 'jeti', 'osen-son-kul': 'serp' };
  var phone = $('.phone');
  var EN = document.documentElement.lang === 'en', UI = window.VOYZ_UI || {}, CYR = /[А-Яа-яЁё]/;
  function tx(s) { return EN && UI[s] != null ? UI[s] : s; }
  function tl(s) { return tx(s.trim()) + (/\s$/.test(s) ? ' ' : ''); }
  var RULES = [[/^(\d+) дней$/, '$1 days'], [/^(\d+) тур$/, '$1 tour'], [/^(\d+) тура$/, '$1 tours'],
    [/^Тур: (.+)\. Оставьте контакты, мы вернёмся с программой и расчётом\.$/, 'Tour: $1. Leave your contacts and we will come back with a program and a quote.']];
  function trStr(s) {
    var k = s.trim(); if (!CYR.test(k)) return s; var v = UI[k];
    if (v == null) for (var i = 0; i < RULES.length; i++) if (RULES[i][0].test(k)) { v = k.replace(RULES[i][0], RULES[i][1]); break; }
    return v == null ? s : s.replace(k, v);
  }
  function trTree(n) {
    if (n.nodeType === 3) { var v = trStr(n.nodeValue); if (v !== n.nodeValue) n.nodeValue = v; return; }
    if (n.nodeType !== 1) return;
    ['placeholder', 'aria-label', 'alt', 'title'].forEach(function (a) { if (n.hasAttribute(a)) var o = n.getAttribute(a), v2 = trStr(o); if (v2 !== o) n.setAttribute(a, v2); });
    [].slice.call(n.childNodes).forEach(trTree);
  }
  function img(k, s) { return A + 'img/' + k + '-' + (s || 'm') + '.webp'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function by(slug) { return T.filter(function (t) { return t.slug === slug; })[0]; }
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null'); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { } return v; }
  var favs = store('voyz_favs') || [];

  var I = {
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>',
    tours: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/></svg>',
    cal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M21 3 10 14M21 3l-7 18-4-7-7-4z"/></svg>',
    back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m15 5-7 7 7 7"/></svg>',
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20.5S3.5 15 3.5 9A4.7 4.7 0 0 1 12 6.6 4.7 4.7 0 0 1 20.5 9c0 6-8.5 11.5-8.5 11.5z"/></svg>',
    heartf: '<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 20.5S3.5 15 3.5 9A4.7 4.7 0 0 1 12 6.6 4.7 4.7 0 0 1 20.5 9c0 6-8.5 11.5-8.5 11.5z"/></svg>',
    share: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V3M8 7l4-4 4 4M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1"/></svg>',
    chev: '<svg class="chev" viewBox="0 0 9 15" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m1.5 1.5 6 6-6 6"/></svg>'
  };

  /* ---------- helpers ---------- */
  function seg(items, sel, id) {
    var i = Math.max(0, items.findIndex(function (x) { return x[0] === sel; }));
    return '<div class="seg" data-seg="' + id + '"><span class="thumb" style="width:calc((100% - 6px)/' + items.length + ');transform:translateX(' + i * 100 + '%)"></span>' + items.map(function (x) { return '<button data-v="' + x[0] + '">' + x[1] + '</button>'; }).join('') + '</div>';
  }
  function favBtn(slug, cls) { return '<span class="glassbtn fav ' + (cls || '') + (favs.indexOf(slug) > -1 ? ' on' : '') + '" data-fav="' + slug + '" role="button" aria-label="В избранное">' + (favs.indexOf(slug) > -1 ? I.heartf : I.heart) + '</span>'; }
  var SPN = { spring: 'Весна', summer: 'Лето', autumn: 'Осень', winter: 'Зима' };
  function plates(t) {
    var k = t.seasons;
    return k.length === 1 ? '<span class="sp sp-' + k[0] + '"><b>' + SPN[k[0]] + '</b> ' + esc(t.season) + '</span>'
      : k.map(function (s) { return '<span class="sp sp-' + s + '"><b>' + SPN[s] + '</b></span>'; }).join('') + '<span>' + esc(t.season) + '</span>';
  }
  function tcard(t, wide) {
    return '<a class="tcard' + (wide ? ' wide' : '') + '" href="#/tour/' + t.slug + '"><img src="' + img(t.card_img, wide ? 'l' : 'm') + '" alt="" loading="lazy">' + favBtn(t.slug) +
      '<div class="in"><span class="badge">' + esc(t.badge) + '</span><h3>' + esc(t.title) + '</h3><p>' + esc(t.points ? t.points.join(' · ') : t.card_title) + '</p><div class="meta"><span>' + esc(t.facts[0][0]) + ' ' + esc(t.facts[0][1]) + '</span>' + plates(t) + '</div></div></a>';
  }
  function toast(msg) { var t = $('.toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toast.h); toast.h = setTimeout(function () { t.classList.remove('on'); }, 2000); }
  function buzz() { try { navigator.vibrate && navigator.vibrate(8); } catch (e) { } }

  /* ---------- screens ---------- */
  function nowMonth() { return new Date().getMonth() + 1; }
  function inSeason(m) { return T.filter(function (t) { return t.months.indexOf(m) > -1; }); }

  function viewHome() {
    var m = nowMonth(), now = inSeason(m), g = T[0];
    var lakes = g.lakes.map(function (l) { return '<div class="tcard lakecard"><img src="' + img(l.img, 'm') + '" alt="" loading="lazy" style="object-position:' + l.pos + '"><div class="in"><span class="badge">' + esc(l.alt) + '</span><h3>' + esc(l.name) + '</h3></div></div>'; }).join('');
    var reel = [['issyk', 'Иссык-Куль'], ['bars', 'Барскоон'], ['aksai', 'Ак-Сай'], ['serp', '«33 попугая»'], ['song', 'Сон-Куль'], ['jeti', 'Джети-Огуз']].map(function (v) { return '<div class="vcard"><video muted loop playsinline preload="none" poster="' + V + v[0] + '.jpg"><source src="' + V + v[0] + '.mp4" type="video/mp4"></video><span>' + v[1] + '</span></div>'; }).join('');
    return '<div class="topline"><img class="logo" src="../../assets/logo.svg" alt="VOYZ"><span class="glassbtn" data-sheet="request" role="button" aria-label="Заявка">' + I.send + '</span></div>' +
      '<div class="hero"><img src="' + img(g.hero, 'l') + '" alt="" style="object-position:' + g.hero_pos + '"><video muted loop playsinline preload="auto" poster="' + V + 'hero.jpg"><source src="' + V + 'hero.mp4" type="video/mp4"></video>' +
      '<div class="in"><span class="eyebrow">Кыргызстан · на внедорожниках</span><h1>Туда, куда не доезжает <em>автобус</em></h1><p>Небольшие группы, продуманные маршруты и поездки в любое время года.</p><a class="btn" href="#/tour/grand-expedition">Смотреть экспедицию</a></div></div>' +
      '<div class="statrow"><div class="stat"><b>' + T.length + '</b><span>маршрутов</span></div><div class="stat"><b>12</b><span>месяцев</span></div><div class="stat"><b>2</b><span>внедорож.</span></div><div class="stat"><b>4–8</b><span>человек</span></div></div>' +
      '<h2 class="h2">Сейчас в сезоне<small>' + MFULL[m - 1] + '</small></h2><div class="hscroll">' + (now.length ? now : T.slice(0, 3)).map(function (t) { return tcard(t); }).join('') + '</div>' +
      '<h2 class="h2">Три озера</h2><div class="hscroll">' + lakes + '</div>' +
      '<h2 class="h2">В движении</h2><div class="hscroll">' + reel + '</div>' +
      '<div class="grouplabel">Частые вопросы</div>' + g.faq.slice(0, 5).map(faq).join('') +
      '<p class="footnote"><a href="../index.html?full=1" data-full>Полная версия сайта</a></p>';
  }
  function faq(f) { return '<div class="faq"><button>' + esc(f[0]) + I.chev + '</button><div class="a"><div><p>' + esc(f[1]) + '</p></div></div></div>'; }

  var tourSeason = 'all';
  function viewTours() {
    var list = T.filter(function (t) { return tourSeason === 'all' || t.seasons.indexOf(tourSeason) > -1; });
    return '<h1 class="largetitle">Туры</h1><p class="sub">Авторские экспедиции на весь год</p>' + seg(SEASONS, tourSeason, 'season') +
      '<div id="tourlist">' + (list.length ? list.map(function (t) { return tcard(t, true); }).join('') : '<p class="sub">В этом сезоне пока нет маршрутов.</p>') + '</div>' +
      '<div class="grouplabel">Не нашли свой?</div><div class="group"><a class="row" data-sheet="request" data-tour="Свой маршрут"><span class="ico">+</span><div class="t"><b>Соберём маршрут под вас</b><span>Другие даты, компания, длительность</span></div>' + I.chev + '</a></div>';
  }
  var selMonth = nowMonth();
  function viewCal() {
    var mon = MONTHS.map(function (n, i) { var m = i + 1, c = inSeason(m).length; return '<button class="mon' + (c ? ' has' : '') + (m === selMonth ? ' sel' : '') + '" data-m="' + m + '">' + n + '<small>' + c + ' ' + (c === 1 ? 'тур' : 'тура') + '</small></button>'; }).join('');
    return '<h1 class="largetitle">Календарь</h1><p class="sub">Выберите месяц и посмотрите, куда поехать</p><div class="months">' + mon + '</div><div id="calres">' + calRes() + '</div>';
  }
  function calRes() {
    var l = inSeason(selMonth);
    return '<div class="grouplabel">' + MFULL[selMonth - 1] + '</div>' + (l.length ? '<div class="group">' + l.map(function (t) { return '<a class="row" href="#/tour/' + t.slug + '"><span class="ico" style="background:none;padding:0;width:56px;height:56px;border-radius:14px;overflow:hidden"><img src="' + img(t.card_img) + '" style="width:100%;height:100%;object-fit:cover" alt=""></span><div class="t"><b>' + esc(t.title) + '</b><span>' + esc(t.card_title) + '</span></div>' + I.chev + '</a>'; }).join('') + '</div>' : '<p class="small">В этом месяце маршрутов нет, но мы можем собрать поездку под вас.</p><div class="wrapx"><a class="btn block" data-sheet="request" data-tour="Свой маршрут">Обсудить маршрут</a></div>');
  }
  function viewReq() {
    var fl = favs.map(by).filter(Boolean);
    return '<h1 class="largetitle">Заявка</h1><p class="sub">Вернёмся с программой и расчётом под вашу группу и даты</p>' + formHTML('') +
      (fl.length ? '<div class="grouplabel">Вам понравилось</div><div class="group">' + fl.map(function (t) { return '<a class="row" href="#/tour/' + t.slug + '"><div class="t"><b>' + esc(t.title) + '</b><span>' + esc(t.season) + '</span></div>' + I.chev + '</a>'; }).join('') + '</div>' : '') +
      '<div class="contacts"></div>';
  }
  var season2 = ['Весна', 'Лето', 'Осень', 'Зима'];
  function formHTML(tour) {
    return '<form data-form data-tour="' + esc(tour) + '" novalidate>' +
      '<div class="group"><div class="field"><label>Имя</label><input name="name" autocomplete="name" placeholder="Как вас зовут"></div><div class="field"><label>Контакт</label><input name="contact" autocomplete="tel" placeholder="Telegram, телефон, почта"></div></div>' +
      '<div class="grouplabel">Когда хотите поехать</div>' + seg([['Весна', 'Весна'], ['Лето', 'Лето'], ['Осень', 'Осень'], ['Зима', 'Зима']], '', 'fseason') +
      '<div class="group"><div class="field"><label>Человек</label><div class="stepper"><button type="button" data-step="-1">−</button><b data-people>2</b><button type="button" data-step="1">+</button></div></div><div class="field"><textarea name="comment" placeholder="Пожелания: опыт, дети, сроки, вопросы"></textarea></div></div>' +
      '<div class="group"><div class="field"><label style="width:auto;flex:1;font-size:15px">Согласен на обработку данных</label><span class="toggle" data-toggle role="switch"></span></div></div>' +
      '<p class="small">Нажимая «Отправить», вы принимаете <a href="../privacy/">политику конфиденциальности</a>.</p><div class="wrapx"><button class="btn block" type="submit">Отправить заявку</button></div><div class="ok"></div></form>';
  }

  function viewTour(t) {
    var vk = VID[t.slug], hero = vk ? '<video muted loop playsinline preload="auto" poster="' + V + vk + '.jpg"><source src="' + V + vk + '.mp4" type="video/mp4"></video>' : '';
    var lakes = t.lakes.map(function (l) { return '<div class="tcard lakecard"><img src="' + img(l.img, 'm') + '" alt="" loading="lazy" style="object-position:' + l.pos + '"><div class="in"><span class="badge">' + esc(l.alt) + '</span><h3>' + esc(l.name) + '</h3><p>' + esc(l.text) + '</p></div></div>'; }).join('');
    var days = t.days.map(function (d, i) {
      return '<div class="day' + (i === 0 ? ' open' : '') + '"><button class="head"><span class="num">' + d.n + '</span><span><b>' + esc(d.title) + '</b><span>' + esc(d.route) + '</span></span>' + I.chev + '</button><div class="more"><div><div class="pic"><img src="' + img(d.img) + '" alt="" loading="lazy" style="object-position:' + d.pos + '"><span>' + esc(d.caption) + '</span></div><div class="txt"><p class="body">' + esc(d.text) + '</p><div class="chips" style="margin-top:12px">' + d.moments.map(function (m) { return '<span class="chip">' + esc(m) + '</span>'; }).join('') + '</div>' + (d.note ? '<p class="note">' + esc(d.note) + '</p>' : '') + '<p class="stay"><b>Ночёвка:</b> ' + esc(d.stay) + '</p></div></div></div></div>';
    }).join('');
    var diff = t.difficulty.map(function (x) { return '<div class="row"><div class="t"><b>' + esc(x.name) + '</b><span>' + esc(x.text) + '</span><div class="meter">' + [0, 1, 2, 3, 4].map(function (i) { return '<i class="' + (i < x.level ? 'on' : '') + '"></i>'; }).join('') + '</div></div></div>'; }).join('');
    var map = t.map ? '<h2 class="h2">Маршрут</h2><div class="mapcard"><img src="../../assets/map/map-m.webp" alt="Карта маршрута"><div data-overlay></div></div><div class="legend"><span>━ Переезды</span><span>┅ Возвращение</span><span>┅ Верхом и пешком</span></div><p class="small" style="margin:8px 20px 0">Схема показывает порядок маршрута, это не дорожная карта.</p>' : '';
    return '<div class="floating"><span class="glassbtn" data-back role="button" aria-label="Назад">' + I.back + '</span><span style="display:flex;gap:10px"><span class="glassbtn" data-share role="button" aria-label="Поделиться">' + I.share + '</span>' + favBtn(t.slug) + '</span></div>' +
      '<div class="thero"><img src="' + img(t.hero, 'l') + '" alt="" style="object-position:' + t.hero_pos + '">' + hero + '</div>' +
      '<div class="sheetbody"><div class="metaline" style="margin-bottom:0"><span class="chip lime">' + esc(t.badge) + '</span>' + plates(t) + '</div><h1 class="tt">' + esc(t.title) + '</h1><p class="lead">' + esc(t.headline) + '.</p>' +
      '<div class="statrow" style="margin-top:0">' + t.facts.map(function (f) { return '<div class="stat"><b>' + esc(f[0]) + '</b><span>' + esc(f[1]) + '</span></div>'; }).join('') + '</div>' +
      '<h2 class="h2">Что увидите</h2><div class="hscroll">' + lakes + '</div>' + map +
      '<h2 class="h2">Программа<small>' + t.days.length + ' дней</small></h2>' + days +
      '<h2 class="h2">Для кого</h2><div class="group">' + t.fit_yes.map(function (x) { return '<div class="fitrow">' + esc(x) + '</div>'; }).join('') + '</div><div class="group">' + t.fit_no.map(function (x) { return '<div class="fitrow no">' + esc(x) + '</div>'; }).join('') + '</div>' +
      '<div class="grouplabel">Сложность</div><div class="group">' + diff + '</div><p class="small">' + esc(t.difficulty_note) + '</p>' +
      '<div class="grouplabel">Организация</div><div class="group">' + t.organization.map(function (o) { return '<div class="row"><div class="t"><b>' + esc(o[0]) + '</b><span>' + esc(o[1]) + '</span></div></div>'; }).join('') + '</div><p class="small">' + esc(t.organization_note) + '</p>' +
      '<h2 class="h2">Вопросы</h2>' + t.faq.map(faq).join('') +
      '<h2 class="h2">Ещё поездки</h2><div class="hscroll">' + T.filter(function (x) { return x !== t; }).map(function (x) { return tcard(x); }).join('') + '</div></div>' +
      '<div class="cta"><a class="btn" data-sheet="request" data-tour="' + esc(t.title) + '">Узнать стоимость и даты</a></div>';
  }

  /* ---------- shell & router ---------- */
  var TABS = [['home', 'Главная', I.home, '#/'], ['tours', 'Туры', I.tours, '#/tours'], ['cal', 'Календарь', I.cal, '#/calendar'], ['req', 'Заявка', I.send, '#/request']];
  phone.innerHTML = '<div class="statusbar"><span>9:41</span><span>●●● ▮</span></div><div class="screens"></div><nav class="tabbar">' + TABS.map(function (t) { return '<a class="tab" data-tab="' + t[0] + '" href="' + t[3] + '">' + t[2] + '<span>' + t[1] + '</span></a>'; }).join('') + '</nav><div class="scrim"></div><div class="sheet" role="dialog" aria-modal="true"><div class="grab"></div><div class="sc"></div></div><div class="toast"></div>';
  var screens = $('.screens'), tabbar = $('.tabbar'), cache = {};
  var views = { home: viewHome, tours: viewTours, cal: viewCal, req: viewReq };
  var scrolls = {};

  function mkScreen(id, html, push) {
    var el = document.createElement('div'); el.className = 'screen' + (push ? ' push enter' : ' hidden'); el.dataset.id = id;
    el.innerHTML = (push ? '' : '<div class="navbar"></div>') + html; screens.appendChild(el); bind(el); return el;
  }
  function bind(el) {
    var vids = $$('video', el);
    vids.forEach(function (v) { if (RM) return; var hv = v.closest('.hero,.thero'); if (hv) { var go = function () { v.play().then(function () { v.classList.add('on'); }).catch(function () { }); }; if (v.readyState >= 3) go(); else v.addEventListener('canplay', go, { once: true }); } });
    if ('IntersectionObserver' in window && !RM) { var io = new IntersectionObserver(function (es) { es.forEach(function (e) { var v = e.target; if (e.isIntersecting) { v.play().catch(function () { }); } else v.pause(); }); }, { root: el, threshold: .3 }); $$('.vcard video', el).forEach(function (v) { io.observe(v); }); }
    var title = $('.largetitle', el), nb = $('.navbar', el);
    el.addEventListener('scroll', function () {
      var y = el.scrollTop;
      if (nb && title) { nb.textContent = title.textContent; nb.classList.toggle('on', y > 44); }
      var th = $('.thero', el); if (th) { var im = $('img', th), vd = $('video', th); var tr = 'translate3d(0,' + (y * .35).toFixed(1) + 'px,0) scale(' + (1 + Math.max(0, -y) / 600) + ')'; im.style.transform = tr; if (vd) vd.style.transform = tr; }
    }, { passive: true });
    var ov = $('[data-overlay]', el);
    if (ov) fetch('../../assets/map/overlay-m.svg').then(function (r) { return r.text(); }).then(function (s) { ov.innerHTML = s; var svg = $('svg', ov); if (!svg || RM) return; var solid = $$('path', svg).filter(function (p) { return p.getAttribute('stroke') && !p.getAttribute('stroke-dasharray') && !p.getAttribute('transform') && parseFloat(p.getAttribute('stroke-width')) > 2; }); solid.forEach(function (p) { p.setAttribute('pathLength', '1000'); p.style.strokeDasharray = '1000'; p.style.strokeDashoffset = '1000'; p.style.transition = 'stroke-dashoffset 2.4s cubic-bezier(.4,.1,.2,1)'; }); $$('circle,rect,text,ellipse', svg).forEach(function (e) { e.style.opacity = 0; e.style.transition = 'opacity .6s'; }); var mo = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { solid.forEach(function (p, i) { setTimeout(function () { p.style.strokeDashoffset = 0; }, i * 100); }); setTimeout(function () { $$('circle,rect,text,ellipse', svg).forEach(function (e) { e.style.opacity = 1; }); }, 900); mo.disconnect(); } }, { root: el, threshold: .3 }); mo.observe(svg); jeepify(svg, el); });
  }
  function jeepify(svg, scroller) { if (window.voyzJeep) window.voyzJeep(svg, scroller, RM); }
  function setTab(id) { $$('.tab').forEach(function (t) { t.classList.toggle('on', t.dataset.tab === id); }); }
  function rerender(id) { var el = cache[id]; if (!el) return; var y = el.scrollTop; el.innerHTML = '<div class="navbar"></div>' + views[id](); bind(el); el.scrollTop = y; }

  var stack = [];  // push screens
  function route() {
    var h = location.hash.replace(/^#/, '') || '/', p = h.split('/').filter(Boolean);
    var tab = p[0] === 'tours' ? 'tours' : p[0] === 'calendar' ? 'cal' : p[0] === 'request' ? 'req' : 'home';
    if (p[0] === 'tour' && by(p[1])) { openTour(by(p[1])); return; }
    closePush();
    showTab(tab);
  }
  function showTab(id) {
    if (!cache[id]) cache[id] = mkScreen(id, views[id]());
    else if (id === 'req' || id === 'tours') rerender(id);
    Object.keys(cache).forEach(function (k) { cache[k].classList.toggle('hidden', k !== id); cache[k].classList.remove('under'); });
    setTab(id); tabbar.classList.remove('hide'); cache[id].scrollTop = scrolls[id] || 0; current = id; hydrateContacts(cache[id]);
  }
  var current = 'home', pushed = null;
  function openTour(t) {
    if (pushed && pushed.dataset.id === t.slug) return;
    closePush(true);
    var el = mkScreen(t.slug, viewTour(t), true); pushed = el;
    if (cache[current]) { scrolls[current] = cache[current].scrollTop; cache[current].classList.add('under'); }
    tabbar.classList.add('hide');
    requestAnimationFrame(function () { requestAnimationFrame(function () { el.classList.remove('enter'); }); });
    el.addEventListener('scroll', function () { $('.floating', el).style.opacity = 1; });
  }
  function closePush(instant) {
    if (!pushed) return; var el = pushed; pushed = null;
    if (cache[current]) cache[current].classList.remove('under');
    if (instant || RM) { el.remove(); return; }
    el.classList.add('leave'); tabbar.classList.remove('hide'); setTimeout(function () { el.remove(); }, 520);
  }
  var inApp = 0, lastH = location.hash;
  addEventListener('hashchange', function () { var f = location.hash; if (f !== lastH) { inApp += (f.length > lastH.length || f.indexOf('#/tour/') === 0) ? 1 : -1; if (inApp < 0) inApp = 0; } lastH = f; route(); });

  /* ---------- sheet ---------- */
  var sheet = $('.sheet'), scrim = $('.scrim');
  function openSheet(tour) {
    $('.sc', sheet).innerHTML = '<h2>Расскажем всё и посчитаем</h2><p class="sub">' + (tour ? 'Тур: ' + esc(tour) + '. ' : '') + 'Оставьте контакты, мы вернёмся с программой и расчётом.</p>' + formHTML(tour || '');
    bindForm($('.sc', sheet)); sheet.classList.add('on'); scrim.classList.add('on'); buzz();
  }
  function closeSheet() { sheet.classList.remove('on'); scrim.classList.remove('on'); }
  scrim.addEventListener('click', closeSheet);
  (function () { var y0 = 0, dy = 0, on = false; sheet.addEventListener('touchstart', function (e) { var sc = $('.sc', sheet); if (e.target.closest('.grab') || sc.scrollTop <= 0) { on = true; y0 = e.touches[0].clientY; dy = 0; } }, { passive: true });
    sheet.addEventListener('touchmove', function (e) { if (!on) return; dy = e.touches[0].clientY - y0; if (dy > 0) { sheet.classList.add('drag'); sheet.style.transform = 'translateY(' + dy + 'px)'; } }, { passive: true });
    sheet.addEventListener('touchend', function () { if (!on) return; on = false; sheet.classList.remove('drag'); sheet.style.transform = ''; if (dy > 110) closeSheet(); }); })();

  /* ---------- forms ---------- */
  function bindForm(root) {
    $$('form[data-form]', root).forEach(function (f) {
      if (f.dataset.bound) return; f.dataset.bound = 1; var people = 2, agree = false, season = '';
      f.addEventListener('click', function (e) {
        var st = e.target.closest('[data-step]'); if (st) { people = Math.max(1, Math.min(12, people + (+st.dataset.step))); $('[data-people]', f).textContent = people; buzz(); }
        var tg = e.target.closest('[data-toggle]'); if (tg) { agree = !agree; tg.classList.toggle('on', agree); buzz(); }
        var sb = e.target.closest('[data-seg="fseason"] button'); if (sb) season = sb.dataset.v;
      });
      f.addEventListener('submit', function (e) {
        e.preventDefault(); var bad = false;
        $$('input[name=name],input[name=contact]', f).forEach(function (i) { var b = !i.value.trim(); i.closest('.field').classList.toggle('bad', b); if (b) bad = true; });
        if (!agree) { bad = true; toast('Нужно согласие на обработку данных'); }
        if (bad) { buzz(); return; }
        var d = { name: f.name.value, contact: f.contact.value, season: season || '—', people: people, comment: f.comment.value, tour: f.dataset.tour || '', page: location.href, at: new Date().toISOString(), source: 'app' };
        var text = [tx('Заявка VOYZ (приложение)'), tl('Тур: ') + (d.tour || tx('не выбран')), tl('Имя: ') + d.name, tl('Контакт: ') + d.contact, tl('Сезон: ') + d.season, tl('Человек: ') + d.people, d.comment ? tl('Комментарий: ') + d.comment : ''].filter(Boolean).join('\n');
        var done = function (live) {
          $$('.group,.grouplabel,.seg,.small,.wrapx', f).forEach(function (x) { x.style.display = 'none'; });
          var ok = $('.ok', f); ok.style.display = 'block'; ok.innerHTML = live ? '<b>Заявка отправлена.</b> Мы вернёмся с программой и расчётом.' : '<b>Заявка собрана.</b> Форма в демо-режиме: скопируйте текст и отправьте нам.<br><br><button type="button" class="btn" data-copy>Скопировать заявку</button>';
          var cp = $('[data-copy]', ok); if (cp) cp.addEventListener('click', function () { (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () { toast('Скопировано'); }).catch(function () { toast('Выделите текст вручную'); }); });
          buzz();
        };
        if (C.formEndpoint) fetch(C.formEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(d) }).then(function (r) { if (!r.ok) throw 0; done(true); }).catch(function () { toast('Не удалось отправить, попробуйте ещё раз'); });
        else { var q = store('voyz_requests') || []; q.push(d); store('voyz_requests', q); done(false); }
      });
    });
  }
  function hydrateContacts(el) {
    var box = $('.contacts', el); if (!box || box.dataset.done) return; box.dataset.done = 1; var rows = [];
    if (C.telegram) rows.push(['Telegram', 'https://t.me/' + C.telegram.replace(/^@/, '')]); if (C.whatsapp) rows.push(['WhatsApp', 'https://wa.me/' + C.whatsapp.replace(/\D/g, '')]); if (C.phone) rows.push(['Позвонить', 'tel:' + C.phone.replace(/[^\d+]/g, '')]); if (C.email) rows.push(['Почта', 'mailto:' + C.email]);
    if (rows.length) box.innerHTML = '<div class="grouplabel">Написать напрямую</div><div class="group">' + rows.map(function (r) { return '<a class="row" href="' + r[1] + '" target="_blank" rel="noopener"><div class="t"><b>' + r[0] + '</b></div>' + I.chev + '</a>'; }).join('') + '</div>';
  }

  /* ---------- global events ---------- */
  phone.addEventListener('click', function (e) {
    var t = e.target;
    var fv = t.closest('[data-fav]'); if (fv) { e.preventDefault(); e.stopPropagation(); var s = fv.dataset.fav, i = favs.indexOf(s); if (i > -1) favs.splice(i, 1); else { favs.push(s); toast('Добавлено в «Заявка → Вам понравилось»'); } store('voyz_favs', favs); buzz(); $$('[data-fav="' + s + '"]').forEach(function (b) { var on = favs.indexOf(s) > -1; b.classList.toggle('on', on); b.innerHTML = on ? I.heartf : I.heart; }); if (cache.req) rerender('req'); return; }
    if (t.closest('[data-back]')) { e.preventDefault(); inApp > 0 ? history.back() : (location.hash = '#/tours'); return; }
    var sh = t.closest('[data-share]'); if (sh) { var d = { title: 'VOYZ · ' + (pushed && by(pushed.dataset.id).title), url: location.href }; if (navigator.share) navigator.share(d).catch(function () { }); else { (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () { toast('Ссылка скопирована'); }).catch(function () { }); } return; }
    var op = t.closest('[data-sheet]'); if (op) { e.preventDefault(); openSheet(op.dataset.tour || (pushed ? by(pushed.dataset.id).title : '')); return; }
    var fa = t.closest('.faq > button'); if (fa) { fa.parentNode.classList.toggle('open'); buzz(); return; }
    var dh = t.closest('.day > .head'); if (dh) { dh.parentNode.classList.toggle('open'); buzz(); return; }
    var sb = t.closest('.seg button'); if (sb) { var sg = sb.parentNode, bs = $$('button', sg), i2 = bs.indexOf(sb); $('.thumb', sg).style.transform = 'translateX(' + i2 * 100 + '%)'; if (sg.dataset.seg === 'season') { tourSeason = sb.dataset.v; var l = T.filter(function (x) { return tourSeason === 'all' || x.seasons.indexOf(tourSeason) > -1; }); $('#tourlist').innerHTML = l.length ? l.map(function (x) { return tcard(x, true); }).join('') : '<p class="sub">В этом сезоне пока нет маршрутов.</p>'; } buzz(); return; }
    var mo = t.closest('.mon'); if (mo) { selMonth = +mo.dataset.m; $$('.mon').forEach(function (m) { m.classList.toggle('sel', m === mo); }); $('#calres').innerHTML = calRes(); buzz(); return; }
    var fl = t.closest('[data-full]'); if (fl) { try { sessionStorage.setItem('voyz_full', '1'); } catch (x) { } }
  });
  // forms rendered on tab screens
  new MutationObserver(function () { bindForm(screens); }).observe(screens, { childList: true, subtree: true });

  // scroll position bookkeeping for tab screens
  screens.addEventListener('scroll', function (e) { if (e.target.dataset && cache[e.target.dataset.id]) scrolls[e.target.dataset.id] = e.target.scrollTop; }, true);

  if (EN) {
    new MutationObserver(function (ms) { ms.forEach(function (m) { [].slice.call(m.addedNodes).forEach(function (n) { trTree(n); }); if (m.type === 'characterData') trTree(m.target); }); }).observe(phone, { childList: true, subtree: true, characterData: true });
  }
  route(); bindForm(screens);
  if (EN) trTree(phone);
})();

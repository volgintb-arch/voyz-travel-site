(function () {
  var EN = document.documentElement.lang === 'en';
  var S = EN ? {
    subject: 'Request from the VOYZ website', hello: 'Hello! I would like to know more about ', defTopic: 'VOYZ tours',
    head: 'VOYZ request', tour: 'Tour: ', none: 'not chosen', name: 'Name: ', contact: 'Contact: ', season: 'Season: ', people: 'People: ', comment: 'Comment: ',
    sent: '<strong>Request sent.</strong> We will come back with a program and a quote.',
    demo: '<strong>Request prepared.</strong> The form is in demo mode right now: copy the text and send it to us.<br><button type="button" class="btn sm dark" data-copy style="margin-top:14px">Copy request</button>',
    copied: 'Copied', manual: 'Select the text manually', fail: 'Could not send. Please try again or contact us directly.'
  } : {
    subject: 'Заявка с сайта VOYZ', hello: 'Здравствуйте! Хочу узнать про ', defTopic: 'туры VOYZ',
    head: 'Заявка VOYZ', tour: 'Тур: ', none: 'не выбран', name: 'Имя: ', contact: 'Контакт: ', season: 'Сезон: ', people: 'Человек: ', comment: 'Комментарий: ',
    sent: '<strong>Заявка отправлена.</strong> Мы вернёмся с программой и расчётом.',
    demo: '<strong>Заявка собрана.</strong> Форма сейчас в демо-режиме: скопируйте текст и отправьте нам.<br><button type="button" class="btn sm dark" data-copy style="margin-top:14px">Скопировать заявку</button>',
    copied: 'Скопировано', manual: 'Выделите текст вручную', fail: 'Не удалось отправить. Попробуйте ещё раз или свяжитесь с нами напрямую.'
  };
  var MON = EN ? ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] : ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  var C = window.VOYZ_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // header state + mobile bar
  var hdr = $('.hdr'), mbar = $('.mbar');
  function onScroll() {
    var y = window.scrollY;
    if (hdr) hdr.classList.toggle('solid', y > 40);
    if (mbar) mbar.classList.toggle('show', y > window.innerHeight * .6);
    var bg = $('.hero .bg');
    if (bg && y < window.innerHeight * 1.2 && !matchMedia('(prefers-reduced-motion: reduce)').matches) bg.style.transform = 'translate3d(0,' + (y * .18) + 'px,0)';
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // mobile nav
  var mn = $('.mnav');
  $$('[data-menu]').forEach(function (b) { b.addEventListener('click', function () { mn.classList.toggle('open'); document.body.style.overflow = mn.classList.contains('open') ? 'hidden' : ''; }); });
  $$('.mnav a').forEach(function (a) { a.addEventListener('click', function () { mn.classList.remove('open'); document.body.style.overflow = ''; }); });

  // reveal on scroll
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { threshold: .12 }) : null;
  $$('.rv').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });

  // subnav highlight
  var links = $$('.subnav a.l');
  if (links.length && 'IntersectionObserver' in window) {
    var map = {}; links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var so = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (l) { l.classList.remove('on'); }); var a = map[e.target.id]; if (a) a.classList.add('on'); } }); }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) so.observe(s); });
  }

  // modal
  var modal = $('.modal');
  function openModal(src) { if (!modal) return; var f = $('form', modal); if (f && src) f.dataset.source = src; modal.classList.add('open'); document.body.style.overflow = 'hidden'; var i = $('input', modal); if (i) setTimeout(function () { i.focus(); }, 50); }
  function closeModal() { if (!modal) return; modal.classList.remove('open'); document.body.style.overflow = ''; }
  $$('[data-open-form]').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); openModal(b.getAttribute('data-open-form')); }); });
  if (modal) { modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); }); $('.close', modal).addEventListener('click', closeModal); }
  addEventListener('keydown', function (e) { if (e.key === 'Escape') closeModal(); });

  // contact buttons from config (hidden when not configured, never fake)
  function contactHref(kind, text) {
    if (kind === 'telegram' && C.telegram) return 'https://t.me/' + C.telegram.replace(/^@/, '') + '?text=' + encodeURIComponent(text);
    if (kind === 'whatsapp' && C.whatsapp) return 'https://wa.me/' + C.whatsapp.replace(/\D/g, '') + '?text=' + encodeURIComponent(text);
    if (kind === 'phone' && C.phone) return 'tel:' + C.phone.replace(/[^\d+]/g, '');
    if (kind === 'email' && C.email) return 'mailto:' + C.email + '?subject=' + encodeURIComponent(S.subject) + '&body=' + encodeURIComponent(text);
    return null;
  }
  $$('[data-contact]').forEach(function (a) {
    var h = contactHref(a.getAttribute('data-contact'), S.hello + (a.getAttribute('data-topic') || S.defTopic));
    if (h) { a.href = h; a.hidden = false; if (/^http/.test(h)) { a.target = '_blank'; a.rel = 'noopener'; } }
  });
  $$('[data-if-contacts]').forEach(function (el) { if (!(C.telegram || C.whatsapp || C.phone || C.email)) el.hidden = true; });

  // forms
  $$('form[data-request]').forEach(function (form) {
    var consent = $('[name=consent]', form);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      $$('[required]', form).forEach(function (f) { var bad = f.type === 'checkbox' ? !f.checked : !f.value.trim(); f.closest('.field,.consent').classList.toggle('bad', bad); if (bad) ok = false; });
      if (!ok) { var first = $('.bad input,.bad select', form); if (first) first.focus(); return; }
      var d = {}; new FormData(form).forEach(function (v, k) { d[k] = v; });
      d.tour = form.dataset.tour || ''; d.source = form.dataset.source || location.pathname; d.page = location.href; d.at = new Date().toISOString();
      var text = [S.head, S.tour + (d.tour || S.none), S.name + d.name, S.contact + d.contact, S.season + (d.month || '—'), S.people + (d.people || '—'), d.comment ? S.comment + d.comment : ''].filter(Boolean).join(String.fromCharCode(10));
      var done = function (live) {
        form.classList.add('sent');
        var m = $('.ok', form); if (m) m.innerHTML = live ? S.sent : S.demo;
        var cp = $('[data-copy]', form); if (cp) cp.addEventListener('click', function () { (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () { cp.textContent = S.copied; }).catch(function () { cp.textContent = S.manual; }); });
      };
      if (C.formEndpoint) {
        fetch(C.formEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(d) })
          .then(function (r) { if (!r.ok) throw 0; done(true); })
          .catch(function () { alert(S.fail); });
      } else { try { var q = JSON.parse(localStorage.getItem('voyz_requests') || '[]'); q.push(d); localStorage.setItem('voyz_requests', JSON.stringify(q)); } catch (x) {} done(false); }
    });
  });
})();

// season filter in the catalog
(function(){
  var chips=[].slice.call(document.querySelectorAll('.fchip')); if(!chips.length) return;
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.toggle('on',x===c)});
    var s=c.getAttribute('data-season');
    [].slice.call(document.querySelectorAll('#tgrid .tcard')).forEach(function(card){
      var ok=s==='all'||(card.getAttribute('data-seasons')||'').split(' ').indexOf(s)>-1;
      if(card.classList.contains('custom')) ok=true;
      card.hidden=!ok;
    });
  });});
})();

// "in season now": show the tours that run in the current month (first three if none do)
  (function () {
    var g = document.getElementById('nowgrid'); if (!g) return;
    var MON = document.documentElement.lang === 'en' ? ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] : ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
    var m = new Date().getMonth() + 1, cards = Array.prototype.slice.call(g.children).filter(function (c) { return c.classList.contains('tcard'); });
    var hit = cards.filter(function (c) { return (' ' + c.dataset.months + ' ').indexOf(' ' + m + ' ') > -1; });
    var lbl = document.getElementById('nowm'); if (lbl) { if (hit.length) lbl.textContent = MON[m - 1]; else lbl.parentNode.removeChild(lbl); }
    var show = hit.length ? hit : cards.slice(0, 3); show.forEach(function (c) { c.hidden = false; }); g.className += ' n' + Math.min(show.length, 3);
  })();

// tour row: arrows, mouse drag (grab cursor) and a hand hint that goes away after the first interaction
(function () {
  var row = document.getElementById('trow'); if (!row) return;
  var wrap = row.parentNode, down = false, sx = 0, sl = 0, moved = 0;
  function used() { wrap.classList.add('used'); }
  Array.prototype.slice.call(document.querySelectorAll('[data-hnav]')).forEach(function (b) {
    b.addEventListener('click', function () {
      used(); var c = row.querySelector('.tcard'), w = c ? c.getBoundingClientRect().width + 16 : 320;
      row.scrollBy({ left: w * Number(b.getAttribute('data-hnav')), behavior: 'smooth' });
    });
  });
  row.addEventListener('scroll', function () { if (row.scrollLeft > 20) used(); }, { passive: true });
  row.addEventListener('mousedown', function (e) { if (e.button !== 0) return; down = true; moved = 0; sx = e.pageX; sl = row.scrollLeft; });
  window.addEventListener('mouseup', function () { down = false; row.classList.remove('drag'); });
  window.addEventListener('mousemove', function (e) {
    if (!down) return; var dx = e.pageX - sx; moved = Math.max(moved, Math.abs(dx));
    if (moved > 6) { row.classList.add('drag'); used(); row.scrollLeft = sl - dx; }
  });
  // a real click on a card opens it; only a drag is swallowed
  row.addEventListener('click', function (e) { if (moved > 6) { e.preventDefault(); e.stopPropagation(); } moved = 0; }, true);
  row.addEventListener('dragstart', function (e) { e.preventDefault(); });
})();

// lightbox: photo slides for a place, or a video
(function () {
  var L = EN0() ? { close: 'Close', prev: 'Previous', next: 'Next', of: ' of ' } : { close: 'Закрыть', prev: 'Назад', next: 'Вперёд', of: ' из ' };
  function EN0() { return document.documentElement.lang === 'en'; }
  var box = null, st, cap, th, imgs = [], idx = 0, lastFocus = null, startX = 0;
  function build() {
    box = document.createElement('div'); box.className = 'lb'; box.hidden = true; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true');
    box.innerHTML = '<button type="button" class="lb-x" aria-label="' + L.close + '">×</button><button type="button" class="lb-p" aria-label="' + L.prev + '">←</button><button type="button" class="lb-n" aria-label="' + L.next + '">→</button>' +
      '<div class="lb-stage"></div><div class="lb-cap"><b></b><span></span></div><div class="lb-th"></div>';
    document.body.appendChild(box); st = box.querySelector('.lb-stage'); cap = box.querySelector('.lb-cap'); th = box.querySelector('.lb-th');
    box.querySelector('.lb-x').addEventListener('click', close);
    box.querySelector('.lb-p').addEventListener('click', function () { go(-1); });
    box.querySelector('.lb-n').addEventListener('click', function () { go(1); });
    box.addEventListener('click', function (e) { if (e.target === box || e.target === st) close(); });
    st.addEventListener('pointerdown', function (e) { startX = e.clientX; });
    st.addEventListener('pointerup', function (e) { var dx = e.clientX - startX; if (imgs.length > 1 && Math.abs(dx) > 50) go(dx < 0 ? 1 : -1); });
    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close(); else if (e.key === 'ArrowLeft') go(-1); else if (e.key === 'ArrowRight') go(1);
    });
  }
  function show() {
    st.innerHTML = '<img src="' + imgs[idx] + '" alt="">';
    cap.querySelector('span').textContent = imgs.length > 1 ? (idx + 1) + L.of + imgs.length : '';
    Array.prototype.forEach.call(th.children, function (b, i) { b.classList.toggle('on', i === idx); });
    var nx = new Image(); nx.src = imgs[(idx + 1) % imgs.length];
  }
  function go(d) { if (imgs.length < 2) return; idx = (idx + d + imgs.length) % imgs.length; show(); }
  function open(kind) { if (!box) build(); lastFocus = document.activeElement; box.hidden = false; box.className = 'lb ' + kind; document.body.style.overflow = 'hidden'; requestAnimationFrame(function () { box.classList.add('in'); }); box.querySelector('.lb-x').focus(); }
  function close() {
    if (!box || box.hidden) return; box.classList.remove('in'); var v = st.querySelector('video'); if (v) v.pause();
    setTimeout(function () { box.hidden = true; st.innerHTML = ''; document.body.style.overflow = ''; if (lastFocus && lastFocus.focus) lastFocus.focus(); }, 180);
  }
  function gallery(el) {
    imgs = el.getAttribute('data-gal').split('|'); idx = 0; open('is-gal');
    cap.querySelector('b').textContent = el.getAttribute('data-name') || ''; th.innerHTML = '';
    imgs.forEach(function (u, i) { var b = document.createElement('button'); b.type = 'button'; b.innerHTML = '<img src="' + u.replace('-l.webp', '-m.webp') + '" alt="">'; b.addEventListener('click', function () { idx = i; show(); }); th.appendChild(b); });
    th.style.display = imgs.length > 1 ? '' : 'none'; box.querySelector('.lb-p').style.display = box.querySelector('.lb-n').style.display = imgs.length > 1 ? '' : 'none';
    show();
  }
  function video(el) {
    imgs = []; open('is-vid'); cap.querySelector('b').textContent = el.getAttribute('data-name') || ''; cap.querySelector('span').textContent = ''; th.innerHTML = ''; th.style.display = 'none';
    box.querySelector('.lb-p').style.display = box.querySelector('.lb-n').style.display = 'none';
    st.innerHTML = '<video controls autoplay playsinline loop poster="' + (el.getAttribute('data-poster') || '') + '"><source src="' + el.getAttribute('data-video') + '" type="video/mp4"></video>';
  }
  function trigger(e) {
    var g = e.target.closest && e.target.closest('[data-gal]'); if (g) { e.preventDefault(); gallery(g); return; }
    var v = e.target.closest && e.target.closest('[data-video]'); if (v) { e.preventDefault(); video(v); }
  }
  document.addEventListener('click', trigger);
  document.addEventListener('keydown', function (e) {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('[role=button][data-gal],[role=button][data-video]')) trigger(e);
  });
})();

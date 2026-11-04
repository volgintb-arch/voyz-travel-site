/* Stories viewer (Instagram-style) for the video clips. Used by the website and the phone app.
   Any element with data-story, data-video, data-poster and data-name opens it; the clips of the same parent form one story set. */
(function () {
  var EN = document.documentElement.lang === 'en';
  var T = EN ? { close: 'Close', prev: 'Previous', next: 'Next' } : { close: 'Закрыть', prev: 'Назад', next: 'Вперёд' };
  var css = '.sv{position:fixed;inset:0;z-index:1100;display:flex;align-items:center;justify-content:center;gap:clamp(12px,2vw,32px);background:rgba(6,6,6,.94);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);opacity:0;transition:opacity .2s;touch-action:none}' +
    '.sv[hidden]{display:none}.sv.in{opacity:1}' +
    '.sv-card{position:relative;height:min(92vh,calc(94vw*16/9));aspect-ratio:9/16;max-width:100vw;border-radius:24px;overflow:hidden;background:#000;box-shadow:0 30px 90px rgba(0,0,0,.6);user-select:none;-webkit-user-select:none}' +
    '.sv-card video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#000}' +
    '.sv-card:before{content:"";position:absolute;left:0;right:0;top:0;height:140px;z-index:2;pointer-events:none;background:linear-gradient(to bottom,rgba(0,0,0,.6),transparent)}' +
    '.sv-bars{position:absolute;z-index:4;top:12px;left:12px;right:12px;display:flex;gap:4px}' +
    '.sv-bars i{flex:1;height:3px;border-radius:3px;background:rgba(255,255,255,.35);overflow:hidden}.sv-bars i b{display:block;height:100%;width:100%;background:#fff;transform-origin:left;transform:scaleX(0)}' +
    '.sv-top{position:absolute;z-index:4;top:26px;left:14px;right:10px;display:flex;align-items:center;justify-content:space-between;color:#fff}' +
    '.sv-top strong{font-family:"Unbounded",system-ui,sans-serif;font-weight:900;text-transform:uppercase;font-size:15px;letter-spacing:.02em;text-shadow:0 1px 8px rgba(0,0,0,.5)}' +
    '.sv-x{width:42px;height:42px;border:0;border-radius:50%;background:rgba(0,0,0,.35);color:#fff;font-size:26px;line-height:1;cursor:pointer}' +
    '.sv-hit{position:absolute;z-index:3;top:70px;bottom:0;width:38%;cursor:pointer}.sv-l{left:0}.sv-r{right:0;width:62%}' +
    '.sv-nav{flex:none;width:54px;height:54px;border-radius:50%;border:0;background:rgba(255,255,255,.14);color:#fff;font-size:24px;cursor:pointer;transition:background .2s}.sv-nav:hover{background:#fff;color:#000}' +
    '@media(max-width:700px){.sv{gap:0}.sv-nav{display:none}.sv-card{border-radius:0;height:100vh;height:100dvh;width:100vw;aspect-ratio:auto}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var ov, card, vid, bars, nameEl, set = [], idx = 0, holding = false, holdTimer = 0, raf = 0, startY = 0, startT = 0;

  function build() {
    ov = document.createElement('div'); ov.className = 'sv'; ov.hidden = true; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true');
    ov.innerHTML = '<button type="button" class="sv-nav sv-pv" aria-label="' + T.prev + '">←</button><div class="sv-card"><div class="sv-bars"></div>' +
      '<div class="sv-top"><strong></strong><button type="button" class="sv-x" aria-label="' + T.close + '">×</button></div><video playsinline></video>' +
      '<div class="sv-hit sv-l"></div><div class="sv-hit sv-r"></div></div><button type="button" class="sv-nav sv-nx" aria-label="' + T.next + '">→</button>';
    document.body.appendChild(ov);
    card = ov.querySelector('.sv-card'); vid = ov.querySelector('video'); bars = ov.querySelector('.sv-bars'); nameEl = ov.querySelector('strong');
    ov.querySelector('.sv-x').addEventListener('click', close);
    ov.querySelector('.sv-pv').addEventListener('click', function () { go(-1); });
    ov.querySelector('.sv-nx').addEventListener('click', function () { go(1); });
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    vid.addEventListener('ended', function () { go(1); });
    // tap: left third back, rest forward; hold: pause; swipe down: close
    ['sv-l', 'sv-r'].forEach(function (c) {
      var z = ov.querySelector('.' + c);
      z.addEventListener('pointerdown', function (e) { startY = e.clientY; startT = Date.now(); holding = false; holdTimer = setTimeout(function () { holding = true; vid.pause(); }, 220); });
      z.addEventListener('pointerup', function (e) {
        clearTimeout(holdTimer);
        if (e.clientY - startY > 90) { close(); return; }
        if (holding) { holding = false; vid.play().catch(function () { }); return; }
        go(c === 'sv-l' ? -1 : 1);
      });
      z.addEventListener('pointerleave', function () { clearTimeout(holdTimer); if (holding) { holding = false; vid.play().catch(function () { }); } });
    });
    document.addEventListener('keydown', function (e) {
      if (ov.hidden) return;
      if (e.key === 'Escape') close(); else if (e.key === 'ArrowLeft') go(-1); else if (e.key === 'ArrowRight') go(1);
      else if (e.key === ' ') { e.preventDefault(); vid.paused ? vid.play() : vid.pause(); }
    });
    document.addEventListener('visibilitychange', function () { if (document.hidden && vid) vid.pause(); });
  }
  function tick() {
    raf = requestAnimationFrame(tick);
    var d = vid.duration || 0, f = bars.children[idx]; if (f && d) f.firstChild.style.transform = 'scaleX(' + Math.min(1, vid.currentTime / d).toFixed(4) + ')';
  }
  function show() {
    set[idx].el.classList.add('seen');
    Array.prototype.forEach.call(bars.children, function (b, i) { b.firstChild.style.transform = 'scaleX(' + (i < idx ? 1 : 0) + ')'; });
    nameEl.textContent = set[idx].name; vid.poster = set[idx].poster || ''; vid.src = set[idx].src; vid.currentTime = 0; vid.play().catch(function () { });
    var nx = set[idx + 1]; if (nx) { var p = new Image(); p.src = nx.poster || ''; }
  }
  function go(d) {
    var n = idx + d;
    if (n >= set.length) { close(); return; }
    if (n < 0) { vid.currentTime = 0; return; }
    idx = n; show();
  }
  function open(el) {
    if (!ov) build();
    var group = Array.prototype.filter.call(el.parentNode.children, function (c) { return c.hasAttribute && c.hasAttribute('data-story'); });
    set = group.map(function (c) { return { el: c, src: c.getAttribute('data-video'), poster: c.getAttribute('data-poster'), name: c.getAttribute('data-name') || '' }; });
    idx = Math.max(0, group.indexOf(el));
    bars.innerHTML = set.map(function () { return '<i><b></b></i>'; }).join('');
    ov.hidden = false; document.body.style.overflow = 'hidden'; requestAnimationFrame(function () { ov.classList.add('in'); });
    show(); cancelAnimationFrame(raf); tick(); ov.querySelector('.sv-x').focus();
  }
  function close() {
    if (!ov || ov.hidden) return; cancelAnimationFrame(raf); vid.pause(); ov.classList.remove('in');
    setTimeout(function () { ov.hidden = true; vid.removeAttribute('src'); vid.load(); document.body.style.overflow = ''; }, 180);
  }
  function trig(e) { var el = e.target.closest && e.target.closest('[data-story]'); if (el) { e.preventDefault(); open(el); } }
  document.addEventListener('click', trig);
  document.addEventListener('keydown', function (e) { if ((e.key === 'Enter' || e.key === ' ') && e.target.matches && e.target.matches('[data-story]')) trig(e); });
  // quiet preview on hover (desktop)
  document.addEventListener('mouseover', function (e) { var s = e.target.closest && e.target.closest('.story'); if (s) { var v = s.querySelector('video'); if (v && v.paused) v.play().catch(function () { }); } });
})();

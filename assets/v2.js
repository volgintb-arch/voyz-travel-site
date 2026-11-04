// v2 motion: headline reveal, hero video, counters, route drawing, parallax, scroll progress
(function () {
  var RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };

  var bar = document.createElement('div'); bar.className = 'progress'; document.body.appendChild(bar);

  // hero headline: word-by-word reveal
  $$('.hero .h1').forEach(function (h) {
    var i = 0;
    (function wrap(node) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'w';
            var s = document.createElement('span'); s.textContent = p; s.style.setProperty('--i', i++);
            w.appendChild(s); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') wrap(n);
      });
    })(h);
  });

  // hero video fades in over the still image once it can play
  $$('.hero .bg video').forEach(function (v) {
    if (RM) return;
    var go = function () { v.play().then(function () { v.classList.add('on'); }).catch(function () {}); };
    if (v.readyState >= 3) go(); else v.addEventListener('canplay', go, { once: true });
  });

  // reel videos play only while visible
  if ('IntersectionObserver' in window && !RM) {
    var vo = new IntersectionObserver(function (es) {
      es.forEach(function (e) { var v = e.target; if (e.isIntersecting) { v.preload = 'auto'; v.play().catch(function () {}); } else v.pause(); });
    }, { threshold: .25 });
    $$('.vcard video').forEach(function (v) { vo.observe(v); });
  }

  // count-up for plain numbers in hero facts
  $$('.facts .num').forEach(function (el) {
    var t = el.textContent.trim(); if (!/^\d+$/.test(t) || RM) return;
    var n = +t; el.textContent = '0';
    setTimeout(function () {
      var s = performance.now();
      (function f(now) { var p = Math.min(1, (now - s) / 1400); el.textContent = Math.round(n * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(f); })(s);
    }, 1400);
  });

  // calendar bars fill with a stagger
  $$('.cal').forEach(function (c) {
    $$('.cal-row', c).forEach(function (row, r) { $$('.cal-bar i', row).forEach(function (i, k) { i.style.setProperty('--c', k); i.style.setProperty('--r', r); }); });
  });

  // stagger reveals and alternate day text direction
  $$('.why,.steps,.org,.diff,.lakes,.grid,.reel,.metas').forEach(function (g) {
    $$('.rv', g).forEach(function (el, i) { el.style.setProperty('--d', (i % 4) * 0.09 + 's'); });
  });

  // map: draw the route when it scrolls into view
  $$('.mapbox svg').forEach(function (svg) {
    if (RM) { svg.classList.add('go'); return; }
    var solid = $$('path', svg).filter(function (p) {
      return p.getAttribute('stroke') && !p.getAttribute('stroke-dasharray') && !p.getAttribute('transform') && parseFloat(p.getAttribute('stroke-width')) > 2;
    });
    solid.forEach(function (p) { p.classList.add('draw'); p.setAttribute('pathLength', '1000'); p.style.strokeDasharray = '1000'; p.style.strokeDashoffset = '1000'; });
    $$('circle,rect,text,ellipse', svg).forEach(function (e) { e.classList.add('pop'); });
    $$('path', svg).forEach(function (p) { if (p.getAttribute('transform')) p.classList.add('pop'); });
    var mo = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        solid.forEach(function (p, i) { setTimeout(function () { p.style.strokeDashoffset = '0'; }, i * 110); });
        setTimeout(function () { svg.classList.add('go'); }, 900); mo.disconnect();
      });
    }, { threshold: .3 });
    mo.observe(svg);
  });

  // parallax + scroll progress
  var par = $$('.pics .main img,.lake img'), ticking = false;
  function frame() {
    ticking = false; var vh = innerHeight, y = scrollY, h = document.documentElement.scrollHeight - vh;
    bar.style.width = (h > 0 ? y / h * 100 : 0) + '%';
    if (RM) return;
    par.forEach(function (img) {
      var r = img.parentNode.getBoundingClientRect(); if (r.bottom < -100 || r.top > vh + 100) return;
      var c = (r.top + r.height / 2 - vh / 2) / vh;
      img.style.transform = 'translate3d(0,' + (c * -34).toFixed(1) + 'px,0) scale(1.14)';
    });
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true }); frame();
})();

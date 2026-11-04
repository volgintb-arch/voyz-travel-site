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

  // map: a little jeep with two tourists drives along the route (out-and-back on the side trips)
  $$('.mapbox svg').forEach(function (svg) {
    var P = $$('path', svg);
    if (RM || P.length < 21 || P[4].getAttribute('stroke') !== '#D8FC00') return;
    var NS = 'http://www.w3.org/2000/svg', vb = svg.viewBox.baseVal;
    var seq = [[2, 1], [4, 1], [6, 1], [8, 1], [10, 1], [12, 1], [12, -1], [14, 1], [14, -1], [16, 1], [18, 1], [18, -1], [20, 1]];
    var legs = seq.map(function (q) { var p = P[q[0]]; return { p: p, dir: q[1], len: p.getTotalLength() }; });
    var total = legs.reduce(function (a, l) { return a + l.len; }, 0);
    var g = document.createElementNS(NS, 'g'); g.setAttribute('class', 'jeep'); g.style.opacity = '0';
    g.innerHTML = '<g class="jb"><ellipse cx="0" cy="2" rx="25" ry="3.5" fill="#000" opacity=".3"/>' +
      '<circle cx="-16" cy="-6" r="7" fill="#0B0B0B"/><circle cx="-16" cy="-6" r="3" fill="#BDBDBD"/><circle cx="16" cy="-6" r="7" fill="#0B0B0B"/><circle cx="16" cy="-6" r="3" fill="#BDBDBD"/>' +
      '<rect x="-27" y="-22" width="54" height="14" rx="5" fill="#FFFFFF" stroke="#0B0B0B" stroke-width="2.4"/><rect x="-27" y="-15" width="54" height="3.5" fill="#FF4B4B"/>' +
      '<circle cx="-7" cy="-28" r="5.2" fill="#F2C29B"/><path d="M-12.6 -28.5a5.6 5.6 0 0 1 11.2 0z" fill="#FF4B4B"/>' +
      '<circle cx="5" cy="-28" r="5.2" fill="#F2C29B"/><path d="M-0.6 -28.5a5.6 5.6 0 0 1 11.2 0z" fill="#8FD3FF"/>' +
      '<path d="M-19 -22V-34H13L16 -22" fill="none" stroke="#0B0B0B" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<circle cx="25" cy="-16" r="2.4" fill="#fff"/></g>';
    svg.appendChild(g);
    var jb = g.firstChild, at = 0, last = 0, vis = false, flip = 1, hold = 0, raf = 0;
    function pos(s) {
      var acc = 0;
      for (var i = 0; i < legs.length; i++) {
        var l = legs[i]; if (s <= acc + l.len || i === legs.length - 1) {
          var d = Math.max(0, Math.min(l.len, s - acc)), a = l.dir > 0 ? d : l.len - d, b = Math.max(0, Math.min(l.len, a + l.dir * 3));
          var p1 = l.p.getPointAtLength(a), p2 = l.p.getPointAtLength(b); return [p1.x, p1.y, p2.x - p1.x];
        } acc += l.len;
      }
    }
    function frame(t) {
      raf = 0; if (!vis) { last = 0; return; }
      var dt = last ? Math.min(64, t - last) : 0; last = t;
      var w = svg.getBoundingClientRect().width;
      if (w > 0) {
        var k = w / vb.width, px = Math.max(46, Math.min(100, w * .08)), sc = px / 54 / k;
        if (hold > 0) { hold -= dt; if (hold <= 0) { at = 0; g.style.opacity = '0'; } }
        else {
          at += dt / 24000 * total; if (at >= total) { at = total; hold = 1800; }
          var q = pos(at); if (q[2] > .2) flip = 1; else if (q[2] < -.2) flip = -1;
          g.style.opacity = '1';
          g.setAttribute('transform', 'translate(' + q[0].toFixed(1) + ' ' + q[1].toFixed(1) + ') scale(' + sc.toFixed(3) + ')');
          jb.setAttribute('transform', 'translate(0 ' + (Math.sin(t / 85) * 1.1).toFixed(2) + ') scale(' + flip + ' 1)');
        }
      }
      raf = requestAnimationFrame(frame);
    }
    var jo = new IntersectionObserver(function (es) {
      vis = es[0].isIntersecting && es[0].intersectionRatio > .25;
      if (vis && !raf) raf = requestAnimationFrame(frame);
    }, { threshold: [0, .25, .5] });
    setTimeout(function () { jo.observe(svg); }, 1500);
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

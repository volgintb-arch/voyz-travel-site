/* Two 4x4 vehicles drive along the route on the map (no people). Used by the website and the phone app. */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  function wheel(cx) {
    return '<circle cx="' + cx + '" cy="-10" r="12.6" fill="#141414"/>' +
      '<circle cx="' + cx + '" cy="-9.5" r="10.3" fill="#262626" stroke="#0B0B0B" stroke-width="1.4"/>' +
      '<circle cx="' + cx + '" cy="-9.5" r="9" fill="none" stroke="#3C3C3C" stroke-width="1.5" stroke-dasharray="2.2 2.1"/>' +
      '<circle cx="' + cx + '" cy="-9.5" r="5.9" fill="#C9CDD3" stroke="#7E848B" stroke-width="1"/>' +
      '<circle cx="' + cx + '" cy="-9.5" r="2.2" fill="#555B61"/>' +
      '<path d="M' + cx + ' -15.2V-3.8M' + (cx - 5.2) + ' -9.5H' + (cx + 5.2) + 'M' + (cx - 3.7) + ' -13.2L' + (cx + 3.7) + ' -5.8M' + (cx + 3.7) + ' -13.2L' + (cx - 3.7) + ' -5.8" stroke="#7E848B" stroke-width=".9"/>';
  }
  // a side view of a boxy expedition 4x4: roof rack with luggage, spare wheel, snorkel, glass with reflections
  function car(body, load1, load2) {
    return '<g class="jb"><ellipse cx="0" cy="1.6" rx="46" ry="4" fill="#000" opacity=".3"/>' +
      '<circle cx="-47" cy="-21" r="7.6" fill="#1D1D1D" stroke="#0B0B0B" stroke-width="1.2"/><circle cx="-47" cy="-21" r="4.1" fill="#9AA0A6"/>' +
      '<path d="M-43 -11V-27Q-43 -29.2 -40.8 -29.2H-27L-23.2 -36.4Q-22.6 -37.6 -21.2 -37.6H12Q13.6 -37.6 14.6 -36.3L19 -29.6L37 -28.6Q42.2 -28.2 43.2 -23.4V-11Z" fill="' + body + '" stroke="#0B0B0B" stroke-width="1.7" stroke-linejoin="round"/>' +
      '<path d="M-43 -11V-16.5H43.2V-11Z" fill="#0B0B0B" opacity=".3"/>' +
      '<path d="M-24.6 -29.6L-21.6 -35.2Q-21 -36 -20 -36H-5.2V-29.6Z" fill="#A9D4EE" stroke="#0B0B0B" stroke-width="1.2"/>' +
      '<path d="M-2.2 -29.6V-36H11.4Q12.4 -36 13 -35.1L17.2 -29.6Z" fill="#A9D4EE" stroke="#0B0B0B" stroke-width="1.2"/>' +
      '<path d="M-19 -35.2H-12.6L-16 -30.2H-22Z" fill="#fff" opacity=".4"/><path d="M1 -35.2H5.4L2.2 -30.2H-1.6Z" fill="#fff" opacity=".35"/>' +
      '<path d="M-3.7 -29.2V-16.6" stroke="#0B0B0B" stroke-width="1" opacity=".55"/><rect x="-1.2" y="-25.8" width="5" height="1.7" rx=".85" fill="#0B0B0B" opacity=".55"/>' +
      '<rect x="-21" y="-40.6" width="33" height="2.2" rx="1" fill="#2A2A2A"/><path d="M-19 -40.6V-37.8M10 -40.6V-37.8" stroke="#2A2A2A" stroke-width="1.6"/>' +
      '<rect x="-18" y="-46.4" width="13" height="5.8" rx="1.8" fill="' + load1 + '" stroke="#0B0B0B" stroke-width="1"/><rect x="-3" y="-45.2" width="10" height="4.6" rx="1.6" fill="' + load2 + '" stroke="#0B0B0B" stroke-width="1"/>' +
      '<rect x="14.5" y="-38" width="1.8" height="9" rx=".9" fill="#1A1A1A" transform="rotate(10 15.4 -33.5)"/>' +
      '<rect x="39.4" y="-26.4" width="4.8" height="5.2" rx="1.6" fill="#FFF3B0" stroke="#0B0B0B" stroke-width="1"/><rect x="41" y="-19" width="3.6" height="3" fill="#1A1A1A"/>' +
      '<rect x="38" y="-14.4" width="8.6" height="3.6" rx="1.6" fill="#242424"/><rect x="-48" y="-14.4" width="6.6" height="3.6" rx="1.6" fill="#242424"/><rect x="-43.6" y="-26" width="2.6" height="5.2" rx=".8" fill="#E0312C"/>' +
      wheel(-25) + wheel(26) + '</g>';
  }

  window.voyzJeep = function (svg, scroller, rm) {
    var P = Array.prototype.slice.call(svg.querySelectorAll('path'));
    if (rm || P.length < 21 || !P[4] || P[4].getAttribute('stroke') !== '#D8FC00') return;
    var vb = svg.viewBox.baseVal;
    var seq = [[2, 1], [4, 1], [6, 1], [8, 1], [10, 1], [12, 1], [12, -1], [14, 1], [14, -1], [16, 1], [18, 1], [18, -1], [20, 1]];
    var legs = seq.map(function (q) { var p = P[q[0]]; return { p: p, dir: q[1], len: p.getTotalLength() }; });
    var total = legs.reduce(function (a, l) { return a + l.len; }, 0), gap = total * .05;
    var cars = [car('#F4F2EC', '#3E5A3C', '#B5651D'), car('#E4572E', '#2F4B6E', '#C9A227')].map(function (m) {
      var g = document.createElementNS(NS, 'g'); g.setAttribute('class', 'jeep'); g.style.opacity = '0'; g.innerHTML = m; svg.appendChild(g);
      return { g: g, jb: g.firstChild, flip: 1 };
    });
    var at = 0, last = 0, vis = false, raf = 0, hold = 1800;
    function pos(s) {
      var acc = 0;
      for (var i = 0; i < legs.length; i++) {
        var l = legs[i];
        if (s <= acc + l.len || i === legs.length - 1) {
          var d = Math.max(0, Math.min(l.len, s - acc)), a = l.dir > 0 ? d : l.len - d, b = Math.max(0, Math.min(l.len, a + l.dir * 3));
          var p1 = l.p.getPointAtLength(a), p2 = l.p.getPointAtLength(b); return [p1.x, p1.y, p2.x - p1.x];
        }
        acc += l.len;
      }
    }
    function frame(t) {
      raf = 0; if (!vis) { last = 0; return; }
      var dt = last ? Math.min(64, t - last) : 0; last = t;
      var w = svg.getBoundingClientRect().width;
      if (w > 0) {
        var k = w / vb.width, px = Math.max(58, Math.min(112, w * .085)), sc = px / 94 / k;
        at += dt / 27000 * total; if (at >= total + gap + hold * total / 27000) at = 0;
        cars.forEach(function (c, i) {
          var s = at - i * gap;
          if (s < 0 || s > total) { c.g.style.opacity = '0'; return; }
          var q = pos(s); if (q[2] > .2) c.flip = 1; else if (q[2] < -.2) c.flip = -1;
          c.g.style.opacity = '1';
          c.g.setAttribute('transform', 'translate(' + q[0].toFixed(1) + ' ' + q[1].toFixed(1) + ') scale(' + sc.toFixed(3) + ')');
          c.jb.setAttribute('transform', 'translate(0 ' + (Math.sin(t / 90 + i * 2) * 1).toFixed(2) + ') scale(' + c.flip + ' 1)');
        });
      }
      raf = requestAnimationFrame(frame);
    }
    var io = new IntersectionObserver(function (es) {
      vis = es[0].isIntersecting && es[0].intersectionRatio > .25;
      if (vis && !raf) raf = requestAnimationFrame(frame);
    }, { root: scroller || null, threshold: [0, .25, .5] });
    setTimeout(function () { io.observe(svg); }, 1200);
  };
})();

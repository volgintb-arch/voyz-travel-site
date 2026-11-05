"""Mobile layout audit: horizontal overflow, clipped elements, words that break mid-word or are wider than their box.
   usage: python audit.py [width ...]   (default 360 390 430 768)"""
import sys, json
from playwright.sync_api import sync_playwright
B = 'http://localhost:8765'
PAGES = ['/', '/tours/', '/tours/grand-expedition/', '/privacy/', '/credits/', '/en/', '/en/tours/grand-expedition/']
JS = r'''() => {
  const W = innerWidth, res = {scroll: document.documentElement.scrollWidth, W, over: [], clip: [], broken: [], wide: [], fonts: {}};
  const sel = el => { let s = el.tagName.toLowerCase(); if (el.id) s += '#' + el.id; if (el.className && typeof el.className === 'string') s += '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.'); return s; };
  const scroller = el => { for (let p = el.parentElement; p; p = p.parentElement) { const cs = getComputedStyle(p); if (/(auto|scroll)/.test(cs.overflowX) && p.scrollWidth > p.clientWidth + 1) return true; } return false; };
  const skip = el => el.closest('.lb,.sv,.modal,svg,.tabbar,[hidden]') || el.tagName === 'IMG' || el.tagName === 'VIDEO';
  document.querySelectorAll('body *').forEach(el => {
    if (skip(el)) return; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    if ((r.right > W + 1 || r.left < -1) && cs.position !== 'fixed' && !scroller(el)) res.over.push(sel(el) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
    // clipped by an overflow:hidden ancestor
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const pc = getComputedStyle(p); if (/(auto|scroll)/.test(pc.overflowX)) break;
      if (/(hidden|clip)/.test(pc.overflowX)) { const pr = p.getBoundingClientRect(); if (r.right > pr.right + 2 || r.left < pr.left - 2) { if (el.children.length === 0 || el.textContent.trim()) res.clip.push(sel(el) + ' in ' + sel(p) + ' ' + Math.round(r.right - pr.right) + 'px | ' + (el.textContent || '').trim().slice(0, 30)); } break; }
    }
  });
  // words: wider than the box, or broken in the middle
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while ((n = walker.nextNode())) {
    const el = n.parentElement; if (!el || skip(el)) continue; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || /^(script|style|noscript)$/i.test(el.tagName)) continue;
    const txt = n.nodeValue; const re = /\S+/g; let m;
    while ((m = re.exec(txt))) {
      if (m[0].length < 5 || /[–—]/.test(m[0])) continue;
      const rg = document.createRange(); rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
      const rects = rg.getClientRects(); if (!rects.length) continue;
      if (rects.length > 1) { const a = Array.from(rects); const rows = new Set(a.map(x => Math.round(x.top / 4))); if (rows.size > 1) res.broken.push(sel(el) + ' "' + m[0] + '" ' + cs.fontSize); }
      const b = rg.getBoundingClientRect(); const blk = el.closest('h1,h2,h3,p,li,span,a,div,button,label');
      if (blk) { const br = blk.getBoundingClientRect(); if (b.right > Math.min(W, br.right) + 2 && !scroller(el)) res.wide.push(sel(el) + ' "' + m[0] + '" ' + cs.fontSize + ' right=' + Math.round(b.right)); }
    }
  }
  document.querySelectorAll('h1,h2,h3,.big,.num').forEach(el => { if (skip(el) || !el.getBoundingClientRect().width) return; const k = sel(el); res.fonts[k] = getComputedStyle(el).fontSize; });
  return res;
}'''
def uniq(a, n=8):
    seen, out = set(), []
    for x in a:
        if x not in seen: seen.add(x); out.append(x)
    return out[:n], len(set(a))
if __name__ == '__main__':
    widths = [int(x) for x in sys.argv[1:]] or [360, 390, 430, 768]
    total = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in widths:
            c = b.new_context(viewport={'width': w, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2); pg = c.new_page(); pg.set_default_timeout(20000)
            for path in PAGES:
                pg.goto(B + path + '?full=1', wait_until='load'); pg.wait_for_timeout(500)
                H = pg.evaluate('document.documentElement.scrollHeight')
                for y in range(0, H, 700): pg.evaluate('window.scrollTo(0,%d)' % y); pg.wait_for_timeout(60)
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(200)
                r = pg.evaluate(JS); issues = []
                if r['scroll'] > r['W'] + 1: issues.append('PAGE scrolls sideways: %d > %d' % (r['scroll'], r['W']))
                for k in ('over', 'clip', 'broken', 'wide'):
                    items, n = uniq(r[k])
                    if n: issues.append('%s (%d): %s' % (k, n, ' || '.join(items)))
                total += len(issues)
                print('%4d %-34s %s' % (w, path, 'ok' if not issues else ''))
                for i in issues: print('        -', i)
            c.close()
        b.close()
    print('\nPAGES WITH ISSUES:', total)

import re, sys
from playwright.sync_api import sync_playwright
B='http://localhost:8765'; CYR=re.compile('[А-Яа-яЁё]'); bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    ap=c.new_page(); ap.set_default_timeout(6000); errs=[]; ap.on('pageerror',lambda e:errs.append(str(e)))
    def go(h):
        ap.goto(B+'/en/app/'+h,wait_until='load'); ap.reload(wait_until='load'); ap.wait_for_timeout(1200)
    def scan(l):
        t=ap.evaluate("document.querySelector('.phone').innerText+' '+[...document.querySelectorAll('[placeholder],[aria-label],[alt]')].map(e=>(e.placeholder||'')+' '+(e.getAttribute('aria-label')||'')+' '+(e.alt||'')).join(' ')")
        m=CYR.search(t); print(' ',l,'chars',len(t),'CYR' if m else 'ok',flush=True)
        if m: bad.append((l,t[max(0,m.start()-30):m.start()+40].replace('\n',' ')))
    for h in ('','#/tours','#/calendar','#/request','#/tour/grand-expedition','#/tour/zima-issyk-kul'):
        go(h); scan(h or 'home')
    print('errors',errs); print('BAD',bad)
    b.close()

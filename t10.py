from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':1440,'height':900}); pg=c.new_page(); pg.set_default_timeout(20000)
    pg.goto('http://localhost:8765/',wait_until='load'); pg.wait_for_timeout(800)
    pg.evaluate("(()=>{const e=document.querySelector('#trow');window.scrollTo({top:e.getBoundingClientRect().top+scrollY-300,behavior:'instant'})})()"); pg.wait_for_timeout(1500); pg.screenshot(path='shots/g_row.png')
    m=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True); q=m.new_page(); q.set_default_timeout(20000)
    q.goto('http://localhost:8765/?full=1',wait_until='load'); q.wait_for_timeout(800)
    q.evaluate("window.scrollTo({top:document.querySelector('.yplate').getBoundingClientRect().top+scrollY-200,behavior:'instant'})"); q.wait_for_timeout(1000); q.screenshot(path='shots/g_mplate.png')
    q.evaluate("window.scrollTo({top:document.querySelector('#trow').getBoundingClientRect().top+scrollY-250,behavior:'instant'})"); q.wait_for_timeout(1000); q.screenshot(path='shots/g_mrow.png')
    q.evaluate("window.scrollTo({top:document.querySelector('.mapbox').getBoundingClientRect().top+scrollY-200,behavior:'instant'})"); q.wait_for_timeout(9000); q.screenshot(path='shots/g_mmap.png')
    b.close()

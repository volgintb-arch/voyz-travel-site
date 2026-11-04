from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); m = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True); q = m.new_page(); errs = []
    q.on('pageerror', lambda e: errs.append(str(e))); q.set_default_timeout(20000)
    q.goto('http://localhost:8765/app/#/tour/grand-expedition', wait_until='load'); q.wait_for_timeout(1500)
    q.evaluate("document.querySelector('.mapcard').scrollIntoView({block:'center',behavior:'instant'})"); q.wait_for_timeout(9000)
    print(q.evaluate("(()=>{const j=document.querySelector('.mapcard .jeep');return j&&[j.getAttribute('transform'),j.style.opacity]})()"), errs)
    q.screenshot(path='shots/g_appmap.png'); b.close()

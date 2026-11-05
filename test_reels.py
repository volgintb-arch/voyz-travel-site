"""Verify actual local Reel playback, controls, source links, and no forced navigation."""
from playwright.sync_api import sync_playwright
from test_support import site_server,settle,ROOT
with site_server() as base,sync_playwright() as p:
 b=p.chromium.launch()
 for width in (390,1440):
  c=b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');q=c.new_page()
  for lang in ('','en/'):
   requested=[];q.on('request',lambda r:requested.append(r.url))
   q.goto(base+'/'+lang,wait_until='domcontentloaded');settle(q)
   assert not any('/assets/social/' in u and '.mp4' in u for u in requested),'Reels must load only on request'
   section=q.locator('#instagram');section.scroll_into_view_if_needed();q.wait_for_timeout(250)
   if not lang:section.screenshot(path=str(ROOT/'shots'/('reels-section-%d.png'%width)),style='.hdr,.tabbar,.progress{visibility:hidden!important}')
   assert q.locator('section').nth(2).get_attribute('id')=='instagram','Reels must replace the upper video block'
   for i in range(3):
    before=q.url;button=q.locator('#instagram button[data-video]').nth(i);button.scroll_into_view_if_needed();button.click()
    q.wait_for_function("(()=>{let v=document.querySelector('.lb video');return v&&v.readyState>=2&&v.currentTime>.1&&!v.paused})()",timeout=15000)
    v=q.locator('.lb video');assert v.get_attribute('controls') is not None;assert not v.evaluate('(v)=>v.muted');assert q.url==before
    assert q.locator('.lb-source').get_attribute('href')==button.get_attribute('data-instagram')
    if i==0 and not lang:q.screenshot(path=str(ROOT/'shots'/('reels-player-%d.png'%width)))
    q.keyboard.press('Escape');q.wait_for_timeout(250);assert not q.locator('.lb').is_visible()
    assert q.locator('.lb video').count()==0,'Player must be unloaded on close'
    print('PASS playback',width,lang or 'ru',i+1,flush=True)
  c.close()
 b.close()

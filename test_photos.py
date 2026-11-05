"""Check licensed photo attribution and responsive hero delivery."""
import json
from PIL import Image
from playwright.sync_api import sync_playwright
from test_support import ROOT,site_server
assets=json.loads((ROOT/'data/photo_assets.json').read_text(encoding='utf8'))
credits=json.loads((ROOT/'data/credits.json').read_text(encoding='utf8'))
for key,row in assets.items():
 assert row['license_url'].startswith('https://creativecommons.org/')
 assert credits[key]['artist']==row['author']
 assert credits[key]['license_url']==row['license_url']
 if key!='home-alakul':
  for size in ('l','m'):
   with Image.open(ROOT/f'assets/img/{key}-{size}.webp') as im:
    assert im.width<=row['downloaded_width'] and im.height<=row['downloaded_height']
with site_server() as u,sync_playwright() as p:
 b=p.chromium.launch()
 for lang in ('','en/'):
  for width,dpr in ((390,2),(1920,2)):
   c=b.new_context(viewport={'width':width,'height':920},device_scale_factor=dpr,reduced_motion='reduce');q=c.new_page();q.goto(u+'/'+lang,wait_until='networkidle')
   assert q.locator('.hero video').count()==0
   hero=q.locator('.hero .bg img');assert hero.evaluate('(e)=>e.complete&&e.naturalWidth>=1440')
   assert ('mobile' if width==390 else '3840') in hero.evaluate('(e)=>e.currentSrc')
   q.screenshot(path=str(ROOT/f'shots/licensed-hero-{width}-{lang.replace("/","") or "ru"}.png'))
   q.goto(u+'/'+lang+'credits/',wait_until='networkidle')
   for row in assets.values():
    assert q.locator('a').evaluate_all('(a,url)=>a.some(x=>x.href===url)',row['source'])
    assert q.locator('a').evaluate_all('(a,url)=>a.some(x=>x.href===url)',row['license_url'])
   c.close()
 b.close()
print('PASS: photo files, no upscaling, author/license links and RU/EN responsive hero')

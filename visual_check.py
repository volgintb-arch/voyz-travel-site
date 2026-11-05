"""Capture all current pages and section contact sheets: python visual_check.py."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from playwright.sync_api import sync_playwright
from test_support import ROOT,active_paths,site_server,settle
OUT=ROOT/'shots';OUT.mkdir(exist_ok=True)
with site_server() as base,sync_playwright() as p:
    b=p.chromium.launch()
    for w in (390,1440):
        c=b.new_context(viewport={'width':w,'height':900},reduced_motion='reduce');q=c.new_page()
        for lang in ('','en/'):
            for path in active_paths():
                name=(lang+path).strip('/').replace('/','-') or 'home'
                q.goto(base+'/'+lang+path,wait_until='domcontentloaded');settle(q,scroll=True)
                q.screenshot(path=str(OUT/f'{name}-{w}.png'),full_page=True)
                if path in ('','tours/grand-expedition/'):
                    tiles=[]
                    for i,e in enumerate(q.locator('section').all()):
                        e.scroll_into_view_if_needed();q.wait_for_timeout(150)
                        e.screenshot(path=str(OUT/f'{name}-{w}-section-{i}.png'),style='.hdr,.tabbar,.subnav,.progress{visibility:hidden!important}')
                        im=Image.open(OUT/f'{name}-{w}-section-{i}.png').convert('RGB');im.thumbnail((400,650))
                        tile=Image.new('RGB',(420,690),'#242424');tile.paste(im,((420-im.width)//2,25));ImageDraw.Draw(tile).text((10,5),f'{name} / {i}',fill='white');tiles.append(tile)
                    rows=(len(tiles)+3)//4;sheet=Image.new('RGB',(1680,690*rows),'#242424')
                    for i,im in enumerate(tiles):sheet.paste(im,((i%4)*420,(i//4)*690))
                    sheet.save(OUT/f'{name}-{w}-sections.jpg',quality=82)
                print('CAPTURE',name,w,flush=True)
        c.close()
    b.close()

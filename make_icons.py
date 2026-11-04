"""Favicon + app icons from the official VOYZ mark (the first letter of the wordmark).
Run: python make_icons.py"""
import os, io
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'assets/icons'); os.makedirs(OUT, exist_ok=True)
V = 'M135.8878 84.28833 89.27274 26.487034 42.657686 84.28833H0L67.9439-.000031H110.60697L178.55089 84.28833H135.8878Z'   # "V" from the VOYZ wordmark
LIME, INK = '#D8FC00', '#0B0B0B'

def svg(size=512, radius=0.22, scale=0.62, bg=LIME, fg=INK):
    w = 178.55 * 1.0; h = 84.3
    s = size * scale / w
    tx = (size - w * s) / 2; ty = (size - h * s) / 2
    rx = size * radius
    # flip Y like the source logo: matrix(1,0,0,-1,0,84.3) puts the glyph upright
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<rect width="{size}" height="{size}" rx="{rx}" fill="{bg}"/>'
            f'<g transform="translate({tx:.2f},{ty + h * s:.2f}) scale({s:.4f},-{s:.4f})"><path d="{V}" transform="translate(0.5558,0) " fill="{fg}"/></g></svg>')

# vector favicon: the glyph is only a wide V, so use a bolder scale for tiny sizes
open(os.path.join(OUT, 'favicon.svg'), 'w', encoding='utf-8').write(svg(64, 0.22, 0.74))
open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(svg(64, 0.22, 0.74))

def render(html, size):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': size, 'height': size})
        pg.set_content('<body style="margin:0;background:transparent">' + html + '</body>')
        png = pg.screenshot(omit_background=True, clip={'x': 0, 'y': 0, 'width': size, 'height': size}); b.close()
    return Image.open(io.BytesIO(png)).convert('RGBA')

jobs = {'icon-512.png': (512, svg(512, 0.22, 0.66)), 'icon-192.png': (192, svg(192, 0.22, 0.66)),
        'apple-touch-icon.png': (180, svg(180, 0, 0.66)),                     # iOS applies its own rounding
        'maskable-512.png': (512, svg(512, 0, 0.5)),                           # extra safe zone for Android masks
        'favicon-32.png': (32, svg(32, 0.2, 0.78)), 'favicon-16.png': (16, svg(16, 0.2, 0.78)), 'favicon-48.png': (48, svg(48, 0.2, 0.78))}
imgs = {}
for name, (size, s) in jobs.items():
    im = render(s, size); im.save(os.path.join(OUT, name)); imgs[name] = im
imgs['favicon-48.png'].save(os.path.join(ROOT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)], append_images=[imgs['favicon-32.png'], imgs['favicon-16.png']])
print('icons:', sorted(os.listdir(OUT)))

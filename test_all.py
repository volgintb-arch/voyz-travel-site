"""Current site regression checks; run without a separate server: python test_all.py."""
import json, re, sys
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright
from test_support import active_paths, active_tours, site_server
CYR = re.compile('[А-Яа-яЁё]')
def run():
    problems, checked = [], set()
    def check(ok, message):
        if not ok: problems.append(message); print('FAIL:', message, flush=True)
    tours = active_tours(); grand = next(t for t in tours if t['slug']=='grand-expedition')
    check((grand['group_min'],grand['group_max'])==(6,12), 'Group bounds in tour data')
    check(['6–12','человек в группе'] in grand['facts'], 'Grand Expedition group must be 6–12')
    check([d['n'] for d in grand['days']]==list(range(1,9)), 'Eight ordered days required')
    paths=active_paths()
    with site_server() as base, sync_playwright() as p:
        browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');page=ctx.new_page()
        page.on('pageerror',lambda e: problems.append('JS: '+str(e)))
        for lang in ('','en/'):
            for path in paths:
                tag=lang+path or '/'; r=page.goto(base+'/'+lang+path,wait_until='domcontentloaded')
                check(r.ok,tag+': HTTP'); check(urlsplit(page.url).path=='/'+lang+path,tag+': redirect')
                info=page.evaluate('''()=>{const q=s=>document.querySelector(s),m=(n,a='name')=>q(`meta[${a}="${n}"]`)?.content;return {
                  lang:document.documentElement.lang,title:document.title,desc:m('description'),robots:m('robots'),canon:q('link[rel=canonical]')?.href,
                  h1:document.querySelectorAll('h1').length,alts:[...document.querySelectorAll('link[hreflang]')].map(e=>e.hreflang).sort(),
                  og:m('og:title','property'),ogi:m('og:image','property'),tw:m('twitter:card'),ld:[...document.querySelectorAll('script[type="application/ld+json"]')].map(e=>JSON.parse(e.textContent)),
                  text:document.body.innerText,urls:[...document.querySelectorAll('a[href],link[href]')].map(e=>e.href).concat([...document.querySelectorAll('img[src],script[src],source[src]')].map(e=>e.src)),
                  ids:[...document.querySelectorAll('[id]')].map(e=>e.id)}}''')
                check(info['lang']==('en' if lang else 'ru'),tag+': language');check(info['h1']==1,tag+': one h1 required')
                check(len(info['ids'])==len(set(info['ids'])),tag+': duplicate IDs')
                for k in ('title','desc','robots','canon','og','ogi','tw','ld'):check(bool(info[k]),tag+': missing '+k)
                check(info['alts']==['en','ru','x-default'],tag+': hreflang')
                if lang:
                    check(not CYR.search(info['text']),tag+': untranslated visible text');check(not CYR.search(info['title']+info['desc']),tag+': untranslated metadata')
                check(page.locator('footer a[href="https://www.instagram.com/voyz_travel/"]').count()==1,tag+': Instagram footer link')
                for url in info['urls']:
                    u=urlsplit(url)
                    if u.netloc!=urlsplit(base).netloc:continue
                    target=u._replace(fragment='').geturl()
                    if target not in checked:
                        checked.add(target);check(ctx.request.get(target).ok,tag+': broken URL '+url)
                    if u.fragment and (u.path.endswith('/') or u.path.endswith('.html')):
                        content=ctx.request.get(target).text()
                        check(bool(re.search(r'\bid=["\x27]'+re.escape(u.fragment)+r'["\x27\s>]',content)),tag+': missing anchor '+url)
                if path in ('','tours/grand-expedition/'):
                    check(page.locator('#team .person-avatar').count()>0,tag+': team portrait')
                    check(page.locator('#instagram .social-post').count()==3,tag+': Instagram posts')
                    options=page.locator('form[data-request]').first.locator('[name=people] option').all_text_contents()
                    check(all(str(i) in options for i in range(1,13)),tag+': group options 1–12')
                print('PASS page',tag,flush=True)
        xml=ET.fromstring(ctx.request.get(base+'/sitemap.xml').body());locs=[e.text for e in xml.findall('{*}url/{*}loc')]
        prefix=urlsplit(info['canon']).path.split('/en/')[0].rstrip('/')
        check({urlsplit(u).path for u in locs}=={prefix+'/'+l+x for l in ('','en/') for x in paths},'sitemap route set')
        check(ctx.request.get(base+'/404.html').ok,'404 page')
        for lang in ('','en/'):
            page.goto(base+'/'+lang,wait_until='domcontentloaded');page.locator('[data-open-form=hero]').click();form=page.locator('.modal form')
            form.locator('[type=submit]').click();check(form.locator('.bad').count()>=3,lang+': validation')
            form.locator('[name=name]').fill('Test VOYZ');form.locator('[name=contact]').fill('test@example.invalid');form.locator('[name=people]').select_option('12');form.locator('[name=consent]').check()
            page.evaluate("window.VOYZ_CONFIG.formEndpoint=''");form.locator('[type=submit]').click()
            check(form.locator('[data-copy]').count()==1,lang+': demo copy button');check(page.evaluate("JSON.parse(localStorage.getItem('voyz_requests')).at(-1).people")=='12',lang+': request group')
            page.keyboard.press('Escape');page.locator('[data-open-form=hero]').click()
            page.evaluate("window.VOYZ_CONFIG.formEndpoint='https://voyz-form.example.invalid/request'")
            page.route('https://voyz-form.example.invalid/request',lambda route:route.fulfill(status=200,json={'ok':True},headers={'Access-Control-Allow-Origin':'*'}))
            form.locator('[type=submit]').click();page.wait_for_function("document.querySelector('.modal .ok').innerText.includes(document.documentElement.lang==='en'?'Request sent':'Заявка отправлена')");page.keyboard.press('Escape')
        page.goto(base+'/tours/grand-expedition/',wait_until='domcontentloaded');detail=page.locator('details').first;detail.locator('summary').click();check(detail.get_attribute('open') is not None,'FAQ expands')
        gal=page.locator('[data-gal]').first
        if gal.count():
            gal.click();check(page.locator('.lb').is_visible(),'gallery opens');page.keyboard.press('Escape');page.wait_for_timeout(250);check(not page.locator('.lb').is_visible(),'gallery closes')
        browser.close()
    print('RESULT:',len(problems),'problems;',len(checked),'local URLs checked',flush=True)
    return 1 if problems else 0
if __name__=='__main__':sys.exit(run())

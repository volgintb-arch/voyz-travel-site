"""Legacy app links redirect to the current responsive website, preserving language."""
import sys
from playwright.sync_api import sync_playwright
from test_support import active_tours,site_server
def run():
    with site_server() as base,sync_playwright() as p:
        b=p.chromium.launch()
        for w in (390,1440):
            c=b.new_context(viewport={'width':w,'height':900});q=c.new_page()
            for lang in ('','en/'):
                cases=[('','/'+lang),('#/tours','/'+lang+'tours/'),('#/request','/'+lang)]+[('#/tour/'+t['slug'],'/'+lang+'tours/'+t['slug']+'/') for t in active_tours()]
                for fragment,target in cases:
                    q.goto(base+'/'+lang+'app/'+fragment,wait_until='domcontentloaded');q.wait_for_url(base+target);assert q.locator('h1').count()==1,target
                    print('PASS redirect',w,lang+'app/'+fragment,'->',target,flush=True)
            c.close()
        b.close()
    return 0
if __name__=='__main__':sys.exit(run())

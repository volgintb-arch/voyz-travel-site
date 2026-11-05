"""Active routes from JSON, isolated local server, screenshot settling."""
import json, os, sys, threading
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def active_tours():
    return sum((json.loads((ROOT / ('data/' + n)).read_text(encoding='utf-8'))['tours'] for n in ('tours.json', 'tours_extra.json')), [])
def active_paths():
    return ['', 'tours/', 'privacy/', 'credits/'] + ['tours/%s/' % t['slug'] for t in active_tours()]
@contextmanager
def site_server():
    if os.environ.get('BASE_URL'):
        yield os.environ['BASE_URL'].rstrip('/')
        return
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    class Server(ThreadingHTTPServer):
        def handle_error(self, request, address):
            # Browsers cancel media downloads when navigating to the next test page.
            if not isinstance(sys.exc_info()[1], ConnectionError):
                super().handle_error(request, address)
    server = Server(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try: yield 'http://127.0.0.1:%d' % server.server_port
    finally:
        server.shutdown(); server.server_close(); thread.join()
def settle(page, scroll=False):
    page.evaluate('Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,3000))])')
    if scroll:
        height = page.evaluate('document.documentElement.scrollHeight')
        for y in range(0, height, 650):
            page.evaluate('(y)=>window.scrollTo({top:y,behavior:"instant"})', y)
            page.wait_for_timeout(35)
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})'); page.wait_for_timeout(250)

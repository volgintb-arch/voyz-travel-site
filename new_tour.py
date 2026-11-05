"""Create a new tour from the template.

    python new_tour.py my-slug "Название тура"

Adds an entry to data/tours_extra.json (copy of data/tour_template.json with the slug and title filled in).
Then edit that entry, run  python build_site.py  and the tour appears on the site (page, card, calendar, sitemap).
When there are two or more tours, the site automatically adds the tour row, the season calendar and "in season now".
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 3 or not re.fullmatch(r'[a-z0-9-]+', sys.argv[1]):
    sys.exit('usage: python new_tour.py my-slug "Название тура"   (slug: latin letters, digits, dashes)')
slug, title = sys.argv[1], sys.argv[2]
tpl = json.load(open(os.path.join(ROOT, 'data/tour_template.json'), encoding='utf-8'))
tpl.pop('_readme', None); tpl['slug'] = slug; tpl['title'] = title
path = os.path.join(ROOT, 'data/tours_extra.json')
ex = json.load(open(path, encoding='utf-8'))
base = json.load(open(os.path.join(ROOT, 'data/tours.json'), encoding='utf-8'))
if any(t['slug'] == slug for t in ex['tours'] + base['tours']): sys.exit('a tour with this slug already exists')
ex['tours'].append(tpl)
json.dump(ex, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('added "%s" to data/tours_extra.json - edit it, then run: python build_site.py' % slug)

"""Lane-30 (shopping R5->A4) READ-ONLY probe: enumerate price-facet cells.

Reimplements catalog.js resolveListing/priceFacets faithfully enough to
enumerate, for each of the 22 fully-seeded categories, every sidebar price
bucket, its derived pool, and whether the faceted URL is an exact capture.
"""
import json, os, re, sys
from collections import defaultdict

ROOT = '/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data'
products = json.load(open(os.path.join(ROOT, 'products.json')))
cats = json.load(open(os.path.join(ROOT, 'categories.json')))
listings = json.load(open(os.path.join(ROOT, 'listings.json')))

byid = {p['id']: p for p in products}
catbyid = {c['id']: c for c in cats}
children = defaultdict(list)
for c in cats:
    children[c.get('parentId')].append(c['id'])

def listable(p):
    return p.get('status') == 1 and p.get('visibility', 0) >= 4 and p.get('inStock')

def final_price(p):
    sp = p.get('specialPrice')
    return sp if sp is not None else p.get('price')

def descendants(cid):
    out = set()
    stack = [int(cid)]
    while stack:
        x = stack.pop()
        if x in out: continue
        out.add(x)
        stack.extend(children.get(x, []))
    return out

def unescape(h):
    return (h or '').replace('&amp;', '&').replace('&#38;', '&').replace('&#038;', '&')

FILTER_PARAMS = ['cat', 'price', 'q']
ORDER_PARAMS = ['product_list_order', 'product_list_dir']
PAGE_PARAMS = ['p', 'product_list_limit']
ALL_KEYS = FILTER_PARAMS + ORDER_PARAMS + PAGE_PARAMS

def norm_path(p):
    return p

def key(path, query, keys):
    parts = []
    for k in keys:
        v = query.get(k)
        if v is None or v == '': continue
        parts.append('%s=%s' % (k, v))
    parts.sort()
    return norm_path(path) + '?' + '&'.join(parts)

exact_index = {}
anchor_index = {}
for l in listings:
    exact_index.setdefault(key(l['path'], l.get('query', {}), ALL_KEYS), l)
    ak = key(l['path'], l.get('query', {}), FILTER_PARAMS)
    prev = anchor_index.get(ak)
    if prev is None or len(l.get('query', {})) < len(prev.get('query', {})):
        anchor_index[ak] = l

SAFE = [
    (155, '/home-kitchen/bedding/kids-bedding.html'),
    (189, '/home-kitchen/kitchen-dining/kitchen-table-linens.html'),
    (232, '/cell-phones-accessories/cases-holsters-sleeves/flip-cases.html'),
    (71,  '/video-games/nintendo-switch.html'),
    (233, '/video-games/legacy-systems/nintendo-systems.html'),
    (247, '/video-games/pc/virtual-reality.html'),
    (183, '/office-products/office-furniture-lighting/chairs-sofas.html'),
    (273, '/grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses.html'),
    (292, '/grocery-gourmet-food/breads-bakery/cakes.html'),
    (85,  '/grocery-gourmet-food/fresh-meal-kits.html'),
    (179, '/patio-lawn-garden/gardening-lawn-care/plants-seeds-bulbs.html'),
    (191, '/patio-lawn-garden/gardening-lawn-care/pots-planters-container-accessories.html'),
    (50,  '/patio-lawn-garden/patio-furniture-accessories.html'),
    (256, '/electronics/wearable-technology/smartwatches.html'),
    (255, '/electronics/portable-audio-video/mp3-mp4-player-accessories.html'),
    (70,  '/cell-phones-accessories/cell-phones.html'),
    (43,  '/home-kitchen/heating-cooling-air-quality.html'),
    (47,  '/health-household/health-care.html'),
    (149, '/clothing-shoes-jewelry/sport-specific-clothing/competitive-swimwear.html'),
    (153, '/sports-outdoors/fan-shop/footwear.html'),
    (29,  '/sports-outdoors/exercise-fitness.html'),
    (226, '/video-games/legacy-systems/playstation-systems.html'),
]

def pool_for(cid):
    ids = descendants(cid)
    return [p for p in products if listable(p) and any(c in ids for c in p.get('categoryIds', []))]

def parse_price(raw):
    lo, hi = float('-inf'), float('inf')
    for b in str(raw).split(','):
        b = b.strip()
        if not b: continue
        a, _, z = b.partition('-')
        f = float('-inf') if a == '' else float(a)
        t = float('inf') if z == '' else float(z)
        if f > lo: lo = f
        if t < hi: hi = t
    return lo, hi

def price_buckets(pool, anchor):
    """Return list of (label, count_from_source_or_None, price_param)."""
    if anchor:
        for f in anchor.get('filters') or []:
            if f['name'] == 'Price':
                out = []
                for o in f['options']:
                    qs = unescape(o['href']).split('?')[-1]
                    m = re.search(r'(?:^|&)price=([^&]*)', qs)
                    out.append((o['label'], o['count'], m.group(1) if m else ''))
                return out
    vals = [final_price(p) for p in pool if final_price(p) is not None]
    if not vals: return []
    span = max(vals) - min(vals)
    step = next((s for s in (1, 5, 10, 50, 100, 500, 1000, 5000) if span / s <= 10), 10000)
    buckets = defaultdict(int)
    for v in vals:
        buckets[int(v // step) * step] += 1
    ent = sorted(buckets.items())
    out = []
    for i, (frm, cnt) in enumerate(ent):
        last = (i == len(ent) - 1 and len(ent) > 1)
        param = '%s-' % frm if last else '%s-%s' % (frm, frm + step)
        label = '$%.2f and above' % frm if last else '$%.2f - $%.2f' % (frm, frm + step - 0.01)
        out.append((label, cnt, param))
    return out

def main():
    for cid, path in SAFE:
        pool = pool_for(cid)
        anchor = anchor_index.get(key(path, {}, FILTER_PARAMS))
        src = 'capture' if (anchor and any(f['name'] == 'Price' for f in anchor.get('filters') or [])) else 'derived'
        print('=== %s (%d) n=%d facets=%s' % (catbyid[cid]['name'], cid, len(pool), src))
        for label, cnt, param in price_buckets(pool, anchor):
            lo, hi = parse_price(param)
            match = [p for p in pool if final_price(p) is not None and lo <= final_price(p) < hi]
            url = path + '?price=' + param
            captured = key(path, {'price': param}, ALL_KEYS) in exact_index
            flag = ''
            if len(match) <= 2: flag = '  <<<'
            print('   %-24s src=%-4s pool=%-4d param=%-10s exactcapture=%s%s' % (
                label, cnt, len(match), param, captured, flag))
            if len(match) <= 3:
                for p in sorted(match, key=lambda x: x['id']):
                    print('        id=%-7d $%-9s %s' % (p['id'], final_price(p), p['name'][:70]))

main()

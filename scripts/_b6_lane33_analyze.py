import json, os, re, sys
D='/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data'
products=json.load(open(D+'/products.json'))
cats=json.load(open(D+'/categories.json'))
listings=json.load(open(D+'/listings.json'))
if isinstance(cats,dict): cats=cats.get('categories',cats)
byid={p['id']:p for p in products}
def listable(p): return p.get('status')==1 and p.get('visibility',0)>=4 and p.get('inStock')
def fp(p): return p['specialPrice'] if p.get('specialPrice') is not None else p['price']
catbyid={c['id']:c for c in cats}
children={}
for c in cats: children.setdefault(c.get('parentId'),[]).append(c)
def desc(cid):
    out=set([cid]); st=[cid]
    while st:
        i=st.pop()
        for ch in children.get(i,[]):
            if ch['id'] not in out: out.add(ch['id']); st.append(ch['id'])
    return out
SAFE=[155,189,232,71,233,247,183,273,292,85,179,191,50,256,255,70,43,47,149,153,29,226]
def poolfor(cid, price=None, sub=None):
    ids=desc(cid)
    pool=[p for p in products if listable(p) and set(p.get('categoryIds',[])) & ids]
    if sub:
        s=desc(int(sub)); pool=[p for p in pool if set(p.get('categoryIds',[])) & s]
    if price:
        lo,hi=price
        pool=[p for p in pool if fp(p)>=lo and (hi is None or fp(p)<hi)]
    return pool
def parseprice(raw):
    lo=-1e18; hi=None
    for b in raw.split(','):
        a,_,z=b.partition('-')
        f=float(a) if a else -1e18
        t=float(z) if z else None
        if f>lo: lo=f
        if t is not None and (hi is None or t<hi): hi=t
    return (lo,hi)
# index listings by path
by_path={}
for l in listings: by_path.setdefault(l['path'],[]).append(l)
exact=set()
for l in listings:
    q='&'.join(sorted(f"{k}={v}" for k,v in l['query'].items() if v not in (None,'')))
    exact.add(l['path']+'?'+q)
print("=== single-result price facets in safe categories ===")
for cid in SAFE:
    c=catbyid.get(cid)
    if not c: print('missing cat',cid); continue
    path='/'+c['urlPath']+'.html' if not str(c.get('urlPath','')).startswith('/') else c['urlPath']
    ls=[l for l in by_path.get(path,[]) if not l['query']]
    if not ls: 
        print(cid,c['name'],path,'NO CAPTURE'); continue
    l=ls[0]
    for f in l.get('filters',[]):
        for o in f.get('options',[]):
            href=o['href'].replace('&amp;','&')
            qs=href.split('?',1)[1] if '?' in href else ''
            q=dict(x.split('=',1) for x in qs.split('&') if x)
            pool=poolfor(cid, parseprice(q['price']) if 'price' in q else None, q.get('cat'))
            if len(pool)<=2 or o['count']<=2:
                key=href.split('?')[0]+'?'+'&'.join(sorted(f"{k}={v}" for k,v in q.items()))
                print(f"cat{cid} {c['name']!r} {f['name']} {o['label']!r} srccount={o['count']} pool={len(pool)} exactcap={key in exact} -> {[(p['id'],p['name'][:50],fp(p)) for p in pool]}")

print()
print("=== ALL captured listings: facet cells with srccount==1 and pool==1 ===")
seen=set()
for l in listings:
    if l['query']: continue
    path=l['path']
    m=[c for c in cats if '/'+str(c.get('urlPath'))+'.html'==path]
    if not m: continue
    cid=m[0]['id']
    for f in l.get('filters',[]):
        for o in f.get('options',[]):
            if o.get('count')!=1: continue
            href=o['href'].replace('&amp;','&')
            qs=href.split('?',1)[1] if '?' in href else ''
            q=dict(x.split('=',1) for x in qs.split('&') if x)
            pool=poolfor(cid, parseprice(q['price']) if 'price' in q else None, q.get('cat'))
            if len(pool)!=1: continue
            key=href.split('?')[0]+'?'+'&'.join(sorted(f"{k}={v}" for k,v in q.items()))
            if key in exact: continue
            p=pool[0]
            if p['id'] in seen: continue
            seen.add(p['id'])
            print(f"{m[0]['name']!r} (cat {cid}) path={path} facet={f['name']!r} label={o['label']!r} q={q} -> id={p['id']} price={fp(p)} rc={p.get('reviewsCount')} name={p['name'][:70]!r}")

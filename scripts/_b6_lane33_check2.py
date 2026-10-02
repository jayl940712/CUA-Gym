import json
D='/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data'
products=json.load(open(D+'/products.json')); cats=json.load(open(D+'/categories.json'))
catbyid={c['id']:c for c in cats}
children={}
for c in cats: children.setdefault(c.get('parentId'),[]).append(c)
def desc(cid):
    out={cid}; st=[cid]
    while st:
        i=st.pop()
        for ch in children.get(i,[]):
            if ch['id'] not in out: out.add(ch['id']); st.append(ch['id'])
    return out
def fp(p): return p['specialPrice'] if p.get('specialPrice') is not None else p['price']
def listable(p): return p['status']==1 and p['visibility']>=4 and p['inStock']
PICK=[(180,300,400,67979),(87,200,300,7778),(58,200,300,101604),(106,500,600,2631)]


for cid,lo,hi,pid in PICK:
    ids=desc(cid)
    pool=[p for p in products if listable(p) and set(p.get('categoryIds',[]))&ids]
    inband=[p for p in pool if lo<=fp(p)<hi]
    above=sorted([ (fp(p),p['id'],p['name'][:40]) for p in pool if fp(p)>=hi],reverse=True)[:4]
    near=sorted([(fp(p),p['id']) for p in pool if fp(p)<lo],reverse=True)[:2]
    print(f"cat{cid} {catbyid[cid]['name']!r} n={len(pool)} band[{lo},{hi})={[(p['id'],fp(p)) for p in inband]} nextbelow={near} above_hi={above}")

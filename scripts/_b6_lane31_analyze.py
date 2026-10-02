import json, sys
B='/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data/'
P=json.load(open(B+'products.json'))
C=json.load(open(B+'categories.json'))
L=json.load(open(B+'listings.json'))
byid={c['id']:c for c in C}
kids={}
for c in C: kids.setdefault(c['parentId'],[]).append(c['id'])
def desc(cid):
    out=set(); st=[cid]
    while st:
        x=st.pop(); out.add(x); st+=kids.get(x,[])
    return out
def listable(p): return p['status']==1 and p['visibility']>=4 and p['inStock']
def fp(p): return p['specialPrice'] if p['specialPrice'] is not None else p['price']
LIST=[p for p in P if listable(p)]
def pool(cid):
    ids=desc(cid)
    return [p for p in LIST if any(c in ids for c in p['categoryIds'])]

CATS=[155,189,232,71,233,247,183,273,292,85,179,191,50,256,255,70,43,47,149,153,29,226]
FILTER=['q','cat','price']; ORDER=['product_list_order','product_list_dir']; PAGE=['p','product_list_limit']
ALL=FILTER+ORDER+PAGE
def key(path,q,keys):
    parts=[]
    for k in keys:
        v=q.get(k)
        if v in (None,''): continue
        parts.append('%s=%s'%(k,v))
    parts.sort()
    return path+'?'+'&'.join(parts)
exact={}
for l in L: exact.setdefault(key(l['path'],l['query'],ALL),l)
def has_capture(path,q): return key(path,q,ALL) in exact

for cid in CATS:
    c=byid[cid]; pl=pool(cid)
    pl_asc=sorted(pl,key=lambda p:(fp(p),p['id']))
    path='/'+c['urlPath']+'.html'
    caps=[k for k in exact if k.startswith(path+'?')]
    print('%-6s %-52s n=%3d  cheapest %8.2f id%-7d next %8.2f (d=%.2f) | dearest %9.2f id%-7d next %9.2f (d=%.2f)'%(
        cid,c['name'][:52],len(pl),fp(pl_asc[0]),pl_asc[0]['id'],fp(pl_asc[1]),fp(pl_asc[1])-fp(pl_asc[0]),
        fp(pl_asc[-1]),pl_asc[-1]['id'],fp(pl_asc[-2]),fp(pl_asc[-1])-fp(pl_asc[-2])))
    print('       urlPath=%s dbProductCount=%s captures=%s'%(c['urlPath'],c['dbProductCount'],caps))

import json, os, collections
D='/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data'
prods=json.load(open(D+'/products.json'))
cats=json.load(open(D+'/categories.json'))
if isinstance(cats,dict): cats=cats.get('categories',cats)
byid={c['id']:c for c in cats}
child=collections.defaultdict(list)
for c in cats:
    child[c.get('parentId')].append(c['id'])
def desc(cid):
    out={cid}; st=[cid]
    while st:
        i=st.pop()
        for ch in child.get(i,[]):
            if ch not in out: out.add(ch); st.append(ch)
    return out
def listable(p): return p['status']==1 and p['visibility']>=4 and p['inStock']
def fp(p): return p['specialPrice'] if p['specialPrice'] is not None else p['price']
SAFE={155:"kids-bedding",189:"kitchen-table-linens",232:"flip-cases",71:"nintendo-switch",233:"nintendo-systems",247:"virtual-reality",183:"chairs-sofas",273:"deli-meats-cheeses",292:"cakes",85:"fresh-meal-kits",179:"plants-seeds-bulbs",191:"pots-planters",50:"patio-furniture",256:"smartwatches",255:"mp3-mp4-acc",70:"cell-phones",43:"heating-cooling",47:"health-care",149:"competitive-swimwear",153:"fan-footwear",29:"exercise-fitness",226:"playstation-systems"}
listings=json.load(open(D+'/listings.json'))
if isinstance(listings,dict): listings=listings.get('listings',listings)
capq=collections.defaultdict(list)
for l in listings:
    capq[l['path']].append(l.get('query',{}))
out={}
for cid,slug in SAFE.items():
    ids=desc(cid)
    pool=[p for p in prods if listable(p) and any(c in ids for c in p['categoryIds'])]
    pool.sort(key=lambda p:(fp(p),p['id']))
    c=byid[cid]
    out[cid]={'slug':slug,'name':c['name'],'url':c.get('urlPath') or c.get('url_path'),'n':len(pool),'db':c.get('dbProductCount'),
      'rows':[{'rank':i+1,'id':p['id'],'price':fp(p),'name':p['name'],'urlKey':p['urlKey'],'sku':p['sku']} for i,p in enumerate(pool[:14])]}
json.dump(out,open('/tmp/b6l40.json','w'),indent=1)
for cid,v in out.items():
    print('==',cid,v['name'],v['url'],'n=',v['n'],'db=',v['db'])
    for r in v['rows'][:10]:
        print('   ',r['rank'],r['id'],r['price'],r['name'][:60])

# --- margins & capture check ---
print("\n#### MARGINS (rank: price | gap_prev / gap_next)")
data=json.load(open('/tmp/b6l40.json'))
for cid,v in data.items():
    rows=v['rows']
    print('==',v['name'],'/'+v['url']+'.html')
    for i,r in enumerate(rows[:8]):
        gp = round(r['price']-rows[i-1]['price'],2) if i>0 else None
        gn = round(rows[i+1]['price']-r['price'],2) if i+1<len(rows) else None
        print('   r%d id=%s $%s prev=%s next=%s | %s'%(r['rank'],r['id'],r['price'],gp,gn,r['name'][:55]))

print("\n#### CAPTURED SORTED LISTINGS touching safe cats")
L=json.load(open(D+'/listings.json'))
if isinstance(L,dict): L=L.get('listings',L)
paths={('/'+v['url']+'.html'):v['name'] for v in data.values()}
for l in L:
    q=l.get('query',{})
    p=l['path']
    if p in paths and q:
        print(p, q, l.get('totalCount'))

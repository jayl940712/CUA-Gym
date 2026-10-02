import json
D='/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data'
products=json.load(open(D+'/products.json'))
cats=json.load(open(D+'/categories.json'))
byid={p['id']:p for p in products}
catbyid={c['id']:c for c in cats}
CAND=[(155,'80-90',67733),(50,'3000-4000',36234),(70,'1000-2000',100037),(47,'100-200',31299),
      (29,'100-200',13058),(58,'700-800',42614),(52,'20000-30000',41407),(106,'600-700',49878),
      (225,'800-900',42562),(262,'1000-2000',90807),(180,'300-400',67979),(33,'300-400',12664),
      (154,'10000-20000',32036),(101,'500-600',7616),(168,'300-400',72381),(87,'200-300',7778)]
for cid,price,pid in CAND:
    c=catbyid[cid]; chain=[]; x=c
    while x and x['id'] not in (1,2):
        chain.append((x['name'],x['id'],x.get('level'),x.get('isActive'),x.get('includeInMenu'),x.get('position')))
        x=catbyid.get(x.get('parentId'))
    ok=all(a and m for _,_,_,a,m,_ in chain)
    p=byid[pid]
    print(f"cat{cid} menu_ok={ok} chain={[ (n,l,a,m) for n,i,l,a,m,_ in reversed(chain)]}")
    print(f"   path=/{c['urlPath']}.html?price={price}  pid={pid} url=/{p.get('urlKey')}.html sku={p.get('sku')} price={p.get('price')} special={p.get('specialPrice')} listable={p['status']==1 and p['visibility']>=4 and p['inStock']} rc={p.get('reviewsCount')}")
    print(f"   name={p['name']}")

"""Read-only analysis helper for lane 44 (shopping R1 -> A7).

Reimplements the parts of hub/websites/webarena_shopping_mock/src/utils/catalog.js
that decide (a) which products are in a category pool, (b) what the price facet
buckets are, and (c) which products actually RENDER on a given listing URL.
Nothing here writes to hub/.
"""
import json, os, sys
from collections import defaultdict

ROOT = "/home/ubuntu/CUA-Gym/hub/websites/webarena_shopping_mock/src/data"

def load(n):
    with open(os.path.join(ROOT, n)) as f:
        return json.load(f)

products = load("products.json")
categories = load("categories.json")
listings = load("listings.json")
reviewCounts = load("reviewCounts.json")

by_id = {p["id"]: p for p in products}
cats_by_id = {c["id"]: c for c in categories}
cats_by_path = {c["urlPath"]: c for c in categories}
children = defaultdict(list)
for c in categories:
    children[c["parentId"]].append(c["id"])

def listable(p):
    return p["status"] == 1 and p["visibility"] >= 4 and p["inStock"]

def final_price(p):
    return p["specialPrice"] if p["specialPrice"] is not None else p["price"]

def descendants(cid):
    out, stack = set(), [int(cid)]
    while stack:
        x = stack.pop()
        if x in out:
            continue
        out.add(x)
        stack.extend(children.get(x, []))
    return out

def pool_for(cid):
    ids = descendants(cid)
    return [p for p in products if listable(p) and any(c in ids for c in p["categoryIds"])]

FILTER_PARAMS = ["cat", "price", "q"]
ORDER_PARAMS = ["product_list_order", "product_list_dir"]
PAGE_PARAMS = ["p", "product_list_limit"]
ALL_KEYS = FILTER_PARAMS + ORDER_PARAMS + PAGE_PARAMS

def key(path, query, keys):
    parts = []
    for k in keys:
        v = query.get(k)
        if v in (None, ""):
            continue
        parts.append("%s=%s" % (k, v))
    parts.sort()
    return path + "?" + "&".join(parts)

exact_index, anchor_index = {}, {}
for l in listings:
    exact_index[key(l["path"], l["query"], ALL_KEYS)] = l
    ak = key(l["path"], l["query"], FILTER_PARAMS)
    prev = anchor_index.get(ak)
    if prev is None or len(l["query"]) < len(prev["query"]):
        anchor_index[ak] = l

def sort_pool(pool, order, dir_):
    sign = -1 if dir_ == "desc" else 1
    if order == "price":
        return sorted(pool, key=lambda p: (sign * final_price(p), p["id"]))
    return list(pool) if dir_ == "asc" else list(reversed(pool))

def parse_price(param):
    if not param:
        return None
    lo, _, hi = param.partition("-")
    return (float(lo or 0), float(hi) if hi else float("inf"))

def resolve(path, query, cid):
    order = query.get("product_list_order")
    dir_ = query.get("product_list_dir")
    limit = int(query.get("product_list_limit") or 12)
    page = int(query.get("p") or 1)
    pool = pool_for(cid)
    if query.get("cat"):
        ids = descendants(query["cat"])
        pool = [p for p in pool if any(c in ids for c in p["categoryIds"])]
    rng = parse_price(query.get("price"))
    if rng:
        pool = [p for p in pool if rng[0] <= final_price(p) < rng[1]]
    pool = sort_pool(pool, order or "position", dir_ or "asc")
    exact = exact_index.get(key(path, query, ALL_KEYS))
    anchor = anchor_index.get(key(path, query, FILTER_PARAMS))
    total = len(pool)
    if anchor:
        total = anchor.get("totalCount") or (len(pool) if anchor.get("productIds") else 0)
    elif cid is not None and not query.get("cat") and not query.get("price"):
        total = cats_by_id[cid]["dbProductCount"]
    if exact:
        from_cap = [by_id[i] for i in exact["productIds"] if i in by_id]
        if len(from_cap) >= min(limit, total) or len(from_cap) == len(exact["productIds"]):
            items = from_cap
        else:
            seen = set(p["id"] for p in from_cap)
            items = (from_cap + [p for p in pool if p["id"] not in seen])[: min(limit, total or limit)]
    else:
        off = (page - 1) * limit
        items = pool[off: off + limit]
    return dict(items=items, pool=pool, total=total, limit=limit, page=page)

def reachable(path, cid, pid, order=None, dir_=None, limit=12):
    """Does product pid render on ANY page of this browsing mode?"""
    q = {}
    if order:
        q["product_list_order"] = order
    if dir_:
        q["product_list_dir"] = dir_
    if limit != 12:
        q["product_list_limit"] = str(limit)
    first = resolve(path, dict(q), cid)
    pages = max(1, -(-first["total"] // limit))
    for p in range(1, pages + 1):
        qq = dict(q)
        if p > 1:
            qq["p"] = str(p)
        if any(x["id"] == pid for x in resolve(path, qq, cid)["items"]):
            return p
    return None

def price_facets(path, cid, query=None):
    query = query or {}
    anchor = anchor_index.get(key(path, query, FILTER_PARAMS))
    if anchor:
        for f in anchor.get("filters") or []:
            if f["name"] == "Price":
                return [(o["label"], o["count"], o["href"]) for o in f["options"]]
    return None

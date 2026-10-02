from common import an, SHOP_ENV

E = SHOP_ENV
REACH = ("CORRECTIONS #58 (CRITICAL, and no static gate detects it): resolveListing() prefers a "
         "captured page-1 listing while page 2 falls through to pool.slice(), and the two sources are "
         "not consistent, so seeded products can fall into the gap and render on NO page under the "
         "default sort - 4 of 63 in Chairs & Sofas at 12/page and 11 at 36/page. Product 99336 "
         "(DUOREST D2, 100%, 6 reviews), the census's flagship top-rated entity, is one of them: real, "
         "listable, uniquely maximal and unreachable by ordinary browsing. Confirm every browsing-"
         "selected target is reachable in the browsing mode the instruction implies, at every page "
         "size - not merely present in the seed. CORRECTIONS #61: five of the 22 safe categories have "
         "SORTED captures (kids-bedding price desc + name desc, competitive-swimwear price asc, "
         "fresh-meal-kits name asc and p=5 name, heating-cooling-air-quality price asc, "
         "mp3-mp4-player-accessories p=3 name); on those exact URLs the grid renders the capture's ids, "
         "not the derived pool.")
CATNAMES = ("CORRECTIONS #63: two census category names are abbreviated and will not match the rendered "
            "nav - category 191 is 'Pots, Planters & Container Accessories' and category 50 is 'Patio "
            "Furniture & Accessories'. CORRECTIONS #43: the parenthesised numbers in the census's "
            "category table are category IDs, not product counts - Kids' Bedding (155) holds 100 "
            "products, Kitchen & Table Linens (189) holds 112, Flip Cases (232) holds 47.")
TOOLBAR = ("The sort-direction control advertises the direction it will switch TO, not the current one "
           "(Toolbar.jsx:79-82) - never assert on its label. Category sort options are Position / "
           "Product Name / Price only; search pages offer Product Name / Price / Relevance, default "
           "dir=desc, and the Price facet is DELIBERATELY ABSENT there (LayeredNav.jsx:12-26), so never "
           "author 'search for X and filter to under $100'. Zero-result pages render no toolbar at all. "
           "sortProducts' price tie-break is id ASCENDING in both directions (catalog.js:1104). "
           "Product-Name-order superlatives were dropped in batch 5 because JS localeCompare could not "
           "be reproduced deterministically offline - do not build ground truth on name order.")
FROZEN = ("The catalog is a frozen ES import (catalog.js:1) with NO state overlay - only the 15 session "
          "keys (addresses, cart, compareList, contactSubmissions, customer, myReviews, "
          "newsletterSubscribed, the five next* counters, orders, wishlist) are injectable. specialPrice "
          "is null on all 22,460 listable products and is permanently unreachable, so there are no "
          "sale-price tasks. totalCount on an unfiltered category page is the source's dbProductCount "
          "(beauty reads 'of 21 796' against 4,398 seeded tiles) - fatal for 'count the items in this "
          "category' outside the 22 fully-seeded ones, and paging past the seeded pool renders an empty "
          "grid.")
ORDERS = ("Order-history facts: 37 orders spanning 2022-03-02 to 2023-05-18, statuses 25 complete / 9 "
          "canceled / 3 pending - there is genuinely no processing, on-hold or out-for-delivery order, "
          "matching the real source. 2023-04 is EMPTY and 2022-04 has no cancellations. Shipping is "
          "$5.00 per item and shippingAmount === 5 x totalQtyOrdered holds for all 37; grandTotal === "
          "subtotal + shippingAmount with tax and discount both 0. All 100 order lines resolve to real "
          "catalog products. sortedOrders() is full-timestamp descending and nothing else participates; "
          "the grid pages at 10 and the account dashboard's Recent Orders block shows 5. CORRECTIONS "
          "#56: the true page-1 boundary is createdAt > 2023-02-09 07:06:57 - the widely-quoted "
          "'000000157, 2023-02-09 18:50:18' is a mash-up of two rows (157 is stored at 07:06:57; "
          "18:50:18 belongs to 158).")
TZ = ("Timezone: format.js:4 renders every stored UTC stamp in America/New_York and five orders print a "
      "day early - 185 (10/4 -> 10/3/22), 154 (12/19 -> 12/18/22), 163 (1/17 -> 1/16/23), 166 (3/11 -> "
      "3/10/23), 170 (5/18 -> 5/17/23). All five stay inside their month, so MONTH buckets are safe and "
      "DAY buckets are not. Three pending orders 187/188/189 all render 5/2/23 and differ only by "
      "minutes, so 'my latest pending order' resolves only by increment id - never build ground truth "
      "on their displayed date.")

SHOPPING = [
{
 "slug": "price_band_cell_to_cart",
 "skills": ["R5", "A4"],
 "chain": "click into a single price-facet cell on a fully-seeded category, then add the one product it returns to the cart",
 "entities": "CORRECTIONS #42: there are 18 single-result and 9 two-result price cells across 12 of the 22 safe categories - enumerate them, do not treat the census's two examples as the pool. Kids' Bedding's '$80.00 and above' link is ?price=80-90 (a source quirk preserved verbatim) and yields exactly one product, id 67733 (Disney Parks Hidden Mickey reversible throw, $88.99). Kids-bedding's nine buckets are 3/21/31/14/15/6/7/2/1 and flip-cases' are 3/28/10/3/3, both reproducing the source capture exactly.",
 "writeback": "cart.items[] (productId, sku, qty, options[] sorted by sortLineOptions) via addToCart, AppContext.jsx:251",
 "notes": E + " " + REACH + " " + CATNAMES + " " + TOOLBAR + " " + FROZEN + " CORRECTIONS #42: Flip Cases - named as one of the two safest facet playgrounds - has NO cell smaller than three products and cannot express a single-result task at all. CORRECTIONS #40: kids-bedding's ?price=20-30 tie is FOUR-way, not three - 31798, 35795, 66784 AND 86962 all at $29.99 - so an author who took the census id list as exhaustive and excluded three would still ship an ambiguous task. Price filter semantics are v >= from && v < to (catalog.js:1167-1173) and comma-stacked buckets intersect. CORRECTIONS #41: Virtual Reality (247) and Smartwatches (256) get their buckets from the DERIVED branch, not from a recorded capture - counts are still exact against the pool but it is a different code path. Tile Add-to-Cart silently NAVIGATES to the PDP when the product has required options (ProductGrid.jsx:63-66) - route through the PDP. R5->A4 is batch 5's single heaviest pair (15 uses) and is KEPT here exactly once, because R5 is 47% and A4 17% of official shopping instances and it is the site's dominant errand; omitting it would misrepresent the distribution. Batch-5 adjacent: facet_cell_single_result.",
 "analogues": an("shopping", 59, 60, 61, 62),
},
{
 "slug": "category_winner_checkout",
 "skills": ["R5", "A10"],
 "chain": "browse to the category, sort or filter to the item the instruction describes, and place the order for it",
 "entities": "clean price extremes with margins: Deli Meats & Cheeses $6.51 (next $11.67), Chairs & Sofas $25.21 ($36.99), Smartwatches $22.49 ($23.99), Cakes $5.19 ($9.95), Kitchen & Table Linens $4.02 ($5.99), Kids' Bedding $7.59 ($9.99) / $88.99 ($79.95). AVOID PlayStation Systems (cheapest is a $0.99 TIE), Health Care ($0.10), fan-shop Footwear ($0.23) and Fresh Meal Kits ($0.34).",
 "writeback": "a new orders[] row (000000190) with items[] and shippingAddress honouring the selected card, plus an emptied cart and bumped nextOrderEntityId / nextOrderIncrementId (placeOrder, AppContext.jsx:513)",
 "notes": E + " " + REACH + " " + CATNAMES + " " + TOOLBAR + " " + FROZEN + " CORRECTIONS #54: two census margin flags are wrong in BOTH directions - Plants, Seeds & Bulbs is marked sub-$0.30 and is actually $0.50 ($6.49 vs $6.99), so it is USABLE; Fresh Meal Kits carries no warning and is $0.34, narrower than the one that was flagged. The warnings are correct for Health Care ($0.10) and fan-shop Footwear ($0.23). CORRECTIONS #69: there is no bulk 'empty cart' - clearCart exists in AppContext.jsx and is referenced by NO component anywhere in src/, so the three seeded lines 554/555/556 need three separate Remove clicks. A10 on the storefront is PLACE-ORDER ONLY: grep -n cancel over pages/ components/ context/ finds nothing relevant, order status is immutable, and there is no order-address mutator - official 175-179 are impossible here. " + ORDERS + " Batch-5 adjacent: clear_cart_then_buy.",
 "analogues": an("shopping", 131, 132, 133, 173),
},
{
 "slug": "category_spread_wishlist_note",
 "skills": ["R5", "A7"],
 "chain": "derive a fully-seeded category's price spread from its sorted listing, then type that spread into the wish-list row's comment box",
 "entities": "seed-exact spreads: Kids' Bedding $7.59-$88.99 (100 items), Kitchen & Table Linens $4.02-$180.00 (112), Cakes $5.19-$425.88 (69), Smartwatches $22.49-$299.00 (56), Nintendo Switch $3.66-$189.00 (51), Fresh Meal Kits $1.50-$289.99 (98), Exercise & Fitness $0.01-$129.00 (76). These 22 categories are the ONLY ones where a superlative computed on our seed equals the one a human would compute on the real page.",
 "writeback": "wishlist.items[].description (updateWishlistItem, AppContext.jsx:347); the wish list boots empty (data/wishlist.json = {\"items\":[]})",
 "notes": E + " CORRECTIONS #45 - USE THIS, it is the reference structural ordering dependency: WishlistPage.jsx emits no form, no textarea and no Update button at all while the list is empty, so the comment box does not EXIST until the product has been added. The agent cannot do the steps out of order even if it wants to. Prefer that over an ordering dependency that exists only because the sentence says 'first ... then'. " + REACH + " " + CATNAMES + " " + TOOLBAR + " " + FROZEN + " " + "CORRECTIONS #39: the census justifies price-sort safety with 'resolveListing() sorts the seeded pool before slicing', which is true in general and NOT the mechanism on a captured page - there resolveListing returns exact.productIds verbatim (catalog.js:1207-1219) and the derived pool is never consulted. Nothing shipped is broken by this (kids-bedding's price-desc capture leads with 67733, the seed maximum) but do not reason from the stated mechanism on a page- or count-sensitive design. Batch-5 adjacent: price_range_into_wishlist_note.",
 "analogues": an("shopping", 39, 40, 42, 43),
},
{
 "slug": "category_product_review_form",
 "skills": ["R5", "A2"],
 "chain": "browse the category to the product the instruction describes, then submit a review with the stated rating, nickname, summary and body",
 "entities": "any of the 22,460 listable products; 6,044 already carry reviews. Rating radios are Rating_1..Rating_5 with values 16..20 (ProductPage.jsx:262-285); the Reviews tab is reached by setTab('reviews') at ProductPage.jsx:611 and paginates 10 per page.",
 "writeback": "myReviews[] (productId, rating, nickname, title, detail, createdAt) + nextReviewId (submitReview, AppContext.jsx:427-447)",
 "notes": E + " CLICK label[for=\"Rating_N\"] (equivalently #Rating_N_label), NEVER the <input>: globals.css:719 makes it 1x1, opacity:0 and absolutely positioned under its own label, so the centre-point hit test is intercepted. The widget is NOT invisible - globals.css:720-724 gives each label font-size:20px and content '\\2605', five real clickable stars. DOM order is ASCENDING (Rating_1..Rating_5), so the FIFTH radio is five stars - the opposite of Luma's visual reversal, and a positional replay is correct here. Assert on the container's data-rating attribute (ProductPage.jsx:280-282), not on a :checked selector. CORRECTIONS #53: nextReviewId seeds at 400000, not 1 - verify the counter before asserting on any generated id. Do NOT inject myReviews to manufacture a rating superlative: ratingPercent (catalog.js:556-568) re-derives the displayed rating from it, so injection moves a product's visible rating, and a single customer shifting a 12-review average is not something the live source would ever show. " + REACH + " " + CATNAMES,
 "analogues": an("shopping", 153, 154, 156, 157),
},
{
 "slug": "price_cell_pair_to_cart",
 "skills": ["R3", "A4"],
 "chain": "count the products a stated price band returns, then add every one of them to the cart",
 "entities": "the 9 two-result price cells across the 22 safe categories (CORRECTIONS #42 - enumerate against products.json, do not reuse the census's examples). Verified bucket counts: kids-bedding 3/21/31/14/15/6/7/2/1, flip-cases 3/28/10/3/3, both identical to the source capture.",
 "writeback": "cart.items[] - assert the EXACT resulting line set and quantities, never a count",
 "notes": E + " CORRECTIONS #60: the cart's three seeded lines (554/555/556) are the SAME three products as cancelled order 000000170, and line 556's stored optionTypeIds 23919/23922 are exactly what the handler rebuilds from {Size: Large, Color: Blue} - so addToCart/reorder MERGE rather than append and the result is a three-row cart at quantity 2, not a six-row cart. Any rubric of the form 'the cart now holds N+M lines' grades the wrong shape. When a task adds to a collection that already holds something, check whether the handler merges or appends before writing a count-shaped rubric. " + REACH + " " + CATNAMES + " " + TOOLBAR + " " + FROZEN + " Tile Add-to-Cart navigates to the PDP on products with required options. /checkout/cart/configure/id/:itemId/product_id/:productId/ (CartConfigurePage.jsx:82-95, radios #cfg-opt-<optionTypeId>) is click-reachable at CartPage.jsx:256 and seeded line 556 already carries Size=Large / Color=Blue - a distinct, unused reward signature if a variant needs one.",
 "analogues": an("shopping", 14, 16, 126, 128),
},
{
 "slug": "month_spend_contact_form",
 "skills": ["R3", "A7"],
 "chain": "sum a stated month or window of order history, then submit the contact form quoting the figure",
 "entities": "monthly totals (store-TZ, grand totals, all 37 orders): 2022-03 $374.12 (3), 2022-04 $102.82 (2), 2022-05 $298.65 (1), 2022-06 $173.56 (1), 2022-07 $394.82 (2), 2022-08 $153.64 (3), 2022-09 $3,024.38 (2), 2022-10 $3,336.22 (4), 2022-11 $403.18 (3), 2022-12 $203.40 (4), 2023-01 $572.88 (2), 2023-02 $1,354.03 (4), 2023-03 $83.31 (2), 2023-04 EMPTY, 2023-05 $4,130.39 (4). Every non-empty month has a unique answer.",
 "writeback": "contactSubmissions[] with name, email, telephone, comment (submitContact, AppContext.jsx:495) - written ONLY on Submit",
 "notes": E + " The official 'fill the form but do NOT submit' family (024-028, 040-044, 143-147, 158-162, 168-172 - ten-plus templates) is UNSCORABLE against /go: ContactPage.jsx:17-21 holds the typed values in React useState and nothing persists. Every task in this lane must require an actual Submit. This is a gap in our state-only reward channel, not in the mock - the official eval reads the live DOM - so it is parity and must not be 'fixed'. " + TZ + " Month buckets are TZ-safe; day-level spend questions are not. April 2023 and April 2022 cancellations are both empty - official 106 and 101 have zero-valued answers, so do not build on them. Shipping arithmetic is derivable because shippingAmount === 5 x totalQtyOrdered holds for all 37 orders. " + ORDERS + " Batch-5 adjacent: monthly_spend_logged.",
 "analogues": an("shopping", 94, 95, 97, 17),
},
{
 "slug": "review_count_selected_product",
 "skills": ["R3", "A2"],
 "chain": "count the reviews on each candidate that meet a stated rating bound, use the count to pick which product the instruction means, then submit a review on it with dictated fields",
 "entities": "76,378 reviews across 6,044 products. reviewCounts.json (which drives the PDP tab label) matches the review bodies for ALL 6,044 reviewed products; products[].reviewsCount (the grid tile) disagrees for 149 of them. Product 67025 (Lion King blanket) has 3 reviews at <=2 stars.",
 "writeback": "myReviews[] + nextReviewId",
 "notes": E + " The review corpus contains 6,181 DUPLICATE content rows across 3,570 products (distinct reviewId, identical productId+title+detail+nickname+rating; 76,378 rows -> 70,197 distinct content keys) - de-dup on the specific product before fixing a count. CORRECTIONS #77: there is a SECOND duplicate class the census's own key misses - product 47884's reviews 289238 and 289222 share title, detail and rating and differ only in one nickname being the other self-concatenated ('Guillermo RamasGuillermo Ramas' vs 'Guillermo Ramas'), so the key that includes nickname does not find it and 47884 has no defensible name set; the census's '3 reviews at <=2 stars' for it is misleading. A de-dup key that includes the field the corruption lives in will not find the corruption. CORRECTIONS #79: nine of ten audited products carry duplicate pairs and on six the duplicated row is a low-star row, so a COUNT-shaped rubric had two defensible answers on eight of ten tasks - prefer a set-shaped rubric, and where the count IS the graded value, verify the de-dup on that exact product. A '>= N reviews' gate reads differently on the tile than on the PDP, so name the surface. Rating widget rules as in category_product_review_form.",
 "analogues": an("shopping", 32, 38, 153, 155),
},
{
 "slug": "cancelled_month_reorder",
 "skills": ["R2", "A4"],
 "chain": "find the order cancelled in a stated month or window, then reorder it into the cart",
 "entities": "cancelled-order months are 2022-03 (x2), 2022-06, 2022-07, 2022-08, 2022-10, 2023-02 (x2) and 2023-05. Named anchors: order 158 (table lamp, cancelled 2/11/23), 156 (mattress foundation, 2/24/23), 170 (cancelled, 5/17/23 displayed).",
 "writeback": "cart.items[] via reorder (AppContext.jsx:598), which copies the order lines in",
 "notes": E + " CORRECTIONS #60: reordering 000000170 MERGES into the three seeded cart lines and yields a three-row cart at quantity 2 - assert the doubled quantities, not a line count. reorder falls back to line.price on a product miss (all 100 seeded lines resolve, keep it so). CORRECTIONS #52: order-view line items are <strong>, not links (OrderViewPage.jsx:27) - there is NO clickable order-to-PDP path, so any chain that reads an order then acts on the product must route through the header quick search on the SKU or name, and a replay expecting to click a line item fails. " + ORDERS + " " + TZ + " 44 of the 100 seeded order lines already carry non-empty options[] rendered as a dl.item-options (OrderViewPage.jsx:28-31), which makes the official 073-077 'size configuration of the picture frame I bought Sep 2022' shape authorable with no injection. Batch-5 adjacent: reorder_cancelled_item.",
 "analogues": an("shopping", 121, 122, 123, 124),
},
{
 "slug": "window_order_reorder_checkout",
 "skills": ["R2", "A10"],
 "chain": "identify the order inside a stated relative window ('today is <date>, over the past N days'), then reorder it and complete checkout",
 "entities": "the seeded history ends 2023-05-18, so official 006-010's relative windows are degenerate as seeded - inject 2-3 orders dated 6/09-6/11/2023 so a 3-day, a 1-month and a 4-month window each have a distinct non-empty answer. processing and 'On Hold' (state holded) are stock Magento statuses and are in-envelope to inject; statusLabel() capitalises only the first char, so write 'On Hold' pre-cased or it renders 'Holded'.",
 "writeback": "a new orders[] row plus an emptied cart; the injected precondition itself lives in orders + nextOrderEntityId + nextOrderIncrementId",
 "notes": E + " INJECTED-ORDER CHECKLIST, every item mandatory or the lane's arithmetic silently breaks: createdAt > 2023-02-09 07:06:57 for page 1 (CORRECTIONS #56 - the quoted 18:50:18 belongs to order 158, not 157); > 2023-03-11 to appear in the dashboard's 5-row Recent Orders block; UTC clock PINNED to 12:00:00 so America/New_York (08:00 EDT / 07:00 EST) cannot cross a day boundary in either direction in any month, which is what makes day-level tasks safe on injected rows though they are unsafe on seeded ones; entityId >= 190 with BOTH nextOrderEntityId and nextOrderIncrementId bumped past it or a later placeOrder mints a duplicate; line itemIds >= 900 (seeded max 544, placeOrder allocates from max+1 and OrderViewPage renders id=\"order-item-row-<itemId>\"); shippingAmount === 5 x totalQtyOrdered; grandTotal === subtotal + shippingAmount with tax and discount 0; every items[].productId real; status paired coherently with state - the seed only holds (complete,complete), (canceled,canceled), (pending,new). 'Out for delivery' / 'under delivery' (official 081, 093, 098, 099) stays FORBIDDEN: it is not a stock Magento status, and those official tasks may exist precisely because the gold answer is 'there is none'. Record any injected status as a NEW task, never as a port of the official one. " + ORDERS + " " + TZ + " " + E,
 "analogues": an("shopping", 125, 121, 6, 8),
},
{
 "slug": "order_address_into_book",
 "skills": ["R4", "A11"],
 "chain": "open the ordinal order the instruction names, then create the address-book entry the errand implies and set the default flags",
 "entities": "seed address id 26 (101 S San Mateo Dr) is the ONLY address on file. Oldest order 000000169 (3/2/22), newest 000000170 (5/17/23 displayed), latest pending resolves to 189 by increment id only.",
 "writeback": "addresses[] + nextAddressId + customer.defaultBilling / defaultShipping (saveAddress, AppContext.jsx:461-489)",
 "notes": E + " CORRECTIONS #65 (doubly fatal, and it kills the obvious framing): AddressEditPage.jsx:15 computes isOnly = state.addresses.length <= 1 && !!existing, and lines 175-200 replace BOTH the #primary_billing and #primary_shipping checkboxes with a <div class=\"message info\">. With one seeded address, EDITING record 26 renders no default checkbox at all - so 'tick both default flags' is unperformable, and it is pre-satisfied anyway because 26 already IS both. Note the && !!existing: /customer/address/new/ DOES render both boxes on a one-address book, which is what makes the CREATE-flow variant work with no injection. This lane must therefore be a create, or must inject 2-3 addresses first. CORRECTIONS #66: all 37 orders ship to the IDENTICAL address, so 'copy order X's billing address into the book' derives a value already on file and the UNTOUCHED state would score 1.0 - inject differently-addressed orders or change what is derived. CORRECTIONS #70: deleteAddress removes the row without clearing customer.defaultBilling/defaultShipping, leaving a dangling pointer - restrict any delete to a non-default entry. Official 175-179 (change an existing order's delivery address) is impossible: OrderViewPage.jsx renders both addresses read-only and AppContext has no order-address mutator. " + ORDERS + " " + TZ + " Batch-5 adjacent: address_book_move.",
 "analogues": an("shopping", 148, 149, 151, 152),
},
{
 "slug": "nth_cheapest_wishlist",
 "skills": ["R4", "A4"],
 "chain": "sort a fully-seeded category by price, take the row at the stated ordinal position, and add it to the wish list",
 "entities": "the 22 fully-seeded categories are the only safe pool - Kids' Bedding 100, Kitchen & Table Linens 112, Cakes 69, Fresh Meal Kits 98, Patio Furniture & Accessories 92, Health Care 86, Heating/Cooling & Air Quality 85, Pots Planters & Container Accessories 80, Exercise & Fitness 76, Cell Phones 68, Chairs & Sofas 63, Plants Seeds & Bulbs 59, Footwear/fan-shop 58, Smartwatches 56, Virtual Reality 55, Competitive Swimwear 55, MP3/MP4 Accessories 54, Nintendo Switch 51, Nintendo Systems 48, Flip Cases 47, Deli Meats & Cheeses 36, PlayStation Systems 176.",
 "writeback": "wishlist.items[] (addToWishlist, AppContext.jsx:324-346); tile heart a.action.towishlist at ProductGrid.jsx:98-118, PDP at :797-816",
 "notes": E + " CORRECTIONS #26: every published tie audit is RANK-1 ONLY and none of them says so - a clean top-1 margin does not license an ordinal task. Recompute the rank-N vs rank-N+1 boundary for the exact slice each task uses; PlayStation Systems already ties at rank 1 ($0.99 = $0.99) and kids-bedding's $20-30 bucket ties four ways at $29.99. " + REACH + " " + CATNAMES + " " + TOOLBAR + " " + FROZEN + " Batch-5 adjacent: category_cheapest_to_cart and kids_bedding_price_superlative - batch 6 moves off the extreme onto an interior ordinal, which is what makes the boundary check load-bearing.",
 "analogues": an("shopping", 126, 127, 129, 130),
},
{
 "slug": "named_order_address_correct",
 "skills": ["R9", "A11"],
 "chain": "read the billing or shipping address off the order named by number, then correct the matching address-book record to it",
 "entities": "orders are addressed at /sales/order/view/order_id/:id/ reached by the grid's View Order link (OrderHistoryPage.jsx:63); billing address renders at OrderViewPage.jsx:90, shipping method at :86, SKUs at :17,:39. Named anchors used by official intents: 148, 161, 170, 178, 180, 187, 189.",
 "writeback": "addresses[] / customer.* via saveAddress",
 "notes": E + " CORRECTIONS #55 - THE TRAP FOR THIS LANE, and it was found by rule 9: all 37 orders carry shippingDescription 'Flat Rate - Fixed' and paymentTitle 'Check / Money order', so an order's shipping method and payment title are CONSTANTS across the whole corpus and an agent that never opened an order scores full marks. The retrieval must be the address, a SKU, a date or a total - never the shipping method. CORRECTIONS #66 compounds it: all 37 orders also ship to the identical address, so the address itself is only a usable derived value if a differently-addressed order is injected. Store phone is genuinely NULL in storeConfig.storePhone - the honest answer to official 082 is 'N/A'. CORRECTIONS #52: order-view line items are not links; route any follow-up through the header quick search. " + ORDERS + " " + TZ,
 "analogues": an("shopping", 112, 108, 110, 148),
},
{
 "slug": "review_text_match_to_cart",
 "skills": ["R6", "A4"],
 "chain": "read a product's reviews for the described complaint or praise, then act on the product the match points to by adding it to the cart or wish list",
 "entities": "76,378 reviews over 6,044 products, Reviews tab 10 per page. Product 67025 (Lion King blanket) carries 3 reviews at <=2 stars. AVOID 47884 (Serrano ham) - CORRECTIONS #77 - its nickname corruption leaves no defensible name set. Handle 89473 (CORSAIR HS80) with care: CORRECTIONS #78 - it passes a 'mentions wireless' text filter cleanly, but reviewer 'Mike S.' uses the word incidentally about OTHER headsets, so 'mentions wireless' and 'complains it isn't wireless' return different name sets; demote such products to a rating-only predicate.",
 "writeback": "cart.items[] or wishlist.items[]",
 "notes": E + " A word-match predicate can be mechanically clean and still ill-posed (CORRECTIONS #78), and an entity can satisfy every mechanical check while the TASK is ill-posed (CORRECTIONS #58's unreachable 99336 is the other face of the same problem). CORRECTIONS #79: score a SET of nicknames or the exact resulting collection, never a count - nine of ten audited products carry duplicate content pairs and on six the duplicate is a low-star row. De-dup on the specific product first. " + REACH + " " + FROZEN + " Reviews are flat with no replies (A8 is absent from the storefront) and there is no vote control (A9 absent), so the only action available after the read is add-to-collection or a text writeback. Batch-5 adjacent: low_star_reviewer_names (R6->R3->A7) - batch 6 swaps the write for the collection action.",
 "analogues": an("shopping", 0, 3, 5, 126),
},
{
 "slug": "described_need_to_wishlist",
 "skills": ["R8", "A4"],
 "chain": "find a product that meets a described need through the search box or the category tree, then add it to the wish list",
 "entities": "VERIFIED-LIVE need categories with real seed depth (CORRECTIONS #67): power strips 33, air purifiers 12, sunscreens 29, dishwasher detergents 5, plus the census's laundry detergent and toothpaste. DEAD IN THE SEED and recorded nowhere else: there is NO yoga mat (all four 'yoga mat' matches are flip-flops with foam soles), NO hand sanitiser (all eight rows are empty refill bottles), no rain umbrella, no cat litter, no electric kettle and no bathroom scale.",
 "writeback": "wishlist.items[], scored against an author-enumerated id set",
 "notes": E + " CORRECTIONS #68: do NOT enumerate the accepted-answer set from a captured search page. The capture for 'laundry detergent' contains rows that are not laundry detergents - OxiClean stain remover (72399) and two dishwasher detergents - so enumerating from the capture is wrong in both directions. Enumerate from products.json, then check the capture against it. Search requires >= 3 characters (catalog.js:894) over a 64-shard token index and has no Price facet, so a budget clause must go through a category page. " + REACH + " " + FROZEN + " Batch-5 adjacent: semantic_need_to_wishlist - keep the need categories disjoint from that lane's ten.",
 "analogues": an("shopping", 136, 137, 139, 140),
},
{
 "slug": "flagship_price_survey_note",
 "skills": ["R1", "A7"],
 "chain": "identify the single best-rated or most expensive item under a stated filter, then record its price or rating in the wish-list note",
 "entities": "CLEAN rating winners with a >=5-review gate: 48759 Junior's Cheesecake 8\" Raspberry Swirl 100%/10 reviews (Cakes, runner-up 95%), 76219 SHIELDON iPhone 13 Leather Wallet Case 97%/12 (Flip Cases, 93%), 91261 Molinari & Sons Italian Dry Salami 95%/12 (Deli, 85%), 40622 VR Link Cable 15ft 89%/11 (Virtual Reality, 83%), 101046 Smart Watch for Android IP68 87%/12 (Smartwatches, 82%). THIN (2 points): Fat Plants San Diego 92 vs 90, Christmas Red Truck Table Runner 87 vs 85.",
 "writeback": "wishlist.items[].description",
 "notes": E + " DO NOT USE 99336 (DUOREST D2) - CORRECTIONS #58 - it is unreachable by ordinary browsing on the default sort and a task naming it has two defensible answers depending on how the agent browses. RATING TIES: Kids' Bedding (14535 = 13849 at 100%), Nintendo Switch (75929 = 75515 at 97%), Nintendo Systems (89115 = 89401 at 100%), and CORRECTIONS #59 adds two the census omits - Patio Furniture (50) has a FOUR-WAY tie at 92% (three-way at floors 6-12) and PlayStation Systems (226) a THREE-WAY tie at 100% at floor 5. ZERO products with >=5 reviews in Competitive Swimwear AND in fan-shop Footwear (153) - the census attributes that only to swimwear. products[].reviewsCount (the tile) disagrees with the review bodies for 149 products while reviewCounts.json (the PDP tab label) matches for all 6,044, so a '>= N reviews' gate reads differently on the two surfaces and the instruction must name which one is authoritative. Same structural ordering dependency as category_spread_wishlist_note: the wish-list textarea does not exist until the item is added. " + REACH + " " + CATNAMES + " " + TOOLBAR + " Batch-5 adjacent: top_rated_min_reviews and sorted_survey_writeback.",
 "analogues": an("shopping", 49, 50, 52, 53),
},
]

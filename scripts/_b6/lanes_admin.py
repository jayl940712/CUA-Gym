from common import an, ADMIN_ENV

E = ADMIN_ENV
REPORTS = ("REPORT LIVE/FROZEN SPLIT, proven by probe not inferred (sid revprobe8281 injected 3 reviews "
           "for product 39: Reviews By Products recomputed 4 -> 7 while Coupons still rendered '0 records "
           "found'). FROZEN - bundled ES imports outside the 44 state keys, no injection reaches them: "
           "Orders, Tax, Invoiced, Refunded, Shipping, Coupons, Product Views, Bestsellers "
           "(SalesReports.jsx:3 plus reportAggregatesOrder.json :12, bestsellersAggregates.json :13, "
           "reportOrderActualColumns.json :14). LIVE - recomputed from session state, injectable: Order "
           "Count, Order Total, New Accounts, Ordered Products, Reviews By Products, Reviews By "
           "Customers (LegacyReports.jsx:8-10 imports getOrders/getReviews/getProducts from "
           "selectors.js). Permanently empty: Coupons (coupons_aggregated []), Product Views "
           "(viewed_daily/monthly/yearly all []), Low Stock (arbitrated parity - do NOT re-open by "
           "raising notify_stock_qty), Downloads / Products in Cart / Abandoned Carts (literal rows={[]}). "
           "One data point only: Refunds (one store-0 row at 2023-04-19, so 'refund report for Q1 2023' "
           "returns ZERO rows and the taxonomy doc's canonical hard example is dead), Invoiced ($39.64), "
           "Tax ($2.64 on 2022-04-24 once the default status filter drops the canceled row). Inert "
           "controls: the Empty Rows select (no report reads show_empty_rows; its helper periodRange() is "
           "imported nowhere), the scope switcher (scopeRows hardcodes storeId = 0), Refresh Statistics "
           "(stamps systemConfig.report_statistics and recomputes nothing; the 'Last updated: Jun 17, "
           "2023' banner is hardcoded at ReportPage.jsx:417). There are NO relative-date presets anywhere "
           "in Family A - the agent must compute and type M/D/YYYY - and a bare page load renders an empty "
           "grid because `applied` requires a from-or-to date.")
YEARTRAP = ("CORRECTIONS #94 (the most dangerous mechanism in the batch, because it produces a wrong "
            "answer that LOOKS right): a window straddling a year boundary but shorter than a year at "
            "Period=Year emits only the earlier interval - 6/1/2022-5/31/2023 renders the 2022-01-01 "
            "bucket and every 2023 order in range simply vanishes, with no error and no empty state. "
            "CORRECTIONS #93 is the rescue: intervalsBetween steps a year period one calendar year at a "
            "time, so ANY From/To staying inside one calendar year renders a single interval "
            "(1/1/2023-3/31/2023 at Period=Year is one ranked table covering exactly Q1). CORRECTIONS "
            "#87/#92: the all-history per-customer figures the census quotes appear on NO screen - "
            "buildGroups emits only the buckets intervalsBetween produces and periodKey truncates to "
            "day/month/year, so no configuration spans 2022 and 2023 in one row; Grace Nguyen's 'Order "
            "Count 10' and the 'Order Total top-1 $1,644.48 margin $212' are both unrenderable, and the "
            "latter is also arithmetically wrong (recomputing gives $1,464.48 with the runner-up at "
            "$1,277.00, margin $187.48 - the published number looks like a transposition).")
GRIDS = ("Grid defaults differ per grid and must be checked individually: orders created_at DESC, "
         "products qty ASC, customers name ASC, review ratings rating_code ASC. CORRECTIONS #89: "
         "GRID_PAGE_SIZES overrides the defaultPageSize prop - ProductGrid passes 20 but "
         "gridUtils.defaultPageSizeFor maps product_listing to 200, so any 'N rows against a page size of "
         "20' reasoning computes against the wrong number. CORRECTIONS #88: the Orders grid has NO "
         "'Pending' status filter - ORDER_STATUS_FILTER_OPTIONS is canceled, closed, complete, fraud, "
         "holded, payment_review, paypal_canceled_reversal, paypal_reversed, processing - so route R5 "
         "through the keyword search (gridUtils.js:132-138, which searches hidden columns), the Purchase "
         "Date range filter or the Grand Total range filter. Suspected Fraud IS in that list, which turns "
         "the dead `fraud` status into a filterable queue once injected.")
REVIEWS = ("Review-surface rules: there is NO rating column and no rating filter on the Reviews grid "
           "(LegacyReviewGrid.jsx:415-440) - star values live only on the review edit form, so any "
           "'all N-star reviews' task must be small enough to open each review (the 5 pending ones "
           "qualify; the 351 total do not). The Pending Reviews grid has no status filter either "
           "(showStatus false, Reviews.jsx:181). CORRECTIONS #98: there is a SECOND per-product review "
           "list the census never mentions - ProductReviews under the product page's 'Product Reviews' "
           "section (ProductEdit.jsx:1462, table :1754-1793) - and it is the most natural click path. "
           "CORRECTIONS #97: it reads RAW state.reviews while every other surface goes through "
           "getReviews(state), which filters deletedReviewIds (selectors.js:252-259), so after a delete "
           "the grid and the report have dropped the row and the product page still shows it. "
           "CORRECTIONS #102: when two surfaces disagree the INSTRUCTION must name the one it means "
           "('in Reports', 'Reports > Reviews > By Products'); a terse instruction may omit the click "
           "path but may not omit which surface is authoritative. CORRECTIONS #103: the stale rows link "
           "to /admin/review/product/edit/id/<id>/ for reviews already deleted, where getReview returns "
           "null and the page renders 'Rating isn't Available' - confusing to an agent, harmless to a "
           "rubric that grades deletedReviewIds. Reviews By Products COUNTS are live; the Average and "
           "Average(Approved) columns are a FROZEN lookup (ratingVoteAggregates.json, 254 rows) - a probe "
           "injected 3 reviews and the count moved 4 -> 7 while the average stayed at 65.0000. GRADE THE "
           "COUNT, NEVER THE AVERAGE.")
WIZARD = ("Configurations-wizard rules: CORRECTIONS #80 - there are 147 configurable products, not the "
          "five the census names, every one carrying configurable_attributes ['size','color']. "
          "CORRECTIONS #83 - all 147 have a COMPLETE size x colour matrix, so 'fill the hole in the "
          "matrix' has no seeded material and every task must ADD a new value to one axis. CORRECTIONS "
          "#82 - sizes 30 and 31 already exist as Size option values (ids 173/174 on attribute 144, 20 "
          "options), so adding them is a SINGLE-page wizard task; only the extended tops (XXS/XXL/XXXL) "
          "genuinely need the two-page attribute round-trip, which is exactly why official 138/139 are "
          "the two-page tasks and 140 is not. CORRECTIONS #81 - SOURCE_FRONTEND_INPUT maps size -> "
          "'swatch_text', so the visible add-option control is #add_new_swatch_text_option_button and "
          "#add_new_option_button renders display:none; and saving Size writes frontend_input "
          "'swatch_text' into productAttributeOverrides[\"144\"], after which configCandidates "
          "(ProductEdit.jsx:510-513, filtering === 'select') DROPS Size from the wizard's step-1 table. "
          "Generation still works because openWizard pre-seeds wizard.attrs from the parent's "
          "configurable_attributes and step 2 renders from attributeByCode - a reviewer must not read the "
          "missing step-1 row as a failed task. You cannot create a new option value inside the wizard "
          "(step 2 renders existing options only) and 'Create New Attribute' navigates away and discards "
          "all wizard state. No inline price/qty editing in the variations matrix - the cells are plain "
          "<span>s - and a configurable PARENT's price and quantity inputs are disabled and excluded from "
          "the patch. CORRECTIONS #86: MH05's parent (entity 126) carries price: null.")
NAMES = ("Official product names do not always identify: 'Chloe Tank' is really Chloe Compete Tank "
         "(WT06) and 'Cora Pant' is Cora Parachute Pant - the same trap is a family, not a one-off. "
         "CORRECTIONS #90: under the grid's keyword search `ryker` matches 32 rows (MS09 Crew-neck AND "
         "MS02 V-neck) and `helios` matches 22 (MS05 EverCool Tee AND MT04 Endurance Tank), so a reward "
         "grading 'all the helios hits' would grade 22 rows where the right answer is 6. Search every "
         "official name against the seed before treating it as identifying, and prefer turning a "
         "collision into a stated distractor over avoiding the name.")
GATE = ("CORRECTIONS #84/#110: express 'nothing else moved' as a GATE on the outcome components, never "
        "as a paid component. A component whose truth condition is the ABSENCE of a mutation is true on "
        "{} by construction, so a distractor can never carry weight of its own. Compute a _scope_ok "
        "predicate over the untouched rows and AND it into every paid component: an over-broad sweep then "
        "scores 0.0 rather than a docked 0.8, the agent gets nothing for restraint, and everything is "
        "lost for disturbing scope. Consequence for metadata: exclusion_constraint must come OFF "
        "hard_criteria, because that slug asserts the exclusion is scored and it no longer is. The "
        "alternative correct shape is a single exact-set statement, false on {} because the expected set "
        "is non-empty.")

ADMIN = [
{
 "slug": "qty_range_bulk_attributes",
 "skills": ["R5", "A4"],
 "chain": "filter the Products grid by a quantity range, then apply one bulk attribute update to exactly the rows it matched",
 "entities": "the entire stockItems.json qty domain is {0, 3, 4, 14, 100} - there are NO rows at 10 without injection (official 045 has no seeded answer). Usable anchors: WH11-S-Blue (3), WS08-XS-Blue (3), MSH09-36-Black (4). Update attributes is an in-page form (ProductGrid.jsx:527-577) with #bulk-price, #bulk-qty, #bulk-status, #bulk-stock-status, #bulk-visibility -> applyBulkAttributes :487-502 -> patchProduct :498.",
 "writeback": "productOverrides[<entity_id>].{qty, salable_quantity, is_in_stock, status, visibility, price}; getProducts merges the override over each seed row at selectors.js:166-180 so the patched value is real everywhere the selector is used",
 "notes": E + " " + GRIDS + " CORRECTIONS #72a: 150 of the 2,040 stock rows carry qty 0.0 (every configurable/grouped/bundle parent), so an injected qty-10 row does NOT sort to the front under the grid's qty ASC default - it lands around page 8 at the 20-row default. Right conclusion, wrong mechanism: the reachable route is the Quantity RANGE FILTER (ProductGrid.jsx:176-178), not the sort. CORRECTIONS #72b: 'products with fewer than 5 units' also matches all 150 qty-0 rows and they are all is_in_stock: 1, so adding 'in stock' does not rescue it - every predicate in this lane must state a LOWER BOUND (1-5, 3-3, 1-14). The bulk form sets ABSOLUTE values, never a %-delta; an all-blank submit closes silently with no message and no state change; the :481 reset omits is_in_stock but CORRECTIONS #73 narrows the leak to two bulk edits within a single page mount, not across a fresh load. " + GATE + " Batch-5 adjacent: restock_shorted_variants. R5->A4 is batch 5's heaviest pair (15 uses) and is kept once here because R5 is 19% and A4 11% of official shopping_admin and the site's actions are almost always applied to a matched set - A4+A5+A6 are 72% of all official actions.",
 "analogues": an("shopping_admin", 45, 47, 48, 49),
},
{
 "slug": "conditional_restock_stock_status",
 "skills": ["R5", "A13"],
 "chain": "filter the grid to the arriving SKU, then act conditionally - add to the existing stock if any exists, and additionally flip the stock status to in-stock if it did not",
 "entities": "CORRECTIONS #74: entity 872 / MP12-33-Blue is the ONLY row of all 2,040 with is_in_stock: 0. That single fact makes the official conditional expressible over the PRISTINE seed with no injection, which matters because A13 is the scarcest skill in the corpus and every other instance in batch 5 had to be manufactured. Pair it against an in-stock sibling so the same instruction resolves the opposite way on a second task.",
 "writeback": "productOverrides[872].{qty, salable_quantity, is_in_stock}",
 "notes": E + " " + GRIDS + " The branch must be genuinely reachable both ways within the lane, or the conditional is theatre: batch 5 measured a reddit conditional that was 88/95 solvable by always taking one branch, which is why its reference implementation injects two MATCHED pairs differing only in the branch-deciding field so memorising the entity buys nothing. Do the same here - 872 supplies one arm for free, the other arm must come from an in-stock SKU with the same instruction wording. A13 is 2% of official shopping_admin (3 templates), so ONE lane is the correct weight; it is also the only home for A13 in batch 6, since official reddit and shopping have zero A13 and gitlab has 1%. " + GATE,
 "analogues": an("shopping_admin", 168, 169, 170),
},
{
 "slug": "praise_count_description",
 "skills": ["R3", "A7"],
 "chain": "count a product's reviews at or above a stated star bound, then rewrite that product's description to carry the count",
 "entities": "review status split is 346 Approved / 5 Pending / 0 Not Approved across 351 rows. Antonia Racer Tank has 3 reviews at 2/3/4 stars, so the 4-star-or-above count is 1; Chloe Compete Tank has 5/4/2, so the count is 2. 'disappointed' matches exactly 6 reviews (ids 37, 146, 168, 172, 351, 353).",
 "writeback": "productDescriptionOverrides[<id>] via setProductDescription (ProductEdit.jsx:390), reached through #product-description at :1049-1057",
 "notes": E + " " + REVIEWS + " " + NAMES + " CORRECTIONS #99: setProductDescription is UNCONDITIONAL on an existing-product save - only the new-product branch at :382 is guarded by if (form.description) - so opening a product and pressing Save with no edit writes the seeded description into the overlay and creates a real diff. Gate on the recorded VALUE by fullmatching a sentence frame, never on the key existing. Official 101 is the exact shape ('{count} customer(s) love it!' with a fallback when there are none) - keep the shape, change the product and the bound. Pick products where the count is unambiguous and the star bound is not a boundary dispute, and de-dup first. Batch-5 adjacent: quantify_the_praise.",
 "analogues": an("shopping_admin", 101, 132, 134, 135),
},
{
 "slug": "matched_review_set_purge",
 "skills": ["R3", "A4"],
 "chain": "count the reviews matching a stated predicate, then bulk-delete or bulk-approve exactly that set",
 "entities": "the pending queue is 5 rows across two products and every review those two products have is pending, so the arithmetic is unambiguous: Olivia 1/4 Zip Light Jacket (pk 1396) has 3 reviews - 5 stars id 347, 3 stars id 349, 1 star id 351 - and deleting the sub-4-star ones leaves exactly 1; Circe Hooded Ice Fleece (pk 1210) has 2 - 4 stars id 352, 1 star id 353 - and leaves exactly 1. Both exact, no tie. 'disappointed' -> exactly 6 reviews.",
 "writeback": "deletedReviewIds[] (deleteReviews, Reviews.jsx:140) and/or reviews[i].status_id via Update Status (:146-156)",
 "notes": E + " " + REVIEWS + " Route replays through the Reviews GRID and the report, never through ProductEdit - CORRECTIONS #97 makes a delete-then-count chain fatal if the agent can reach the count from the product page. CORRECTIONS #28: the review grid is the ONLY grid whose mass action receives a second argument (LegacyReviewGrid.jsx:271); LegacyGrid.jsx:367 calls onApply(selected) with one argument everywhere else, and a blank status silently no-ops (Reviews.jsx:148). Official 021's 'Not Approved reviews' count is degenerately 0 on the seed; `reviews` is a full 351-row persisted key, so flipping status_id/status_code on a handful is bucket (a) and well inside Magento's envelope. " + GATE + " Batch-5 adjacent: review_purge_then_report and pending_review_triage - batch 6 keeps the count and the bulk apply and drops the report read-back, which belongs to report_figure_custom_variable.",
 "analogues": an("shopping_admin", 174, 171, 172, 173),
},
{
 "slug": "family_variant_matrix_extend",
 "skills": ["R6", "A6"],
 "chain": "find the configurable family by keyword search, then add a new option value to every one of its existing variants through the Configurations wizard",
 "entities": "147 configurables to choose from. Verified: Diana Tights WP06 (parent 1854, 6 children, sizes 28/29 x Black/Blue/Orange), Phoebe Zipper Sweatshirt WH07 (parent 1130, 15 children), Sahara Leggings WP05 (parent 1847, size-28 children WP05-28-{Blue,Gray,Red} all $75), Hollister Backyard Sweatshirt MH05 (parent 126, 15 children at $52, parent price null), Chloe Compete Tank WT06 (parent 1764). Size and colour live on the child simple rows only; parents carry color: null.",
 "writeback": "newProducts[] (one per generated combination, addProduct at ProductEdit.jsx:639) + productOverrides[<parent>].{configurable_attributes, configurable_children} (:640-646)",
 "notes": E + " " + WIZARD + " " + NAMES + " " + GRIDS + " The wizard is a real 4-step modal, not a stub: div.modal-slide._show[data-role=\"configurable-wizard\"] at :1170, step rail :1186-1195, #wizard_next :1205 validated by wizardNext:581, #generate_configurations :1208, step-1 checkboxes input[name=\"attributes[]\"] :1240-1263, step-2 input[name=\"configurable[<code>][]\"] :1305-1317, step-3 bulk price/qty modes :1338-1382. It is the deepest click path on the site (Catalog > Products > filter > parent > Configurations > 4-step modal) and is still 10/10 from /. " + GATE + " Batch-5 adjacent: tights_size_matrix - use parents disjoint from that lane's ten.",
 "analogues": an("shopping_admin", 136, 137, 138, 139),
},
{
 "slug": "variant_run_pct_reprice",
 "skills": ["R6", "A5"],
 "chain": "search out the size or colour run, then apply the stated arithmetic to its price",
 "entities": "Sahara Leggings size-28 children WP05-28-{Blue,Gray,Red} are ALL $75 - a uniform seed price is what lets one absolute value in the bulk form express a uniform percentage in a single shot. Diana Tights WP06 children and Hollister MH05's 15 children (all $52) have the same property. A run with differing prices does not.",
 "writeback": "productOverrides[<id>].price for each member of the run (buildPatch, ProductEdit.jsx:350-358, or applyBulkAttributes for the uniform case)",
 "notes": E + " There is NO percentage delta anywhere: #bulk-price sets an ABSOLUTE value (ProductGrid.jsx:487-502), so a '+23%' over variants with differing prices requires N individual edits through each child's own edit page, and the child edit page re-seeds on id change (:213-221). CORRECTIONS #85: choose percentages that land on <= 2 decimals - batch 5 declined to reuse the official 13.5% because 13.5% of $75 gives 64.875, which has two defensible roundings and produces an unfixable dispute between a correct agent and a correct rubric. " + WIZARD + " " + NAMES + " " + GRIDS + " " + GATE + " A5 and A6 exist ONLY on shopping_admin among the four sites (gitlab has no field a control mutates arithmetically - time tracking is an opaque free-text string written on blur; reddit and the shopping storefront have no editable numeric field but cart/wishlist qty), so this lane and family_variant_matrix_extend are load-bearing for batch-6 skill coverage. Batch-5 adjacent: size_run_reprice.",
 "analogues": an("shopping_admin", 177, 178, 180, 182),
},
{
 "slug": "ordinal_order_cancel",
 "skills": ["R4", "A10"],
 "chain": "order the sales grid to pick out the ordinal order the instruction names, then cancel or hold it",
 "entities": "newest pending is 000000299 (2023-05-31) and all pending-order timestamps are distinct; oldest complete billing name is John Lee (000000260, 2022-01-08); most recent canceled is 000000136 (Lily Potter / harrypotterfan1@gmail.com). Status counts: complete 153, canceled 142, pending 10, processing 2, closed 1. Last-5-pending total $885.40; last-2-complete total $182.40. Grace Nguyen owns pending 000000065 ($210.00), 000000307 ($101.20) and 000000308 ($175.40).",
 "writeback": "orderOverrides[<entity_id>].{status, state}",
 "notes": E + " " + GRIDS + " getOrderGridRows (selectors.js:115-137) merges only status, grand_total and updated_at from the patch - enough for the grid's Status cell and its status filter, and nothing else. CORRECTIONS #106: orderStatuses.json has no state 'pending' row, so #history_status renders ZERO options on a pending order - never try to change an order's status from the comment box. The `fraud` status is declared in orderStatuses.json but carries 0 rows; patching it onto an ALREADY-RECENT order (299, 65, 308) keeps the row on page 1 under created_at DESC and is in-envelope, and Suspected Fraud is in the filter list, so it buys a filterable queue that pending cannot offer. Beware the self-sabotage documented in batch 5: cancelling orders decrements the very Order Count row a follow-up would read, and after cancelling Grace's three pending orders the top of that report becomes a 3-way tie - so a task must ask for a named customer's own row, never for 'the top customer'. This lane stops at the cancellation and does not read anything back. Batch-5 adjacent: cancel_then_order_count.",
 "analogues": an("shopping_admin", 102, 103, 104, 105),
},
{
 "slug": "pending_queue_bulk_approve",
 "skills": ["R4", "A4"],
 "chain": "take the ordinal slice of the pending review queue the instruction names, then bulk-approve or bulk-delete exactly those rows",
 "entities": "only 5 pending reviews exist - ids 347 (5 stars), 349 (3), 351 (1) on Olivia 1/4 Zip Light Jacket (pk 1396) and 352 (4), 353 (1) on Circe Hooded Ice Fleece (pk 1210). An ordinal slice must therefore be <= 5 and stated as an exact set.",
 "writeback": "reviews[i].status_id / status_code, or deletedReviewIds[]",
 "notes": E + " " + REVIEWS + " Assert the exact resulting status map, not a count - and note that the ratings are only on the review EDIT form, so the agent is genuinely forced to open each of the five, which is what makes this a real multi-hop rather than a grid sweep. Injecting Not Approved rows into the 351-row `reviews` key is bucket (a) and is a state real Magento reaches routinely, which is how official 021 becomes non-degenerate. " + GRIDS + " " + GATE,
 "analogues": an("shopping_admin", 171, 174, 19, 20),
},
{
 "slug": "report_figure_custom_variable",
 "skills": ["R10", "A7"],
 "chain": "configure a report over a stated date window and period, then record the figure it produces in a new custom variable",
 "entities": "Shipping Report 2022 = 215 orders / $3,145.00 (backed by 516 real aggregate rows; uniquely excludeCanceled=false at SalesReports.jsx:271) and 2023 = 85 / $1,270.00. Orders Report 2022 = 116 orders / $15,475.46, 2023 = 42 / $5,873.48. Ordered Products totals 510 for 1/1/2022-12/31/2023. Order Count 2022 is documented in-file as 36 rows / 116 orders / $13,695.82. systemConfig.variables seeds EMPTY, so one new row is an unambiguous diff - the best writeback slot on the site. Form fields code, name, html_value, plain_value (Tools.jsx:989-994) -> useSystemCollection('variables','variable_id').add at :1005-1007.",
 "writeback": "systemConfig.variables[]",
 "notes": E + " " + REPORTS + " " + YEARTRAP + " CORRECTIONS #76: Custom Variables are CREATE-ONLY - App.jsx registers only /admin/admin/system_variable (:356) and .../new (:434), there is no edit/id/:id route, CustomVariables (Tools.jsx:26-53) passes no rowHref so grid rows are not links, and the existing/update/remove branches of CustomVariableForm are unreachable dead code. A 'fill in the pre-seeded placeholder variable' task is not authorable; use an append shape. Because the merge is shallow, systemConfig must be re-posted whole - read it back from /go and patch. The taxonomy doc's canonical hard example ('compute last quarter's refund total, write it into a CMS block') is DEAD: Refunds returns zero rows for Q1 2023. The Shipping 2022 figure is the working substitute. R10 exists on NO other site in this batch - gitlab's only period control computes from new Date() and R10 is 0% of official gitlab, reddit has no reporting surface at all, and the shopping storefront has none - so this lane and report_winner_price_rule carry R10 for the whole batch. R10->A7 is a heavy batch-5 pair (7 uses) and is KEPT here, because R10 is 14% of official shopping_admin (its signature skill) and A7 is its only clean persistent writeback. Batch-5 adjacent: shipping_revenue_ledger.",
 "analogues": an("shopping_admin", 162, 161, 156, 159),
},
{
 "slug": "report_winner_price_rule",
 "skills": ["R10", "A2"],
 "chain": "run the report that ranks the thing, then create a cart price rule named for the winner with the stated discount type and amount",
 "entities": "top search term is 'hollister' with popularity 19, margin 15 over the runner-up at 4 - very safe. cartPriceRules (4 seeded rows) and coupons (1) are both persisted state keys and Marketing writes both on save.",
 "writeback": "cartPriceRules[] and, where a coupon code is stated, coupons[]",
 "notes": E + " WIRE THE REWARD TO state.cartPriceRules, NEVER TO THE COUPONS REPORT: coupons_aggregated is [] (SalesReports.jsx:344/:364), so creating a rule or a coupon will never make a row appear there and a reward asserting on the report fails a correct rollout. CORRECTIONS #107: the Dashboard's Top Search Terms panel renders the ranking directly (Dashboard.jsx:67-72), so a naive 'top search term' task is answerable from the LANDING PAGE without ever opening the report - the R10 and R1 claims would both be unearned. The panel filters num_results > 0, which cuts two ways: a ZERO-RESULT-query predicate has a genuinely exclusive route through the report, and an injection patching a term's result count to 0 drops it from the panel AND the report consistently, so no single screen is contradicted. CORRECTIONS #108 is the reference repair: rebuilding around 'queries returning ten or more products' resolves to Joust Bag (4 hits / 10 results, margin 2, no tie) while the unfiltered leader hollister returns only 1 product and is EXCLUDED by the predicate - so an agent that skips the retrieval names the wrong rule and scores 0.0. A repair that merely adds a retrieval id to the metadata would have passed the gate and trained nothing. " + REPORTS + " " + YEARTRAP + " Batch-5 adjacent: search_term_promotion.",
 "analogues": an("shopping_admin", 151, 152, 154, 155),
},
{
 "slug": "bestseller_price_bump",
 "skills": ["R1", "A5"],
 "chain": "identify the year's best-selling product from the Bestsellers report, then apply the stated arithmetic to its price",
 "entities": "2022 bestseller is Quest Lumaflex(TM) Band at qty 5, margin 1 over a THREE-WAY tie at 4; 2023 is Sprite Yoga Strap 6 foot at qty 4, margin 1. Both are safe at rank 1 and only at rank 1. Top-3 bestsellers for Jan 2023 is a FIVE-WAY TIE at qty 2 and is unusable - and it is NOT injectable, because BestsellersReport calls bestsellersRows(bestsellerAggregates, ...) at SalesReports.jsx:411 reading the bundled bestsellersAggregates.json (:13), never getOrders(state). The tie is permanent; use the yearly figures.",
 "writeback": "productOverrides[<id>].price",
 "notes": E + " " + REPORTS + " CORRECTIONS #100: bestsellersRows has TWO rendering paths for the same year - a from/to inside one calendar year takes the same-year branch (reportUtils.js:265-269), disables the main select and returns a boundary select over bestsellers_daily, while a multi-year range reads bestsellers_yearly by rating_pos. Batch 5 recomputed both rather than assuming: they AGREE at rank 1 for 2022 (entity 20, qty 5) and 2023 (entity 33, qty 4), but that is a fact about this seed, not a property of the code, and nothing would signal a conflict on a different seed. CORRECTIONS #101: recomputing all three graded figures from orders.json (non-canceled, by calendar year) matches the bundled aggregate exactly - 24-UG01/2022 = 5, 24-WG085/2023 = 4, 24-WB07/2023 = 3 - so the LIVE Ordered Products report gives the same answer and neither route is a cheat; that closes the alternative-route risk as well as the correctness one. " + YEARTRAP + " Choose percentages landing on <= 2 decimals (CORRECTIONS #85). Batch-5 adjacent: promote_the_bestseller (R2->R10->R1->A7) - batch 6 keeps the superlative and swaps the write for an arithmetic mutation.",
 "analogues": an("shopping_admin", 0, 6, 95, 98),
},
{
 "slug": "superlative_product_disable",
 "skills": ["R1", "A10"],
 "chain": "identify the product or product family a stated superlative names, then disable it or mark it out of stock",
 "entities": "families with clean membership: MH05 Hollister Backyard Sweatshirt (15 children), WH07 Phoebe Zipper Sweatshirt (15), WT06 Chloe Compete Tank, Taurus Elements Shell, Gobi HeatTec Tee, Aeon Capri. For a stock-based superlative, note the two qty-3 rows (WH11-S-Blue, WS08-XS-Blue) TIE at rank 1, so 'the lowest-stock in-stock product' has no unique answer - phrase it as a bounded range WITH A LOWER BOUND. Top search term hollister (19, margin 15) is a safe superlative but see the Dashboard leak.",
 "writeback": "productOverrides[<id>].status = 2 (Disable) and/or .is_in_stock = 0, via the Products grid mass action (ProductGrid.jsx:463-473) -> patchProduct",
 "notes": E + " " + NAMES + " Turn the ryker/helios collision into a SEEDED DISTRACTOR rather than avoiding the name: a collision that defeats a careless agent is difficulty, one that defeats the rubric is a bug, and the difference is whether the instruction disambiguates. " + GATE + " Concretely: disabling all 32 ryker hits must score 0.0, not 0.6, because the gate withdraws both components rather than docking one - and the batch-5 repair that made this task STRICTER rather than looser is the model. CORRECTIONS #72b applies to any 'fewer than N units' phrasing. " + GRIDS + " CORRECTIONS #107's lesson generalises: check whether the Dashboard or any other landing surface already answers the superlative before claiming R1. Batch-5 adjacent: retire_product_line.",
 "analogues": an("shopping_admin", 90, 91, 122, 126),
},
{
 "slug": "named_product_variant_wizard",
 "skills": ["R9", "A6"],
 "chain": "open the configurable product named in the instruction, then add the stated option value to every one of its colour or size variants",
 "entities": "draw from the 147 configurables, not the census's five: Diana Tights WP06 (parent 1854), Karmen, Erika, Portia, Sylvia, Mimi, Fiona, Bardot, Cora Parachute Pant, Aeon Capri, Chloe Compete Tank WT06 (1764), Phoebe WH07 (1130), Sahara WP05 (1847), Hollister MH05 (126). Attribute 144 (Size) carries 20 option values including 30 (id 173) and 31 (id 174).",
 "writeback": "newProducts[] + productOverrides[<parent>].{configurable_attributes, configurable_children}",
 "notes": E + " " + WIZARD + " " + NAMES + " Official 140's string is exactly 'Add new size 30 and 31 to all color variants of Diana Tights' - do NOT reproduce it; change the product and the option value, and remember CORRECTIONS #82 means that particular pair needs no attribute round-trip at all. R9->A6 is a heavy batch-5 pair (5 uses) and is KEPT once here, because official 136-140 is 14 templates / 8% of instances and is literally 'named product -> variant matrix': dropping it would misrepresent the site, and A6 exists on no other site in the batch. " + GATE + " Batch-5 adjacent: tights_size_matrix.",
 "analogues": an("shopping_admin", 140, 136, 137, 139),
},
{
 "slug": "window_order_address_fix",
 "skills": ["R2", "A11"],
 "chain": "find the order inside a stated date window, then correct its billing or shipping address to the one given",
 "entities": "order data spans 2022-01-08 to 2023-05-31 only. Orders with address-edit routes at /admin/sales/order/address/address_id/:id/: 299, 65, 301, 300, 125. Phone lookup anchor: +1 2058812302 -> John Smith / john.smith.xyz@gmail.com, entity_id 2, stored UNFORMATTED as 2058812302.",
 "writeback": "orderAddressOverrides[<address_id>] (patchOrderAddress, AppContext.jsx:209)",
 "notes": E + " MOCK BUG, CORRECTIONS #91 - this is the lane-defining hazard: selectors.js getOrderGridRows reads the orderOverrides patch and SHORT-CIRCUITS (`if (!patch) return row`) before orderAddressOverrides is ever consulted, so an edited address reaches the grid's Billing/Shipping Address columns ONLY when the same order also carries an unrelated orderOverrides patch. Edit an address alone and the order view shows the new value while the grid still shows the old one. Never grade an address through a grid column, and do not author a task whose correct END STATE is a two-screen contradiction - that is the mutation-side mirror of the injection plausibility rule, and batch 5 dropped a candidate ('copy shipping onto billing within one order') over it rather than ship it. Under TASK4 S2 this is a fact to design around; hub/ is read-only. There are NO relative-date presets in Family A and the legacy toolbar's today-minus-one-month default yields empty rows in 2026, so the window must be stated as absolute M/D/YYYY dates the agent types. " + YEARTRAP + " " + GRIDS + " CORRECTIONS #96: a full credit-memo refund produces a NEGATIVE report contribution (orderReportAmount subtracts the refund and the order discount separately, so fully-refunded order 000000028 reads -$50.40) - keep any injected refund partial. Batch-5 adjacent: phone_lookup_address_fix (R9->R7->A11) - batch 6 swaps the retrieval to a date window so the pair is new.",
 "analogues": an("shopping_admin", 127, 128, 129, 131),
},
{
 "slug": "customer_join_order_comment",
 "skills": ["R7", "A8"],
 "chain": "join a customer to their orders through a report or a grid, then leave a comment on the order the instruction names",
 "entities": "the ONE clean all-history join: Samantha Jones / coolcat321@hotmail.com has 9 cancellations, margin 2 over a two-way tie at 7 (Julia Williams, Alexander Thomas); her most recent cancelled order is 000000088 (entity_id 88, 2023-04-14 03:05:30, $168.80) and all nine of her cancelled timestamps are distinct. Its SKUs are WSH09-29-White, WSH09-28-Green, MSH11-34-Blue, WP09-29-Purple - but items[] has EIGHT entries because each configurable line is duplicated by a price 0.00 child row while total_item_count is 4, so any reward must fix a convention. Single-interval superlatives that ARE renderable: April 2023 order count leader Grace Nguyen 4, margin 2; 2023 total leader Sarah Miller $846.80, margin $156.00. orders.customer_id <-> customers.entity_id and customer_email <-> email are both fully consistent (36/36, 0 orphans); 34 of 70 customers have no orders.",
 "writeback": "orderComments[<order_id>][] via #history_comment + Submit Comment (OrderView.jsx:449-496, handler :395-429)",
 "notes": E + " 'Customer who completed the most orders' is BROKEN under the literal all-status reading - a THREE-WAY tie at 15 (Grace Nguyen, Sarah Miller, Samantha Jones, margin 0). " + YEARTRAP + " CORRECTIONS #95: the Order Count and Order Total reports render the customer NAME, not the email, and TWO seeded customers are named 'Jane Smith' (janesmith456@yahoo.com vs janesmith@gmail.com) - never key on the name for an email-valued task, and the census's 'safe' 2022 top-customer line is arithmetically right and unusable for that reason. CORRECTIONS #105: the review-to-customer join is COMPLETELY DEAD on the seed - five of the six 'disappointed' reviews have customer_id null and the sixth points at Emma Lopez, who has zero orders; the nickname route fails too (Wilbur / Ricky / Lasandra / Aiko match no customer, 'Hannah Lim' has no orders, 'Emma' is ambiguous). Reviving it needs BOTH customer_id (what CustomerEdit.jsx:154-156 and the By Customers report filter on) and nickname = customers.name (what ReviewEdit renders as 'Posted By', since it never renders the customer at all) - injecting one alone reproduces the writable-key-nobody-reads pattern. Reviews By Customers renders a SINGLE row until customer_id is injected: exactly 1 of 351 reviews has a non-null customer_id. An empty comment with unchanged status is rejected (OrderView.jsx:401-404), and CORRECTIONS #106 means #history_status has zero options on a pending order. Customer NOTES do not exist (CustomerEdit.jsx:409-530 has no notes field; the nearest free text is customer[taxvat]) - do not frame anything as 'add a note to the customer's record'. " + REPORTS + " Batch-5 adjacent: unhappy_customer_followup and reward_top_customer.",
 "analogues": an("shopping_admin", 112, 113, 114, 116),
},
]

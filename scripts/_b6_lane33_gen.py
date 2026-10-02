#!/usr/bin/env python3
"""Batch-6 lane 33 generator -- shopping, skills R5 -> A2.

Chain: browse a category and apply the Shop By > Price facet cell that holds
exactly one product, then submit that product's review form.

Every target is DERIVED: the instruction names the category and the price band,
never the product. All ten cells were measured against
hub/websites/webarena_shopping_mock/src/data with
scripts/_b6_lane33_analyze.py + _b6_lane33_check2.py:

  * the captured plain-category listing advertises the band with count == 1
    (priceFacets, catalog.js:1271-1283, returns the capture verbatim);
  * the derived seed pool for the same band holds exactly 1 listable product
    (resolveListing, catalog.js:1142-1243);
  * no exact capture exists for the facet URL, so items == pool.slice(0, 12)
    -- the single product renders on page 1 (no CORRECTIONS #58 gap exposure).

Writes bundles to output/tasks/shopping/<task_id>/ and the batch artifacts to
output/tasks/shopping/_batches/category_product_review_form/.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE = os.path.join(ROOT, "output", "tasks", "shopping")
BATCH = os.path.join(SITE, "_batches", "category_product_review_form")
APP = "webarena_shopping_mock"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

RATE_ANALOGUES = {
    5: 'Rate my recently purchased floor lamp with 5 stars using my nickname Emma Lopez, with the summary "Good purchase" and review "I like it"',
    4: 'Rate my recently purchased Jiffy Mix with 4 stars using my nickname ShoppingEmma, with the summary "Good purchase" and review "I like it"',
    3: 'Rate my recently purchased PS3 accessory with 3 stars using my nickname GamingEmma, with the summary "Ok I guess" and review "Does the job"',
    2: 'Rate my recently purchased Mini Wireless Bluetooth Speaker with 2 stars using my nickname SimpleEmma, with the summary "Very bad" and review "I hated it"',
    1: 'Rate my recently purchased Foundation For Mattress With Frame Set with 1 stars using my nickname ShoppingEmma, with the summary "Very bad" and review "I hated it"',
}
FACET_ANALOGUE_RANGE = 'Open the "makeup remover" category page filtered to price from $20.00 to $29.99'
FACET_ANALOGUE_ABOVE = 'Open the "children dental care" category page filtered to price to $200 and above'


TASKS = [
    {
        "n": 1,
        "slug": "xbox_controller_band",
        "style": "terse",
        "category": "Xbox One",
        "breadcrumb": "Video Games > Xbox One",
        "cat_path": "/video-games/xbox-one.html",
        "facet_label": "$200.00 - $299.99",
        "facet_query": "price=200-300",
        "product_id": 101604,
        "product_name": "SCUF Instinct Pro Steel Gray Custom Wireless Performance Controller for Xbox Series X|S, Xbox One, PC, and Mobile",
        "product_price": "229.99",
        "runner_up": "the next-cheapest Xbox One row is $160.00 (id 37670) and the next-dearest is $403.99 (id 18722), so the band [200, 300) is a strict one-product cell",
        "rating": 4,
        "nickname": "ShoppingEmma",
        "summary": "Worth the upgrade",
        "detail": "Paddles and triggers still feel great after a week of play",
        "intent": 'Exactly one Xbox One product is priced between $200.00 and $299.99. Review it with 4 stars, nickname ShoppingEmma, summary "Worth the upgrade", review "Paddles and triggers still feel great after a week of play".',
        "derived_from": "facet_cell_single_result_smartwatch_over_250_004",
    },
    {
        "n": 2,
        "slug": "nordic_mirror_band",
        "style": "terse",
        "category": "Mirrors",
        "breadcrumb": "Beauty & Personal Care > Tools & Accessories > Mirrors",
        "cat_path": "/beauty-personal-care/tools-accessories/mirrors.html",
        "facet_label": "$500.00 - $599.99",
        "facet_query": "price=500-600",
        "product_id": 2631,
        "product_name": "WLJDT LICHAO Nordic Concise Bathroom Mirror Round Makeup Mirror Bathroom Wall Hanging Mirror",
        "product_price": "595.91",
        "runner_up": "next below the band is $493.99 (id 50085); the only dearer mirror is $621.99 (id 49878), which sits in the separate \"$600.00 and above\" cell",
        "rating": 1,
        "nickname": "EmmaL",
        "summary": "Not worth it",
        "detail": "Arrived scratched and far too dim for the price",
        "intent": 'One mirror in the Mirrors category falls in the $500.00 - $599.99 price band. Give it 1 star, nickname EmmaL, summary "Not worth it", review "Arrived scratched and far too dim for the price".',
        "derived_from": None,
    },
    {
        "n": 3,
        "slug": "flagship_projector_top_band",
        "style": "terse",
        "category": "Video Projectors",
        "breadcrumb": "Electronics > Video Projectors",
        "cat_path": "/electronics/video-projectors.html",
        "facet_label": "$20,000.00 and above",
        "facet_query": "price=20000-30000",
        "product_id": 41407,
        "product_name": "Sony VPL-VW1000ES 4K Home Theater ES Projector + TUFF Mount C7016 Durable Ceiling TV Mount for 13-Inch to 37-Inch Displays + 2 HDMI Cables",
        "product_price": "21999.99",
        "runner_up": "the next projector down is $17,774.32 (id 40872) and nothing in the category costs more, so the top band holds exactly one row with a $4,225.67 gap",
        "rating": 5,
        "nickname": "HomeTheaterEmma",
        "summary": "Reference class",
        "detail": "Nothing else in the store comes close to this picture",
        "intent": 'Only one video projector here costs $20,000.00 or more. Rate it 5 stars as HomeTheaterEmma, with the summary "Reference class" and the review "Nothing else in the store comes close to this picture".',
        "derived_from": None,
    },
    {
        "n": 4,
        "slug": "gruyere_wheel_top_band",
        "style": "terse",
        "category": "Cheese",
        "breadcrumb": "Grocery & Gourmet Food > Dairy, Cheese & Eggs > Cheese",
        "cat_path": "/grocery-gourmet-food/dairy-cheese-eggs/cheese.html",
        "facet_label": "$1,000.00 and above",
        "facet_query": "price=1000-2000",
        "product_id": 90807,
        "product_name": "Gruyere Cheese - Cave-Aged 12 Months - 70 lb wheel",
        "product_price": "1967.35",
        "runner_up": "the next-dearest cheese is $657.55 (id 21570) and nothing exceeds this row, a $1,309.80 margin",
        "rating": 5,
        "nickname": "Emma Lopez",
        "summary": "Worth every penny",
        "detail": "The whole wheel arrived in perfect condition",
        "intent": 'A single item in the Cheese category is priced $1,000.00 or above. Post a 5-star review on it as Emma Lopez, summary "Worth every penny", review "The whole wheel arrived in perfect condition".',
        "derived_from": "facet_cell_single_result_deli_over_100_dearer_007",
    },
    {
        "n": 5,
        "slug": "pelican_case_top_band",
        "style": "terse",
        "category": "Sports",
        "breadcrumb": "Sports & Outdoors > Sports",
        "cat_path": "/sports-outdoors/sports.html",
        "facet_label": "$300.00 and above",
        "facet_query": "price=300-400",
        "product_id": 12664,
        "product_name": "Waterproof Case Pelican Storm iM2950 Case With Foam (Black)",
        "product_price": "315.95",
        "runner_up": "the next-dearest Sports row is $169.95 (ids 61187 and 60310) and nothing costs more, a $146.00 margin",
        "rating": 3,
        "nickname": "GearEmma",
        "summary": "Heavy but solid",
        "detail": "Watertight, though I badly underestimated the weight",
        "intent": 'In the Sports category exactly one product costs $300.00 or more. Review it with 3 stars, nickname GearEmma, summary "Heavy but solid", review "Watertight, though I badly underestimated the weight".',
        "derived_from": None,
    },
    {
        "n": 6,
        "slug": "health_care_top_band",
        "style": "explicit",
        "category": "Health Care",
        "breadcrumb": "Health & Household > Health Care",
        "cat_path": "/health-household/health-care.html",
        "facet_label": "$100.00 and above",
        "facet_query": "price=100-200",
        "product_id": 31299,
        "product_name": "Orthofeet Proven Plantar Fasciitis and Foot Relief. Extended Widths. Bunions Orthopedic Walking Shoes Diabetic Arch Support Women's Sneakers, Verve",
        "product_price": "134.95",
        "runner_up": "the next-dearest Health Care row is $72.99 (id 34435) and nothing costs more, a $61.96 margin",
        "rating": 5,
        "nickname": "ShoppingEmma",
        "summary": "Finally some relief",
        "detail": "Six weeks in and my heel pain is gone",
        "intent": 'I want to leave feedback on the one expensive thing in Health & Household > Health Care. Open that category, use the Shop By > Price block to filter to "$100.00 and above" -- a single product is listed. Open it, go to its Reviews tab, and submit a 5-star review with the nickname ShoppingEmma, the summary "Finally some relief" and the review text "Six weeks in and my heel pain is gone".',
        "derived_from": None,
    },
    {
        "n": 7,
        "slug": "heated_jacket_top_band",
        "style": "terse",
        "category": "Exercise & Fitness",
        "breadcrumb": "Sports & Outdoors > Exercise & Fitness",
        "cat_path": "/sports-outdoors/exercise-fitness.html",
        "facet_label": "$100.00 and above",
        "facet_query": "price=100-200",
        "product_id": 13058,
        "product_name": "Venture Heat Men's Heated Knit Fleece Jacket Vest with Battery Pack - 11 Watt High Power Electric Sweater (Vest or Jacket)",
        "product_price": "129.00",
        "runner_up": "the next-dearest Exercise & Fitness row is $79.99 (id 83442) and nothing costs more, a $49.01 margin",
        "rating": 2,
        "nickname": "ColdEmma",
        "summary": "Battery quits early",
        "detail": "Warm for about an hour, then nothing",
        "intent": 'Exercise & Fitness lists just one product at $100.00 or more. Rate it 2 stars, nickname ColdEmma, summary "Battery quits early", review "Warm for about an hour, then nothing".',
        "derived_from": None,
    },
    {
        "n": 8,
        "slug": "artificial_flowers_band",
        "style": "terse",
        "category": "Artificial Plants & Flowers",
        "breadcrumb": "Home & Kitchen > Home Decor Products > Artificial Plants & Flowers",
        "cat_path": "/home-kitchen/home-decor-products/artificial-plants-flowers.html",
        "facet_label": "$400.00 - $499.99",
        "facet_query": "price=400-500",
        "product_id": 72859,
        "product_name": "JNWEIYU Artificial Flowers Fake Silk Flower Bouquets with Vase Potted Plants",
        "product_price": "451.16",
        "runner_up": "next below the band is $379.99 (id 72381, its own \"$300.00 - $399.99\" cell) and next above is $598.89 (id 99275)",
        "rating": 4,
        "nickname": "EmmaDecorates",
        "summary": "Looks real from the sofa",
        "detail": "Pricey, but the vase alone is lovely",
        "intent": 'Exactly one item in the Artificial Plants & Flowers category sits in the $400.00 - $499.99 band. Review it: 4 stars, nickname EmmaDecorates, summary "Looks real from the sofa", review "Pricey, but the vase alone is lovely".',
        "derived_from": None,
    },
    {
        "n": 9,
        "slug": "canvas_print_top_band",
        "style": "terse",
        "category": "Posters & Prints",
        "breadcrumb": "Home & Kitchen > Wall Art > Posters & Prints",
        "cat_path": "/home-kitchen/wall-art/posters-prints.html",
        "facet_label": "$300.00 and above",
        "facet_query": "price=300-400",
        "product_id": 67979,
        "product_name": "Fine Art Canvas Frozen Shores Canvas Print Artwork by Marion Griese, 45\"W x 60\"H Vertical Gallery Wrapped Large Wall Decor",
        "product_price": "399.99",
        "runner_up": "the next-dearest print is $199.99 (id 33901) and nothing costs more, a $200.00 margin",
        "rating": 3,
        "nickname": "WallArtEmma",
        "summary": "Big and bold",
        "detail": "Great colours, but the canvas wrap is uneven",
        "intent": 'One item in Posters & Prints is priced $300.00 or more. Give it 3 stars as WallArtEmma, summary "Big and bold", review "Great colours, but the canvas wrap is uneven".',
        "derived_from": None,
    },
    {
        "n": 10,
        "slug": "toothbrush_bundle_top_band",
        "style": "explicit",
        "category": "Toothbrushes & Accessories",
        "breadcrumb": "Beauty & Personal Care > Oral Care > Toothbrushes & Accessories",
        "cat_path": "/beauty-personal-care/oral-care/toothbrushes-accessories.html",
        "facet_label": "$200.00 and above",
        "facet_query": "price=200-300",
        "product_id": 7778,
        "product_name": "Triple Bristle DUO & 2 Kids Sonic Toothbrushes + Refills Bundle | Rechargeable 31,000 VPM Tooth Brush | Patented 3 Brush Head Design | Angled Bristles Clean Each Tooth | Dentist Approved",
        "product_price": "231.24",
        "runner_up": "the next-dearest toothbrush row is $159.00 (id 92758) and nothing costs more, a $72.24 margin",
        "rating": 1,
        "nickname": "SimpleEmma",
        "summary": "Overpriced bundle",
        "detail": "Two of the brush heads stopped charging within a month",
        "intent": 'Beauty & Personal Care > Oral Care > Toothbrushes & Accessories has exactly one product in the "$200.00 and above" price band of the Shop By > Price block. Open that product\'s page, switch to its Reviews tab, and submit a one-star review using the nickname SimpleEmma, the summary "Overpriced bundle" and the review body "Two of the brush heads stopped charging within a month".',
        "derived_from": None,
    },
]

COMPONENTS = """COMPONENT_WEIGHTS = {
    "single_review_on_the_derived_product": 0.4,
    "star_rating_recorded": 0.2,
    "nickname_and_summary_recorded": 0.2,
    "review_body_recorded": 0.2,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def _int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if float(value).is_integer() else None
    if isinstance(value, str):
        text = value.strip()
        try:
            number = float(text)
        except ValueError:
            return None
        return int(number) if float(number).is_integer() else None
    return None


def _norm(value):
    if not isinstance(value, str):
        return ""
    text = re.sub(r"\\s+", " ", value).strip().lower()
    return text.strip(" .!,;:")


def _reviews(state):
    rows = state.get("myReviews")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _target(state):
    rows = _reviews(state)
    if len(rows) != 1:
        return None
    row = rows[0]
    if _int(row.get("productId")) != PRODUCT_ID:
        return None
    return row


def _checks(state):
    row = _target(state)
    if row is None:
        return dict((name, False) for name in COMPONENT_WEIGHTS)
    return {
        "single_review_on_the_derived_product": True,
        "star_rating_recorded": _int(row.get("rating")) == RATING,
        "nickname_and_summary_recorded": (
            _norm(row.get("nickname")) == _norm(NICKNAME)
            and _norm(row.get("title")) == _norm(SUMMARY)
        ),
        "review_body_recorded": _norm(row.get("detail")) == _norm(DETAIL),
    }
"""


def reward_py(t, criteria):
    header = '"""Deterministic reward for %s.\n\nSuccess criteria:\n%s\n\nOnly user-visible persisted state is inspected, and only `current_state`. The\nscored surface is `myReviews`, whose sole writer is `submitReview`\n(AppContext.jsx:427-447); it boots empty from `createInitialData()`\n(utils/dataManager.js:144), so an untouched episode and an empty state both\nscore exactly 0.0 on every component.\n\nGround truth is fixed by the frozen catalog seed of webarena_shopping_mock\nin ./hub/: the %s price cell of %s holds exactly one listable\nproduct, id %d.\n"""\n' % (
        t["task_id"],
        "\n".join("  * " + c for c in criteria),
        t["facet_label"],
        t["breadcrumb"],
        t["product_id"],
    )
    return (
        header
        + "\nimport re\n\n"
        + "PRODUCT_ID = %d\nRATING = %d\nNICKNAME = %r\nSUMMARY = %r\nDETAIL = %r\n\n"
        % (t["product_id"], t["rating"], t["nickname"], t["summary"], t["detail"])
        + COMPONENTS
        + '''

def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}


def evaluate(evidence):
    state = _state(evidence)
    checks = _checks(state)
    components = [
        {
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {"satisfied": bool(checks.get(name))},
        }
        for name in COMPONENT_WEIGHTS
    ]
    return {
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }
'''
    )


def nemo_reward_py(t):
    header = '"""NeMo-Gym reward program for %s.\n\nImplements exactly the rubric of reward.py, reading `current_state` from\nGET /go?sid=... instead of a frozen evidence bundle, and printing\nREWARD: <float> on every output path including the error paths.\n\nSelf-contained: standard library plus requests, which is present in\ncuagym/requirements.txt.\n"""\n' % t["task_id"]
    return (
        header
        + "\nimport re\nimport sys\n\nimport requests\n\n"
        + 'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % PLACEHOLDER
        + "PRODUCT_ID = %d\nRATING = %d\nNICKNAME = %r\nSUMMARY = %r\nDETAIL = %r\n\n"
        % (t["product_id"], t["rating"], t["nickname"], t["summary"], t["detail"])
        + COMPONENTS
        + '''

def score_state(state):
    checks = _checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
    return round(total, 6)


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        payload = response.json()
        state = payload.get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    try:
        value = score_state(state)
    except Exception as exc:  # noqa: BLE001 - a scoring bug must still score
        print("reward scoring failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    print("REWARD: %s" % value)


main()
'''
    )


REPLAY = '''"""Golden replay draft - %(task_id)s.

Click-only from "/": every navigation follows a rendered link, button or form
control. The only page.goto is the initial landing.

Intent: %(intent)s

Route: / -> nav band %(breadcrumb)s -> Shop By > Price > "%(facet_label)s"
(href %(cat_path)s?%(facet_query)s, one tile) -> that tile -> Reviews tab ->
star label -> nickname / summary / review -> Submit Review.

Target: product %(product_id)d, %(product_name)s ($%(product_price)s).

Three mock facts this driver respects:
  * the price facet options come from the captured plain-category listing
    verbatim (catalog.js:1271-1283), so the "%(facet_label)s" link exists and
    carries ?%(facet_query)s;
  * the star radios are 1x1 and opacity:0 (globals.css:719); the visible target
    is the <label>. Click label[for="Rating_N"]. DOM order is ASCENDING
    (ProductPage.jsx:284-293), so Rating_%(rating)d really is %(rating)d star(s);
  * the orange fill is driven by data-rating on div.review-control-vote
    (ProductPage.jsx:280-282), not by input:checked. Assert on that attribute.
"""


def _open_category(page):
    """Nav band renders the whole descendant tree in the DOM (Header.jsx:302-345),
    CSS-hover only, so the nested link is clickable without hovering."""
    page.locator('nav.navigation a[href="%(cat_path)s"]').first.click()
    page.wait_for_load_state("networkidle")


def _apply_price_facet(page):
    block = page.locator("#narrow-by-list")
    link = block.locator("a", has_text="%(facet_label)s").first
    link.click()
    page.wait_for_load_state("networkidle")
    assert "%(facet_query)s" in page.url
    tiles = page.locator("li.product-item a.product-item-link")
    assert tiles.count() == 1, "the %(facet_label)s cell must hold exactly one product"


def _open_pdp(page):
    page.locator("li.product-item a.product-item-link").first.click()
    page.wait_for_load_state("networkidle")


def _write_review(page):
    page.locator("#tab-label-reviews-title").click()
    page.locator('label[for="Rating_%(rating)d"]').click()
    assert page.locator("div.review-control-vote").first.get_attribute(
        "data-rating") == "%(rating)d"
    page.locator("#nickname_field").fill(%(nickname)r)
    page.locator("#summary_field").fill(%(summary)r)
    page.locator("#review_field").fill(%(detail)r)
    page.get_by_role("button", name="Submit Review", exact=True).click()
    page.wait_for_load_state("networkidle")


def run(page, base_url):
    page.goto(base_url + "/")
    _open_category(page)
    _apply_price_facet(page)
    _open_pdp(page)
    _write_review(page)
'''


def build(t):
    t = dict(t)
    t["task_id"] = "category_product_review_form_%s_%03d" % (t["slug"], t["n"])
    bundle = os.path.join(SITE, t["task_id"])
    os.makedirs(bundle, exist_ok=True)

    criteria = [
        "state.myReviews holds exactly one entry and its productId is %d (%s), the only product in the %s price band of %s."
        % (t["product_id"], t["product_name"], t["facet_label"], t["breadcrumb"]),
        "That entry's rating is exactly %d." % t["rating"],
        "That entry's nickname is %r and its title is %r." % (t["nickname"], t["summary"]),
        "That entry's detail is %r." % t["detail"],
    ]

    with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
        json.dump(
            {
                "task_id": t["task_id"],
                "task_instruction": t["intent"],
                "app_dir": APP,
                "start_path": "/",
                "difficulty": "medium",
                "success_criteria": criteria,
            },
            fh,
            indent=2,
        )
        fh.write("\n")

    analogues = [
        FACET_ANALOGUE_RANGE if "-" in t["facet_label"] else FACET_ANALOGUE_ABOVE,
        RATE_ANALOGUES[t["rating"]],
    ]

    manifest = {
        "schema_version": 2,
        "task_id": t["task_id"],
        "instruction": t["intent"],
        "apps": [
            {
                "name": APP,
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
                "start_path": "/",
                "initial_state": None,
                "golden_state": None,
            }
        ],
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "webarena",
        "metadata": {
            "style": t["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R5", "A2"],
            "skill_chain": "faceted category navigation -- %s, Shop By > Price cell \"%s\", which holds exactly one product -> submit that product's multi-field review form (rating, nickname, summary, body)"
            % (t["breadcrumb"], t["facet_label"]),
            "derived_from": t["derived_from"],
            "official_analogues": analogues,
            "injected_preconditions": [],
            "topic": "category_product_review_form -- derive a product from a single-result price facet, then write its review",
            "inspiration_ids": ["webarena-271", "webarena-272", "webarena-585", "webarena-589"],
            "authoring_notes": [
                "Derived target: the instruction never names the product. The %s cell of %s resolves to exactly one listable product, id %d ($%s)."
                % (t["facet_label"], t["breadcrumb"], t["product_id"], t["product_price"]),
                "Tie margin: %s." % t["runner_up"],
                "Rendering: no exact capture exists for %s?%s, so resolveListing (catalog.js:1142-1243) falls through to pool.slice(0, 12) and the single seeded product renders on page 1; totalCount comes from the captured facet count (also 1), so the toolbar and the grid agree. This is the browsing mode the instruction implies, so CORRECTIONS #58's captured-page-1/derived-page-2 gap is not exposed."
                % (t["cat_path"], t["facet_query"]),
                "Facet availability: priceFacets (catalog.js:1271-1283) returns the captured plain-category Price block verbatim, so the \"%s\" option renders with its source count and href."
                % t["facet_label"],
                "Click reachability from '/': every ancestor of the category carries isActive and includeInMenu, and NavBand (Header.jsx:302-345) renders the whole descendant tree in the DOM, so the category link is clickable without a typed URL.",
                "Writeback: submitReview (AppContext.jsx:427-447) appends {reviewId, productId, title, detail, nickname, customerId, rating, createdAt} to myReviews and bumps nextReviewId from its seeded 400000 (dataManager.js:149). The rubric never reads nextReviewId or any generated id.",
                "Rating radios are Rating_1..Rating_5 with values 16..20 (ProductPage.jsx:262-285) but the stored rating is the plain 1-5 Number handed to setRating; the reward asserts %d." % t["rating"],
                "The rubric asserts the exact resulting collection -- myReviews is exactly one entry, on the derived product -- so nothing is paid for restraint and a scattershot run that reviews several candidates scores 0.0.",
                "An agent that skips the facet retrieval cannot name the product: no component pays unless myReviews' single row carries productId %d." % t["product_id"],
                "No initial_setup: myReviews boots empty from createInitialData(), which is already the hardest starting point for this rubric, and any injected review would either pre-satisfy or force a preservation component.",
                "Grounded in webarena_shopping_mock @ hub/websites/webarena_shopping_mock; nothing under hub/ was modified.",
                "Both reward programs read the live session document only, never initial_state or state_diff.",
            ],
        },
    }
    with open(os.path.join(bundle, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(bundle, "reward.py"), "w") as fh:
        fh.write(reward_py(t, criteria))
    nemo = nemo_reward_py(t)
    with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
        fh.write(nemo)

    row = {
        "task_payload": {
            "task_id": t["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": t["intent"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": t["task_id"],
                "app_dir": APP,
                "initial_setup": None,
                "eval_reward_code": nemo,
            },
        }
    }
    with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2)
        fh.write("\n")

    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    with open(os.path.join(BATCH, "replays", t["task_id"] + ".py"), "w") as fh:
        fh.write(REPLAY % t)

    return t, row


def main():
    os.makedirs(BATCH, exist_ok=True)
    built = []
    rows = []
    for spec in TASKS:
        t, row = build(spec)
        built.append(t)
        rows.append(row)

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(
            {
                "schema_version": 2,
                "tasks": [
                    {"task_id": t["task_id"], "path": "%s/task.json" % t["task_id"]}
                    for t in built
                ],
            },
            fh,
            indent=2,
        )
        fh.write("\n")

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    for t in built:
        words = len(t["intent"].split())
        print("%-58s %-8s %2d stars  pid=%-6d %2d words" % (t["task_id"], t["style"], t["rating"], t["product_id"], words))


if __name__ == "__main__":
    main()

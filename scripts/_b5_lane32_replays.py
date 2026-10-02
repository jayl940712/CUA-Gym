#!/usr/bin/env python3
"""Emit golden-replay DRAFTS for batch-5 lane 32 (shopping/category_cheapest_to_cart).

These are drafts for the golden-browser agent. They are click-only from "/" and
contain no page.goto() after the initial landing.
"""
import os

OUT = "/home/ubuntu/CUA-Gym/output/tasks/shopping/_batches/category_cheapest_to_cart/replays"

HEADER = '''"""Golden replay DRAFT for {task_id}.

Click-only from start_path "/". No page.goto() after the initial landing, no
constructed URLs. Navigation is through the NavBand category tree
(Header.jsx:316-345 renders the whole 301-category descendant tree in the DOM;
the submenus are CSS-hover only, so the hover below is belt-and-braces).

Cheapest is reached with Sort By -> Price on a category page. The page's
natural direction is ascending (catalog.js:1126 defaultListDir), so no
direction toggle is needed and the replay must never assert on the direction
control's own label - it advertises the direction it will switch TO
(Toolbar.jsx:79-82).
"""


def open_category(page, trail):
    """trail: list of NavBand labels, top level first."""
    top = page.locator("nav.navigation li.level-top").filter(
        has=page.locator('a.level-top span:text-is("%s")' % trail[0])
    ).first
    top.hover()
    if len(trail) == 1:
        top.locator('a.level-top').first.click()
    else:
        for label in trail[1:-1]:
            top.locator('a:has(span:text-is("%s"))' % label).first.hover()
        top.locator('a:has(span:text-is("%s"))' % trail[-1]).first.click()
    page.wait_for_selector("#sorter")


def sort_by_price_ascending(page):
    page.select_option("#sorter", "price")
    page.wait_for_selector(".product-item")


def first_tile(page):
    return page.locator("li.product-item").first


def add_first_tile_via_pdp(page):
    """Route through the product page, which is required whenever the product
    carries a required custom option (ProductGrid.jsx:63-66 diverts the tile
    button to the PDP instead of adding)."""
    first_tile(page).locator("a.product-item-link").first.click()
    page.wait_for_selector("#product-addtocart-button")
    for group in page.locator("#product-options-wrapper .field.required").all():
        radio = group.locator("input[type=radio]").first
        if radio.count():
            radio.check(force=True)
    page.click("#product-addtocart-button")
    page.wait_for_selector(".message-success, div.message.success")


def open_cart(page):
    page.click('a.action.showcart, a[href="/checkout/cart/"]')
    page.wait_for_selector("#shopping-cart-table, .cart.item")


def run(page, base_url):
    page.goto(base_url + "/")
'''

TASKS = {
    "category_cheapest_to_cart_deli_counter_bargain_001": {
        "body": '''    open_category(page, ["Grocery & Gourmet Food", "Deli & Prepared Foods", "Deli Meats & Cheeses"])
    sort_by_price_ascending(page)
    # first tile is product 47533 "Coppa Capicola- SLICED 3 packages" at $6.51
    add_first_tile_via_pdp(page)
    # end state: cart holds seeded 554/555/556 plus one line for 47533
''',
    },
    "category_cheapest_to_cart_table_linens_bargain_002": {
        "body": '''    open_category(page, ["Home & Kitchen", "Kitchen & Dining", "Kitchen & Table Linens"])
    sort_by_price_ascending(page)
    # first tile is product 14578, the KOECPS clear table protector at $4.02
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_legacy_nintendo_003": {
        "body": '''    open_category(page, ["Video Games", "Legacy Systems", "Nintendo Systems"])
    sort_by_price_ascending(page)
    # first tile is product 39600, the Animal Crossing Amiibo card at $0.89
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_mp3_adapter_004": {
        "body": '''    open_category(page, ["Electronics", "Portable Audio & Video", "MP3 & MP4 Player Accessories"])
    sort_by_price_ascending(page)
    # first tile is product 19698, the hudiemm0B cassette adapter at $0.99
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_office_and_balcony_005": {
        "body": '''    open_category(page, ["Office Products", "Office Furniture & Lighting", "Chairs & Sofas"])
    sort_by_price_ascending(page)
    # first tile is product 32684, the KaiMeng ribbed office chair at $25.21
    add_first_tile_via_pdp(page)

    open_category(page, ["Patio, Lawn & Garden", "Patio Furniture & Accessories"])
    sort_by_price_ascending(page)
    # first tile is product 34421, the synthetic rattan weaving material at $17.99
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_phone_and_case_006": {
        "body": '''    open_category(page, ["Cell Phones & Accessories", "Cell Phones"])
    sort_by_price_ascending(page)
    # first tile is product 43211, the TracFone My Flip 2 at $1.49
    add_first_tile_via_pdp(page)

    open_category(page, ["Cell Phones & Accessories", "Cases, Holsters & Sleeves", "Flip Cases"])
    sort_by_price_ascending(page)
    # first tile is product 76561, the Asuwish iPhone Xs wallet case at $6.99
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_heater_swap_007": {
        "body": '''    # 1. the injected fourth line (product 87880, $3.02 Comfort Zone heater)
    #    has to go. Remove it from the cart page first.
    open_cart(page)
    row = page.locator("tbody.cart.item").filter(has_text="Comfort Zone CZ2018").first
    row.locator("a.action-delete, a.action.action-delete").first.click()
    page.wait_for_timeout(500)

    # 2. cheapest product in Heating, Cooling & Air Quality is 13510 at $1.07
    open_category(page, ["Home & Kitchen", "Heating, Cooling & Air Quality"])
    sort_by_price_ascending(page)
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_kids_blanket_swap_008": {
        "body": '''    # 1. drop the injected Pink Minnie Mouse blanket (product 72918, $14.70)
    open_cart(page)
    row = page.locator("tbody.cart.item").filter(has_text="Pink Minnie Mouse Fleece Blanket").first
    row.locator("a.action-delete, a.action.action-delete").first.click()
    page.wait_for_timeout(500)

    # 2. cheapest Kids' Bedding product is 67025, the Lion King throw at $7.59
    open_category(page, ["Home & Kitchen", "Bedding", "Kids' Bedding"])
    sort_by_price_ascending(page)
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_video_game_sweep_009": {
        "body": '''    open_category(page, ["Video Games", "PC", "Virtual Reality"])
    sort_by_price_ascending(page)
    # product 43290, Nurtery VR carrying case, $2.39
    add_first_tile_via_pdp(page)

    open_category(page, ["Video Games", "Legacy Systems", "Nintendo Systems"])
    sort_by_price_ascending(page)
    # product 39600, Animal Crossing Amiibo card, $0.89
    add_first_tile_via_pdp(page)

    open_category(page, ["Video Games", "Nintendo Switch"])
    sort_by_price_ascending(page)
    # product 77531, Nintendo Switch OLED Model, $3.66 - REQUIRED Color option,
    # so the tile button would only navigate; add_first_tile_via_pdp checks the
    # first radio and submits from the product page.
    add_first_tile_via_pdp(page)
''',
    },
    "category_cheapest_to_cart_budget_smartwatch_010": {
        "body": '''    open_category(page, ["Electronics", "Wearable Technology", "Smartwatches"])
    sort_by_price_ascending(page)
    # product 19328, Padgene bluetooth smartwatch, $22.49 - REQUIRED Color
    # option, so the add must happen on the product page.
    add_first_tile_via_pdp(page)
''',
    },
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for task_id, spec in TASKS.items():
        text = HEADER.format(task_id=task_id) + spec["body"]
        with open(os.path.join(OUT, task_id + ".py"), "w") as handle:
            handle.write(text)
    print("wrote %d replay drafts" % len(TASKS))


main()

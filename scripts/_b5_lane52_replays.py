#!/usr/bin/env python3
"""Golden replay DRAFTS for lane 52 (shopping_admin / retire_product_line).

Click-only from '/'. These are drafts for the golden-browser agent to verify
and tighten; nothing here has been executed.
"""
import os

REPLAYS = "/home/ubuntu/CUA-Gym/output/tasks/shopping_admin/_batches/retire_product_line/replays"
os.makedirs(REPLAYS, exist_ok=True)

HEADER = '''"""Golden replay draft for {tid}.

Click-only from start_path "/" (TASK4 S6): no page.goto after the landing
navigation, no constructed URLs. Reachability path:
{path}
"""

BASE = "http://localhost:8003"   # CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL
SID = "REPLACE_ME"


def open_products_grid(page):
    """Landing page -> left rail Catalog -> Products."""
    page.goto("%s/?sid=%s" % (BASE, SID))
    page.wait_for_selector("nav.admin__menu-wrap")
    page.click("li.level-0#menu-catalog a.menu-item, li.level-0 a.menu-item:has-text('Catalog')")
    page.click("div.submenu li.level-2 a:has-text('Products')")
    page.wait_for_selector("table.data-grid")


def keyword_search(page, keyword):
    box = page.locator("input.data-grid-search-control")
    box.fill(keyword)
    box.press("Enter")
    page.wait_for_selector("span.admin__data-grid-records-count")


def open_filters(page):
    page.click("button[data-action='grid-filter-expand']")


def apply_filters(page):
    page.click("button[data-action='grid-filter-apply']")
    page.wait_for_selector("span.admin__data-grid-records-count")


def select_all_matching(page):
    page.click("div.data-grid-multicheck-select button.action-select")
    page.click("div.data-grid-multicheck-select span.action-menu-item:has-text('Select All')")


def select_rows(page, ids):
    for pid in ids:
        page.check("#idscheck%d" % pid)


def mass_action(page, label):
    page.click("div.admin__data-grid-action-select-wrap button.action-select")
    page.click("div.admin__data-grid-action-select-wrap span.action-menu-item:has-text(\\"%s\\")" % label)
    page.wait_for_timeout(250)


def run(page):
'''


def write(tid, path, body):
    text = HEADER.format(tid=tid, path=path) + body + "\n"
    with open(os.path.join(REPLAYS, tid + ".py"), "w", encoding="utf-8") as fh:
        fh.write(text)


write(
    "retire_product_line_hollister_sweatshirt_takedown_001",
    "  / -> Catalog > Products -> keyword 'hollister' -> Options > Select All -> Actions > Change status / Disable",
    '''    open_products_grid(page)
    keyword_search(page, "hollister")
    # 16 records found: MH05 children 111-125 plus configurable parent 126.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")
    # Expect: "A total of 16 record(s) have been updated."
''')

write(
    "retire_product_line_teton_hoodie_relaunch_002",
    "  / -> Catalog > Products -> keyword 'teton' -> Filters > Status = Disabled -> Options > Select All -> Actions > Change status / Enable",
    '''    open_products_grid(page)
    keyword_search(page, "teton")
    open_filters(page)
    page.select_option("select[name='status']", "2")   # Disabled
    apply_filters(page)
    # 16 records found: the whole MH02 family, disabled by initial_setup.py.
    select_all_matching(page)
    mass_action(page, "Change status / Enable")
''')

write(
    "retire_product_line_ryker_crew_neck_only_003",
    "  / -> Catalog > Products -> keyword 'ryker' -> Filters > SKU contains 'MS09' -> Options > Select All -> Actions > Change status / Disable",
    '''    open_products_grid(page)
    keyword_search(page, "ryker")
    # 32 records found: MS09 Crew-neck (463-478) AND MS02 V-neck (559-574).
    open_filters(page)
    page.fill("input[name='sku']", "MS09")
    apply_filters(page)
    # 16 records found - the Crew-neck line only.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")
''')

write(
    "retire_product_line_helios_endurance_tank_pull_004",
    "  / -> Catalog > Products -> keyword 'helios' -> Filters > SKU contains 'MT04' -> Options > Select All -> Actions > Update attributes -> status + stock status -> Save",
    '''    open_products_grid(page)
    keyword_search(page, "helios")
    # 22 records found: MS05 EverCool Tee AND MT04 Endurance Tank.
    open_filters(page)
    page.fill("input[name='sku']", "MT04")
    apply_filters(page)
    # 6 records found - entity_ids 671-676.
    select_all_matching(page)
    mass_action(page, "Update attributes")
    page.wait_for_selector("#bulk-status")
    page.select_option("#bulk-status", "2")           # Disabled
    page.select_option("#bulk-stock-status", "0")     # Out of Stock
    page.click("form.admin__form-section button.action-primary")
''')

write(
    "retire_product_line_taurus_yellow_dye_recall_005",
    "  / -> Catalog > Products -> keyword 'taurus' -> Filters > Color = Yellow -> Options > Select All -> Actions > Change status / Disable",
    '''    open_products_grid(page)
    keyword_search(page, "taurus")
    open_filters(page)
    page.select_option("select[name='color']", "60")   # Yellow
    apply_filters(page)
    # 5 records found: 337, 340, 343, 346, 349.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")
''')

write(
    "retire_product_line_top_search_term_stockout_006",
    "  / -> Reports > Search Terms -> sort by Hits -> Catalog > Products -> keyword 'selene' -> Options > Select All -> Actions > Update attributes -> Out of Stock -> Save",
    '''    page.goto("%s/?sid=%s" % (BASE, SID))
    page.wait_for_selector("nav.admin__menu-wrap")
    page.click("li.level-0 a.menu-item:has-text('Reports')")
    page.click("div.submenu li.level-2 a:has-text('Search Terms')")
    page.wait_for_selector("table")
    # Default sort is ID descending: click Hits to rank by popularity.
    page.click("th:has-text('Hits')")
    page.click("th:has-text('Hits')")          # descending
    # Top row is the injected 'selene yoga hoodie' at 31 hits (next is hollister, 19).

    open_products_grid(page)
    keyword_search(page, "selene")
    # 16 records found: WH05 children 1093-1107 plus parent 1108.
    select_all_matching(page)
    mass_action(page, "Update attributes")
    page.wait_for_selector("#bulk-stock-status")
    page.select_option("#bulk-stock-status", "0")     # Out of Stock
    page.click("form.admin__form-section button.action-primary")
''')

write(
    "retire_product_line_chloe_takedown_logged_007",
    "  / -> Catalog > Products -> keyword 'chloe compete' -> Options > Select All -> Actions > Change status / Disable -> System > Custom Variables -> Add New Variable -> Save",
    '''    open_products_grid(page)
    keyword_search(page, "chloe compete")
    # 16 records found: WT06 1749-1764.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")
    # The grid message reads "A total of 16 record(s) have been updated."

    page.click("li.level-0 a.menu-item:has-text('System')")
    page.click("div.submenu li.level-2 a:has-text('Custom Variables')")
    page.click("#add")
    page.wait_for_selector("#rf_code")
    page.fill("#rf_code", "line_retirement_log")
    page.fill("#rf_name", "Line Retirement Log")
    page.fill("#rf_plain_value", "16")
    page.click("#save")
''')

write(
    "retire_product_line_gobi_takedown_finish_008",
    "  / -> Catalog > Products -> keyword 'gobi' -> Filters > Status = Enabled -> Select All -> Disable; then re-search and Update attributes > Out of Stock",
    '''    open_products_grid(page)
    keyword_search(page, "gobi")
    open_filters(page)
    page.select_option("select[name='status']", "1")   # Enabled
    apply_filters(page)
    # 11 records found - the rows the half-done takedown left live.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")

    # Second pass: the whole line out of stock. AdminGrid.jsx:190 clears the
    # selection whenever the query string changes, so this must be a fresh
    # select-then-apply.
    open_filters(page)
    page.select_option("select[name='status']", "")    # clear the status facet
    apply_filters(page)
    # 16 records found - entity_ids 431-446.
    select_all_matching(page)
    mass_action(page, "Update attributes")
    page.wait_for_selector("#bulk-stock-status")
    page.select_option("#bulk-stock-status", "0")
    page.click("form.admin__form-section button.action-primary")
''')

write(
    "retire_product_line_karmen_size_29_run_009",
    "  / -> Catalog > Products -> keyword 'Karmen Yoga Pant-29' -> Options > Select All -> Actions > Change status / Disable",
    '''    open_products_grid(page)
    keyword_search(page, "Karmen Yoga Pant-29")
    # 3 records found: 1816 WP01-29-Black, 1817 WP01-29-Gray, 1818 WP01-29-White.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")
''')

write(
    "retire_product_line_cheaper_pant_line_retired_010",
    "  / -> Catalog > Products -> keyword 'cora' (read price) -> keyword 'aeon' (read price) -> Select All on the cheaper family -> Actions > Change status / Disable",
    '''    open_products_grid(page)
    keyword_search(page, "cora parachute")
    # 7 records found, Price column reads $75.00 on every row.
    keyword_search(page, "aeon capri")
    # 7 records found, Price column reads $48.00 on every row -> Aeon is cheaper.
    select_all_matching(page)
    mass_action(page, "Change status / Disable")
''')

print("wrote replay drafts to", REPLAYS)

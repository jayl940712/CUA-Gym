from pathlib import Path
D = Path("output/tasks/shopping/_batches/shopping_advsearch_bench/replays")
PRE = 'TIMEOUT = 30000\n\n\ndef _page(lane):\n    for name in ("shopping", "webarena_shopping_mock"):\n        try:\n            return lane.page(name)\n        except KeyError:\n            continue\n    return lane.page()\n\n\nasync def _settle(page, selector):\n    # AppProvider\'s boot awaits fetchServerState + deferred chunks AFTER the page\n    # reports idle, so wait for real content and then give the store a beat.\n    await page.wait_for_selector(selector, timeout=TIMEOUT)\n    await page.wait_for_timeout(1200)\n\n\nasync def _advanced(page, name="", description="", price_from="", price_to=""):\n    """Footer/search-block \'Advanced Search\' -> fill the form -> Search."""\n    await page.get_by_role("link", name="Advanced Search").first.click()\n    await _settle(page, "#form-validate")\n    await page.fill("#name", name)\n    await page.fill("#sku", "")\n    await page.fill("#description", description)\n    await page.fill("#short_description", "")\n    await page.fill("#price", price_from)\n    await page.fill("#price_to", price_to)\n    await page.locator("#form-validate").get_by_role("button", name="Search").click()\n    await page.wait_for_selector(".search.found", timeout=TIMEOUT)\n    await _settle(page, ".search.results li.product-item")\n\n\nasync def _found_count(page):\n    text = await page.locator(".search.found").inner_text()\n    return int(text.strip().split()[0])\n\n\ndef _tiles(page):\n    return page.locator(".search.results li.product-item")\n\n'

def w(task_id, head, body):
    (D / f"{task_id}.py").write_text(f'"""{head}"""\n\n' + PRE + "\n" + body, encoding="utf-8")

w("shopping_advsearch_bench_binoculars_floor_compare_swap_001",
  """Golden replay: binoculars floor -> compare-list swap.

Home -> Advanced Search -> name=binoculars, price from 400 -> cheapest hit onto
the comparison list and into the cart -> Compare Products -> remove the two
preloaded columns. No page.goto(), no constructed URLs.
""", '''
TARGET = "SLSFJLKJ 10X42 FMC Binoculars"
PRELOADED = ("Uttermost Volterra", "NOZE Rustic Coat Rack")


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")
    # Precondition: the injected pair makes the header Compare link render.
    assert await page.get_by_role("link", name="Compare Products").count() == 1

    await _advanced(page, name="binoculars", price_from="400")
    assert await _found_count(page) == 3

    tile = _tiles(page).filter(has_text=TARGET)
    assert await tile.count() == 1
    await tile.get_by_role("button", name="Add to Compare").click()
    await page.wait_for_timeout(700)
    await tile.get_by_role("button", name="Add to Cart").click()
    await page.wait_for_timeout(900)

    await page.get_by_role("link", name="Compare Products").first.click()
    await _settle(page, "#product-comparison")
    assert await page.locator("td.cell.product.info").count() == 3

    for name in PRELOADED:
        cell = page.locator("td.cell.product.info").filter(has_text=name)
        assert await cell.count() == 1
        await cell.get_by_role("button", name="Remove Product").click()
        await page.wait_for_timeout(900)

    await page.wait_for_selector("#product-comparison", timeout=TIMEOUT)
    assert await page.locator("td.cell.product.info").count() == 1
''')

w("shopping_advsearch_bench_microwave_floor_wishlist_tally_002",
  """Golden replay: microwave floor -> wish-list row carrying the match tally.
""", '''
TARGET = "YJYDD Microwave Stand Industrial"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="microwave", price_from="500")
    tally = await _found_count(page)
    assert tally == 4

    tile = _tiles(page).filter(has_text=TARGET)
    assert await tile.count() == 1
    await tile.get_by_role("button", name="Add to Wish List").click()
    await page.wait_for_timeout(900)

    await page.get_by_role("link", name="My Wish List").first.click()
    await _settle(page, ".wishlist-grid li.product-item")
    row = page.locator(".wishlist-grid li.product-item").filter(has_text=TARGET)
    assert await row.count() == 1
    await row.locator("textarea.product-item-comment").fill(str(tally))
    await page.get_by_role("button", name="Update Wish List").click()
    await page.wait_for_timeout(1200)
''')

w("shopping_advsearch_bench_microscope_ceiling_price_review_003",
  """Golden replay: microscope ceiling -> five-star review whose summary is the price.
""", '''
TARGET = "AmScope SE401Z-P"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="microscope", price_to="300")
    assert await _found_count(page) == 7

    tile = _tiles(page).filter(has_text=TARGET)
    assert await tile.count() == 1
    price = (await tile.locator(".price").first.inner_text()).strip()
    assert price == "$276.88"
    await tile.locator("strong.product-item-name a").click()
    await _settle(page, "h1")

    link = page.get_by_role("link", name="Be the first to review this product")
    assert await link.count() == 1
    await link.first.click()
    await _settle(page, "#review-form")
    await page.click("label.rating-5")
    await page.fill("#nickname_field", "Emma")
    await page.fill("#summary_field", price)
    await page.fill("#review_field", "Crisp optics and a solid stand for the money.")
    await page.get_by_role("button", name="Submit Review").click()
    await page.wait_for_timeout(1500)
''')

w("shopping_advsearch_bench_dishwasher_description_pair_compare_004",
  """Golden replay: description='dishwasher safe' + price floor -> both hits compared,
cheaper one carted.
""", '''
CHEAPER = "XHZC Cutlery Set"
DEARER = "LLSS Dinner Set"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, description="dishwasher safe", price_from="700")
    assert await _found_count(page) == 2

    for name in (CHEAPER, DEARER):
        tile = _tiles(page).filter(has_text=name)
        assert await tile.count() == 1
        await tile.get_by_role("button", name="Add to Compare").click()
        await page.wait_for_timeout(800)

    tile = _tiles(page).filter(has_text=CHEAPER)
    assert (await tile.locator(".price").first.inner_text()).strip() == "$1,081.88"
    await tile.get_by_role("button", name="Add to Cart").click()
    await page.wait_for_timeout(1000)
''')

w("shopping_advsearch_bench_projector_band_extremes_split_005",
  """Golden replay: projector band -> cheapest carted, dearest wish-listed, using the
advanced-result sorter in both directions.
""", '''

async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="projector", price_from="900", price_to="20000")
    assert await _found_count(page) == 62

    # Sort by Price. Both price keys are present, so withParams keeps the query
    # balanced and the result page re-renders.
    await page.select_option("#sorter", "price")
    await _settle(page, ".search.results li.product-item")
    first = _tiles(page).first
    assert (await first.locator(".price").first.inner_text()).strip() == "$947.09"
    await first.get_by_role("button", name="Add to Cart").click()
    await page.wait_for_timeout(1000)

    await page.locator("button.sorter-action").click()
    await _settle(page, ".search.results li.product-item")
    first = _tiles(page).first
    assert (await first.locator(".price").first.inner_text()).strip() == "$17,774.32"
    await first.get_by_role("button", name="Add to Wish List").click()
    await page.wait_for_timeout(1000)
''')

w("shopping_advsearch_bench_tripod_band_reviewed_split_006",
  """Golden replay: tripod band -> the tile that renders a rating goes on the compare
list, the tile that renders none goes in the cart.
""", '''
REVIEWED = "Canon PowerShot SX620"
UNREVIEWED = "NCRD Selfie Stick"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="tripod", price_from="300", price_to="400")
    assert await _found_count(page) == 2

    reviewed = _tiles(page).filter(has_text=REVIEWED)
    unreviewed = _tiles(page).filter(has_text=UNREVIEWED)
    assert await reviewed.count() == 1 and await unreviewed.count() == 1
    # The discriminator is the presence of the rating node itself.
    assert await reviewed.locator(".product-reviews-summary").count() == 1
    assert await unreviewed.locator(".product-reviews-summary").count() == 0

    await reviewed.get_by_role("button", name="Add to Compare").click()
    await page.wait_for_timeout(800)
    await unreviewed.get_by_role("button", name="Add to Cart").click()
    await page.wait_for_timeout(1000)
''')

w("shopping_advsearch_bench_speaker_band_qty_tally_007",
  """Golden replay: bluetooth-speaker band -> cheapest hit carted at a quantity equal
to the number of matches.
""", '''
TARGET = "Herdio 5.25 Inches"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="bluetooth speaker", price_from="200", price_to="500")
    tally = await _found_count(page)
    assert tally == 11

    tile = _tiles(page).filter(has_text=TARGET)
    assert await tile.count() == 1
    assert (await tile.locator(".price").first.inner_text()).strip() == "$299.98"
    await tile.locator("strong.product-item-name a").click()
    await _settle(page, "#product-addtocart-button")

    await page.fill("#qty", str(tally))
    await page.click("#product-addtocart-button")
    await page.wait_for_timeout(1200)
''')

w("shopping_advsearch_bench_cutting_board_cart_line_swap_008",
  """Golden replay: advanced search for a chopping board -> cart it, then drop the
bodysuit line from the shopping cart.
""", '''
BOARD = "The Ultimate Gourmet Cutting Board"
BODYSUIT = "Plus Size Lingerie"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="cutting board", price_from="60")
    assert await _found_count(page) == 2

    tile = _tiles(page).filter(has_text=BOARD)
    assert await tile.count() == 1
    assert (await tile.locator(".price").first.inner_text()).strip() == "$68.55"
    await tile.get_by_role("button", name="Add to Cart").click()
    await page.wait_for_timeout(1000)

    # Header My Cart toggles the flyout; View and Edit Cart is the second click.
    await page.get_by_role("link", name="My Cart").first.click()
    await page.wait_for_timeout(700)
    await page.get_by_role("link", name="View and Edit Cart").first.click()
    await _settle(page, "#shopping-cart-table")

    row = page.locator("#shopping-cart-table tbody").filter(has_text=BODYSUIT)
    assert await row.count() == 1
    await row.get_by_title("Remove item").first.click()
    await page.wait_for_timeout(1200)
''')

w("shopping_advsearch_bench_bookcase_wishlist_retire_009",
  """Golden replay: cheapest bookcase in the band saved, then the dearer of the two
preloaded wish-list rows removed.
""", '''
BOOKCASE = "W&X Multi-Functional Storage Shelf"
DEARER = "Atlantic Furniture Metro Platform Bed"
KEEPER = "Neewer 90W Desk Mount LED Video Light"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="bookcase", price_from="500", price_to="1000")
    assert await _found_count(page) == 7

    tile = _tiles(page).filter(has_text=BOOKCASE)
    assert await tile.count() == 1
    assert (await tile.locator(".price").first.inner_text()).strip() == "$563.99"
    await tile.get_by_role("button", name="Add to Wish List").click()
    await page.wait_for_timeout(1000)

    await page.get_by_role("link", name="My Wish List").first.click()
    await _settle(page, ".wishlist-grid li.product-item")
    rows = page.locator(".wishlist-grid li.product-item")
    assert await rows.count() == 3
    # $794.33 is dearer than the $563.99 bookcase; $209.49 is not.
    dearer = rows.filter(has_text=DEARER)
    assert await dearer.count() == 1
    assert "$794.33" in await dearer.inner_text()
    keeper = rows.filter(has_text=KEEPER)
    assert "$209.49" in await keeper.inner_text()

    await dearer.get_by_role("link", name="Remove item").click()
    await page.wait_for_timeout(1200)
''')

w("shopping_advsearch_bench_telescope_floor_sole_hit_trio_010",
  """Golden replay: the only telescope at or above $500, three of it in the cart.
""", '''
TARGET = "AWJ Telescope,70Mm Aperture"


async def run(lane, task):
    page = _page(lane)
    await _settle(page, "#maincontent")

    await _advanced(page, name="telescope", price_from="500")
    assert await _found_count(page) == 1

    tile = _tiles(page).filter(has_text=TARGET)
    assert await tile.count() == 1
    await tile.locator("strong.product-item-name a").click()
    await _settle(page, "#product-addtocart-button")

    await page.fill("#qty", "3")
    await page.click("#product-addtocart-button")
    await page.wait_for_timeout(1200)
''')

print("replays written")

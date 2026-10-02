#!/usr/bin/env python3
"""Batch-6 lane 35 generator: shopping / R3 -> A7.

Chain: sum a stated month or window of Emma's order history, then SUBMIT the
Contact Us form quoting that figure.  ContactPage.jsx:17-21 keeps typed values
in React useState; only submitContact (AppContext.jsx:495) persists to
state.contactSubmissions, so every task in this lane requires a real Submit.

Writes bundles to output/tasks/shopping/<task_id>/ plus the lane's
GENERATION.md, replay drafts, index.json and nemo_tasks.jsonl.
"""

import json
import os
import shutil

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output", "tasks", "shopping")
BATCH = os.path.join(OUT, "_batches", "month_spend_contact_form")
REPLAYS = os.path.join(BATCH, "replays")

APP_DIR = "webarena_shopping_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

EMMA_ADDRESS = {
    "firstname": "Emma",
    "lastname": "Lopez",
    "street": "101 S San Mateo Dr",
    "city": "San Mateo",
    "region": "California",
    "postcode": "94010",
    "country_id": "US",
    "telephone": "6505551212",
    "company": None,
    "email": None,
}


def order(entity_id, status, created_at, items, item_id_base):
    """Build one order record in placeOrder's exact convention.

    AppContext.jsx:554-583 writes every field below; shipping is $5.00 per
    item (utils/orders.js FLAT_RATE_PER_ITEM) and grandTotal = subtotal +
    shippingAmount with tax and discount both zero, which holds for all 37
    seeded orders.
    """
    qty = sum(i["qty"] for i in items)
    subtotal = round(sum(i["price"] * i["qty"] for i in items), 2)
    shipping = 5 * qty
    grand = round(subtotal + shipping, 2)
    return {
        "entityId": entity_id,
        "incrementId": str(entity_id).zfill(9),
        "status": status,
        "state": "new" if status == "pending" else status,
        "createdAt": created_at,
        "grandTotal": grand,
        "subtotal": subtotal,
        "shippingAmount": shipping,
        "taxAmount": 0,
        "discountAmount": 0,
        "totalQtyOrdered": qty,
        "shippingDescription": "Flat Rate - Fixed",
        "customerEmail": "emma.lopez@gmail.com",
        "shippingMethod": "flatrate_flatrate",
        "paymentMethod": "checkmo",
        "paymentTitle": "Check / Money order",
        "billingAddress": dict(EMMA_ADDRESS),
        "shippingAddress": dict(EMMA_ADDRESS),
        "items": [
            {
                "itemId": item_id_base + n,
                "productId": i["productId"],
                "sku": i["sku"],
                "name": i["name"],
                "price": i["price"],
                "qtyOrdered": i["qty"],
                "rowTotal": round(i["price"] * i["qty"], 2),
                "productType": "simple",
                "options": [],
            }
            for n, i in enumerate(items)
        ],
    }


# --- real catalog lines, all lifted verbatim from seeded order items --------
CHAI = {
    "productId": 21777,
    "sku": "B00022VUAK",
    "name": "2 Canisters of Flamingo Vanilla Decaf Sugar-Free Chai, 11.9oz.",
    "price": 25.99,
    "qty": 1,
}
TEA_DROPS = {
    "productId": 22906,
    "sku": "B07ZG4X2X1",
    "name": (
        "Tea Drops Organic Citrus Ginger Tea - Bulk Pack of 20 Lightly Sweetened, "
        "Loose Leaf, Pressed Organic Tea - Herbal Citrus Ginger Tea Blend To Go - "
        "Iced or Hot Bagless Tea Gift"
    ),
    "price": 22.99,
    "qty": 1,
}
COFFEE_TABLE = {
    "productId": 15477,
    "sku": "B09Q3DZ1DR",
    "name": (
        'P PURLOVE 47.2" Rectangle Modern Coffee Table 2 Tier Coffee Table Cocktail '
        "Table with LED Light with 16 Colors for Living Room Bedroom"
    ),
    "price": 189.99,
    "qty": 1,
}
SPEAKER = {
    "productId": 19567,
    "sku": "B085VHV4GW",
    "name": (
        "Pantone Ultra-HD Sound Waterproof Handsfree Hanging Bluetooth Subwoofer "
        "Speaker - 8Hr Play Time, Mic, BT Calls, Long Distance Connectivity, "
        "iOS/Android Compatible [Lime Green]"
    ),
    "price": 29.99,
    "qty": 2,
}
SANDAL = {
    "productId": 25683,
    "sku": "B00QH4Q1VA",
    "name": (
        "SIKA 173105 Optimax Sandal OB SRA - Ideal for Hospital and Care, "
        "Hotel/Restaurant/Canteen, Service and Cleaning, Pharmaceutical and Food Industry"
    ),
    "price": 101.90,
    "qty": 1,
}
DINING_CHAIR = {
    "productId": 15919,
    "sku": "B07DB4R43W",
    "name": "Christopher Knight Home Venetian Velvet Dining Chair, Black",
    "price": 276.11,
    "qty": 2,
}

# entityIds 150, 151, 152, 153 and 186 are the only gaps in the seeded
# 148..189 range, so an injected order carrying one of them looks native and
# leaves nextOrderEntityId / nextOrderIncrementId at their pristine 190.
INJ_DEC22 = order(186, "complete", "2022-12-21 15:42:08", [CHAI, TEA_DROPS], 100000)
INJ_NOV22 = order(150, "canceled", "2022-11-15 19:05:33", [COFFEE_TABLE], 100010)
INJ_MAR23 = order(151, "complete", "2023-03-22 14:10:26", [SPEAKER], 100020)
INJ_JAN23 = order(152, "complete", "2023-01-09 16:22:41", [SANDAL], 100030)
INJ_SEP22 = order(153, "canceled", "2022-09-12 13:44:52", [DINING_CHAIR], 100040)


ORDER_ANALOGUE_MAR = "How much I spend in March 2023 on shopping at One Stop Market?"
ORDER_ANALOGUE_JUL = "How much I spend in July 2022 on shopping at One Stop Market?"
ORDER_ANALOGUE_NOV = (
    "How much did I spend on shopping at One Stop Market on November 2022? "
    "They gave me a 20% discount on the total amount for orders exceeding $200 in cash"
)
ORDER_ANALOGUE_FOOD = (
    "How much I spent on food-related shopping during March 2023? "
    "Include shipping fee for each item is $5."
)
ORDER_ANALOGUE_EACH_MONTH = (
    "How much I spend each month from Jan to the end of March 2023 on shopping at "
    "One Stop Market? Give me the dollar amount for each month separately."
)
ORDER_ANALOGUE_NONCANCELLED = "Get the total payment amount of the last 5 non-cancelled orders"
ORDER_ANALOGUE_CANCELLED = "Tell me the total cost of my latest cancelled order?"
ORDER_ANALOGUE_PENDING = "Get the total payment amount of the last 5 pending orders"
ORDER_ANALOGUE_PASTFOUR = (
    "Today is 6/12/2023. Tell me how many fulfilled orders I have over the past four "
    "month, and the total amount of money I spent."
)
CONTACT_ANALOGUE = (
    'Fill out the contact us form with this refund message for the Stereo Sound System '
    'bought Feb 2023: "I need a refund. Order: <order_id>. Amount: <amount>. Reason: It '
    'broke after three days of use." Leave the filled form ready for review and do not '
    "submit it. Fill in the order id and amount information from my order history."
)


TASKS = [
    {
        "id": "month_spend_contact_form_dec2022_injected_gross_001",
        "style": "terse",
        "instruction": (
            "Work out what my December 2022 orders came to in total, shipping included, "
            "and send that figure to store support through the Contact Us form. "
            "Put only the amount in the message."
        ),
        "amount": "262.38",
        "component": "december_2022_total_recorded",
        "derived_from": "monthly_spend_logged_dec22_vs_jan23_gap_005",
        "analogues": [ORDER_ANALOGUE_NOV, CONTACT_ANALOGUE],
        "setup": {
            "orders": [INJ_DEC22],
            "why": (
                "Injects order 000000186, a $58.98 complete order dated 2022-12-21, into "
                "December 2022. The pristine December total is $203.40 and is quoted in the "
                "batch-5 census, so the injection moves the only correct answer to $262.38 "
                "and makes the sum unmemorisable. Nothing in contactSubmissions is touched, "
                "so the post-setup state still scores 0.0."
            ),
        },
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {262.38}: the four seeded "
                "December 2022 orders (000000162 $53.29, 000000184 $20.49, 000000154 $97.15, "
                "000000174 $32.47) plus the injected 000000186 $58.98."
            ),
        ],
        "notes": [
            "December 2022 contains no cancelled order before or after the injection, so "
            "'total' is unambiguous and no status predicate is needed.",
            "Order 000000154 stores 2022-12-19 and renders 12/18/22 under America/New_York "
            "(format.js:4). It stays inside December, so the month bucket is timezone-safe.",
            "Grand totals are a column on /sales/order/history/ (OrderHistoryPage.jsx:59), "
            "so no per-order drill-in is required.",
        ],
    },
    {
        "id": "month_spend_contact_form_oct2022_net_of_cancels_002",
        "style": "terse",
        "instruction": (
            "Add up my October 2022 orders, skipping the ones I cancelled, and message "
            "store support through Contact Us with that total. "
            "Put only the amount in the message."
        ),
        "amount": "1209.90",
        "component": "october_2022_net_spend_recorded",
        "derived_from": "monthly_spend_logged_oct2022_all_statuses_002",
        "analogues": [ORDER_ANALOGUE_NONCANCELLED, CONTACT_ANALOGUE],
        "setup": None,
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {1209.90}: 000000178 $345.84 "
                "plus 000000176 $845.07 plus 000000185 $18.99, with the cancelled 000000177 "
                "$2,126.32 excluded."
            ),
        ],
        "notes": [
            "The cancelled order is the largest in the month, so the status predicate is "
            "load-bearing: an agent that ignores the Status column gets $3,336.22.",
            "Order 000000185 stores 2022-10-04 and renders 10/3/22; still October.",
            "Batch-5's oct2022 task summed ALL statuses; this one is the complement, so the "
            "correct answer and the rubric both differ.",
        ],
    },
    {
        "id": "month_spend_contact_form_cancelled_during_2022_003",
        "style": "terse",
        "instruction": (
            "I want to know how much the orders I cancelled during 2022 were worth "
            "altogether. Total them up and send that amount to store support using the "
            "Contact Us form. Put only the amount in the message."
        ),
        "amount": "3053.97",
        "component": "cancelled_2022_value_recorded",
        "derived_from": None,
        "analogues": [ORDER_ANALOGUE_CANCELLED, CONTACT_ANALOGUE],
        "setup": None,
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {3053.97}: the six 2022 "
                "cancelled orders 000000160 $115.18, 000000173 $206.59, 000000182 $173.56, "
                "000000149 $354.66, 000000172 $77.66 and 000000177 $2,126.32."
            ),
        ],
        "notes": [
            "Nine orders are cancelled overall; the three from 2023 (000000158 $174.99, "
            "000000156 $231.54, 000000170 $365.42) are out of scope, so the whole-history "
            "cancelled total $3,825.92 is a wrong answer and the year filter is load-bearing.",
            "The six 2022 cancellations are spread across pages 1-4 of the 10-row grid; the "
            "limiter select (OrderHistoryPage.jsx:78-83) offers 20 and 50 per page.",
            "Order 000000170 stores 2023-05-18 and renders 5/17/23 - still 2023, so the "
            "year bucket survives the America/New_York shift.",
        ],
    },
    {
        "id": "month_spend_contact_form_nov2022_injected_cancel_trap_004",
        "style": "terse",
        "instruction": (
            "One of my November 2022 orders got cancelled. Total what I actually paid that "
            "month, leaving that one out, and send the amount to store support through the "
            "Contact Us form. Put only the amount in the message."
        ),
        "amount": "403.18",
        "component": "november_2022_net_spend_recorded",
        "derived_from": "monthly_spend_logged_nov2022_shipping_share_006",
        "analogues": [ORDER_ANALOGUE_NOV, CONTACT_ANALOGUE],
        "setup": {
            "orders": [INJ_NOV22],
            "why": (
                "Pristine November 2022 holds three orders and all three are complete, so a "
                "'leave out the cancelled one' instruction would be decoration. Injecting "
                "000000150, a $194.99 CANCELLED order dated 2022-11-15, plants a distractor "
                "that satisfies the month filter and fails the status filter. The correct "
                "answer stays $403.18; an agent that skips the Status column reads $598.17. "
                "contactSubmissions is untouched, so the post-setup state scores 0.0."
            ),
        },
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {403.18}: 000000183 $51.94 "
                "plus 000000171 $133.07 plus 000000164 $218.17, with the injected cancelled "
                "000000150 $194.99 excluded."
            ),
        ],
        "notes": [
            "This is a distractor injection, not an arithmetic one: the sum is unchanged and "
            "only the predicate becomes real.",
            "None of the five timezone-shifted orders (185, 154, 163, 166, 170) falls in "
            "November 2022, and the injected order is stamped 19:05:33 UTC = 14:05 EST, so "
            "the month bucket is safe.",
        ],
    },
    {
        "id": "month_spend_contact_form_augsep2022_merchandise_only_005",
        "style": "explicit",
        "instruction": (
            "I need to separate merchandise from shipping in my August and September 2022 "
            "spending. This store charges flat-rate shipping of $5.00 per item, and each "
            "order's own page shows its subtotal on a separate line from the shipping "
            "charge. Add up the merchandise subtotals of every order placed in August 2022 "
            "and September 2022 - include the one that was cancelled - then open the Contact "
            "Us form and submit that combined subtotal to store support. Put only the amount "
            "in the message."
        ),
        "amount": "3098.02",
        "component": "aug_sep_2022_merchandise_subtotal_recorded",
        "derived_from": "monthly_spend_logged_mar2023_merchandise_only_007",
        "analogues": [ORDER_ANALOGUE_FOOD, CONTACT_ANALOGUE],
        "setup": None,
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {3098.02}: August subtotals "
                "000000155 $28.99, 000000172 $62.66 and 000000165 $26.99, plus September "
                "subtotals 000000175 $113.85 and 000000179 $2,865.53."
            ),
        ],
        "notes": [
            "The order grid shows only the grand total, so the subtotal has to come from the "
            "five order-view pages at /sales/order/view/order_id/<id>/, reachable by the "
            "View Order link in each grid row (OrderHistoryPage.jsx:61-63).",
            "Grand totals for the same window sum to $3,178.02, exactly $80.00 more (16 items "
            "at $5.00), so an agent that forgets to strip shipping lands on a distinct wrong "
            "number.",
            "Explicit style: the $5.00-per-item rule and the include-cancelled decision are "
            "both stated, because neither is derivable from the grid alone without opening "
            "every order.",
        ],
    },
    {
        "id": "month_spend_contact_form_q4_2022_completed_006",
        "style": "terse",
        "instruction": (
            "Add up everything I spent across October, November and December 2022, counting "
            "only orders that completed, and pass that quarter total to store support through "
            "the Contact Us form. Put only the amount in the message."
        ),
        "amount": "1816.48",
        "component": "q4_2022_completed_spend_recorded",
        "derived_from": "monthly_spend_logged_dec22_vs_jan23_gap_005",
        "analogues": [ORDER_ANALOGUE_EACH_MONTH, CONTACT_ANALOGUE],
        "setup": None,
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {1816.48}: October's completed "
                "$1,209.90 plus November's $403.18 plus December's $203.40, with the cancelled "
                "000000177 $2,126.32 excluded."
            ),
        ],
        "notes": [
            "Eleven orders fall in the window and ten of them completed; the single cancelled "
            "one is worth more than the whole correct answer, so ignoring status gives "
            "$3,942.80.",
            "Ten of the eleven rows sit below the page-1 boundary (CORRECTIONS #56 puts that "
            "boundary at createdAt > 2023-02-09 07:06:57), so the task genuinely requires the "
            "pager or the per-page limiter.",
            "Orders 000000185 (10/3/22) and 000000154 (12/18/22) are timezone-shifted but both "
            "stay inside the quarter.",
        ],
    },
    {
        "id": "month_spend_contact_form_mar2023_injected_total_007",
        "style": "terse",
        "instruction": (
            "Total my March 2023 spending at this store, shipping included, straight from my "
            "order history, then send that number to store support through the Contact Us "
            "form. Put only the amount in the message."
        ),
        "amount": "153.29",
        "component": "march_2023_total_recorded",
        "derived_from": "monthly_spend_logged_mar2023_merchandise_only_007",
        "analogues": [ORDER_ANALOGUE_MAR, CONTACT_ANALOGUE],
        "setup": {
            "orders": [INJ_MAR23],
            "why": (
                "Pristine March 2023 is the single most quoted figure in the corpus ($83.31, "
                "two orders) and is the target of official task 330, so it is the value an "
                "agent is most likely to have memorised. Injecting 000000151, a $69.98 "
                "complete order dated 2023-03-22, moves the only correct answer to $153.29. "
                "contactSubmissions is untouched, so the post-setup state scores 0.0."
            ),
        },
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {153.29}: 000000166 $17.99 plus "
                "000000180 $65.32 plus the injected 000000151 $69.98."
            ),
        ],
        "notes": [
            "March 2023 holds no cancelled order before or after the injection, so 'total' is "
            "unambiguous.",
            "Order 000000166 stores 2023-03-11 and renders 3/10/23; it stays in March, and "
            "000000180 renders 3/11/23, so the two are adjacent in the grid but distinct.",
            "The pristine answer $83.31 is a specific, checkable wrong answer for an agent "
            "that recites the seed instead of reading the page.",
        ],
    },
    {
        "id": "month_spend_contact_form_jan2023_injected_reconcile_008",
        "style": "explicit",
        "instruction": (
            "I'm reconciling my January 2023 card statement against this store. Take every "
            "order dated January 2023 in my order history, whatever its status, and add up "
            "the order totals exactly as the grid shows them - those already include the flat "
            "shipping charge. Then open the Contact Us form and submit the resulting January "
            "2023 total to store support so they can check it against their books. Put only "
            "the amount in the message."
        ),
        "amount": "679.78",
        "component": "january_2023_total_recorded",
        "derived_from": "monthly_spend_logged_dec22_vs_jan23_gap_005",
        "analogues": [ORDER_ANALOGUE_EACH_MONTH, CONTACT_ANALOGUE],
        "setup": {
            "orders": [INJ_JAN23],
            "why": (
                "Pristine January 2023 is $572.88 over two orders and is quoted in the census. "
                "Injecting 000000152, a $106.90 complete order dated 2023-01-09, moves the only "
                "correct answer to $679.78 and puts a third row in the month. "
                "contactSubmissions is untouched, so the post-setup state scores 0.0."
            ),
        },
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {679.78}: 000000163 $132.24 plus "
                "000000148 $440.64 plus the injected 000000152 $106.90."
            ),
        ],
        "notes": [
            "All three January 2023 orders are complete, so 'whatever its status' is stated for "
            "clarity rather than as a filter; the instruction is explicit-style and says so.",
            "Order 000000163 stores 2023-01-17 and renders 1/16/23; still January.",
            "The grand-total column already includes shipping (grandTotal = subtotal + "
            "shippingAmount, tax and discount zero on all 37 seeded orders and on the injected "
            "one), so no drill-in is needed and the instruction says which number to read.",
        ],
    },
    {
        "id": "month_spend_contact_form_may2023_gross_all_statuses_009",
        "style": "terse",
        "instruction": (
            "For my records I need the gross value of every order dated May 2023, cancelled "
            "ones included. Total them and send the figure to store support through Contact "
            "Us. Put only the amount in the message."
        ),
        "amount": "4130.39",
        "component": "may_2023_gross_value_recorded",
        "derived_from": "monthly_spend_logged_pending_orders_total_010",
        "analogues": [ORDER_ANALOGUE_PENDING, CONTACT_ANALOGUE],
        "setup": None,
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {4130.39}: the three pending "
                "orders 000000187 $1,004.99, 000000188 $2,004.99 and 000000189 $754.99 plus the "
                "cancelled 000000170 $365.42."
            ),
        ],
        "notes": [
            "Deliberately the include-cancelled reading, and the instruction says so; the "
            "net-of-cancellations figure $3,764.97 is the discriminating wrong answer.",
            "All four rows sit at the head of the descending grid, so this one is page-1 work; "
            "its difficulty is the explicit status decision, not pagination.",
            "The three pending orders all render 5/2/23 and differ only by increment id, so "
            "nothing here is built on a day bucket - only the May 2023 month bucket, which the "
            "5/17/23 render of 000000170 does not leave.",
        ],
    },
    {
        "id": "month_spend_contact_form_sep2022_injected_cancel_trap_010",
        "style": "terse",
        "instruction": (
            "September 2022: one of those orders was cancelled, so leave it out. Add up the "
            "rest and send that total to store support using the Contact Us form. "
            "Put only the amount in the message."
        ),
        "amount": "3024.38",
        "component": "september_2022_net_spend_recorded",
        "derived_from": "monthly_spend_logged_sep2022_note_on_wishlist_lamp_004",
        "analogues": [ORDER_ANALOGUE_NONCANCELLED, CONTACT_ANALOGUE],
        "setup": {
            "orders": [INJ_SEP22],
            "why": (
                "Pristine September 2022 holds two orders and both are complete, so a "
                "'leave out the cancelled one' instruction would have nothing to bite on. "
                "Injecting 000000153, a $562.22 CANCELLED order dated 2022-09-12, plants a "
                "distractor that passes the month filter and fails the status filter: the "
                "correct answer stays $3,024.38 and an agent that ignores Status reads "
                "$3,586.60. contactSubmissions is untouched, so the post-setup state scores 0.0."
            ),
        },
        "criteria": [
            "state.contactSubmissions holds exactly one submission whose comment is non-empty.",
            (
                "That comment's set of money figures is exactly {3024.38}: 000000175 $133.85 plus "
                "000000179 $2,890.53, with the injected cancelled 000000153 $562.22 excluded."
            ),
        ],
        "notes": [
            "Distractor injection: the arithmetic is unchanged and the predicate becomes real.",
            "The injected order is stamped 13:44:52 UTC = 09:44 EDT on 2022-09-12, and none of "
            "the five timezone-shifted seeded orders falls in September 2022.",
            "Batch-5's September task wrote the derived value onto a wishlist row; this one "
            "submits it through Contact Us and adds a cancellation that did not exist, so both "
            "the writeback surface and the correct-answer derivation differ.",
        ],
    },
]


# --------------------------------------------------------------------------
# reward source
# --------------------------------------------------------------------------

REWARD_HELPERS = '''
import re
from decimal import Decimal, InvalidOperation

# A "money token" is either a dollar-prefixed number or a bare number written to
# two decimal places. A bare year such as 2022 is neither, so a message that
# names its month does not accidentally register the year as an amount.
_MONEY_RE = re.compile(r"\\$\\s*\\d[\\d,]*(?:\\.\\d+)?|\\d[\\d,]*\\.\\d{2}")


def _amounts(text):
    found = set()
    if not isinstance(text, str):
        return found
    for raw in _MONEY_RE.findall(text):
        cleaned = raw.replace("$", "").replace(",", "").strip()
        try:
            value = Decimal(cleaned)
        except (InvalidOperation, ValueError):
            continue
        try:
            found.add(value.quantize(Decimal("0.01")))
        except (InvalidOperation, ValueError):
            continue
    return found


def _submissions(state):
    if not isinstance(state, dict):
        return []
    rows = state.get("contactSubmissions")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _sole_comment(state):
    rows = _submissions(state)
    if len(rows) != 1:
        return None
    comment = rows[0].get("comment")
    if not isinstance(comment, str) or not comment.strip():
        return None
    return comment
'''


def reward_body(task):
    return '''

COMPONENT_WEIGHTS = {
    "contact_message_submitted": 0.3,
    "%(component)s": 0.7,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

EXPECTED_AMOUNTS = set([Decimal("%(amount)s")])


def _checks(state):
    comment = _sole_comment(state)
    results = {}
    results["contact_message_submitted"] = comment is not None
    results["%(component)s"] = comment is not None and _amounts(comment) == EXPECTED_AMOUNTS
    return results
''' % {"component": task["component"], "amount": task["amount"]}


def reward_py(task):
    doc = '"""Deterministic reward for %s.\n\nSuccess criteria:\n%s\n\nScoring reads current_state only, never a diff against initial_state, so an\nempty current_state scores 0.0 on every component and a key that returns to\nits pristine value cannot fabricate a miss.\n\nOrder records are immutable on the storefront - there is no cancel, status or\norder-total control anywhere in pages/, components/ or context/ - so the\nderived figure cannot move mid-episode.\n"""\n' % (
        task["id"],
        "\n".join("  * " + c for c in task["criteria"]),
    )
    tail = '''

def _app(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app
    return {}


def evaluate(evidence):
    app = _app(evidence)
    state = app.get("current_state") if isinstance(app.get("current_state"), dict) else {}
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
    return doc + REWARD_HELPERS + reward_body(task) + tail


def nemo_reward_py(task):
    doc = '"""NeMo-Gym reward program for %s.\n\nImplements exactly the rubric of reward.py, reading current_state from\nGET /go?sid=... instead of a frozen evidence bundle, and printing\nREWARD: <float> on every output path including the error path.\n\nSelf-contained: standard library plus requests, which is present in\ncuagym/requirements.txt.\n"""\n\nimport sys\n\nimport requests\n' % task["id"]
    ids = '''
SID = "__CUA_GYM_SID__"
BASE_URL = "%s"
''' % URL_PLACEHOLDER
    tail = '''

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
    except Exception as exc:
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    try:
        value = score_state(state)
    except Exception as exc:
        print("reward scoring failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    print("REWARD: %s" % value)


main()
'''
    return doc + REWARD_HELPERS + ids + reward_body(task) + tail


def setup_py(task):
    setup = task["setup"]
    if not setup:
        return None
    fixture = json.dumps(setup["orders"], indent=1)
    doc = '"""NeMo-Gym setup program for %s.\n\n%s\n\nThe pristine session document is read back from GET /go?sid= first and the\npatched document is POSTed whole, so no top-level key is dropped whichever way\nthe state API treats a partial set. The inlined fixture is a raw string\nliteral, so no escape is eaten by the Python parser before the JSON decoder\nsees it.\n\nSelf-contained: standard library plus requests, which is present in\ncuagym/requirements.txt.\n"""\n\nimport json\nimport sys\n\nimport requests\n\nSID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\nINJECTED_ORDERS = json.loads(r"""\n%s\n""")\n' % (
        task["id"],
        setup["why"],
        URL_PLACEHOLDER,
        fixture,
    )
    tail = '''

def main():
    read = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    read.raise_for_status()
    payload = read.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not state:
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: no session document to patch", file=sys.stderr)
        raise SystemExit(1)
    state = json.loads(json.dumps(state))
    existing = state.get("orders")
    if not isinstance(existing, list):
        existing = []
    injected_ids = set()
    for row in INJECTED_ORDERS:
        injected_ids.add(row["entityId"])
    kept = []
    for row in existing:
        if isinstance(row, dict) and row.get("entityId") in injected_ids:
            continue
        kept.append(row)
    state["orders"] = kept + INJECTED_ORDERS
    state["contactSubmissions"] = []
    written = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    written.raise_for_status()
    print("SETUP OK")


main()
'''
    return doc + tail


REPLAY_TEMPLATE = '''"""Golden replay draft for %(id)s.

Click-only from start_path "/": header My Account -> account nav My Orders ->
per-page limiter -> (order rows / View Order) -> footer Contact Us -> Submit.
No page.goto after the initial landing, no constructed URL.

DRAFT: the derived figure below is the authored ground truth
(%(amount)s). golden-browser must re-derive it from the rendered grid
rather than trusting this constant.
"""

DERIVED_TOTAL = "%(amount)s"


def run(page, base_url):
    page.goto(base_url + "/")

    # 1. Retrieval (R3): reach the order history by clicking only.
    page.get_by_role("link", name="My Account").first.click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="My Orders").first.click()
    page.wait_for_load_state("networkidle")

    # Show every order on one page so the month/window can be summed without
    # constructing a ?p= URL.
    page.select_option("#order-limiter", "50")
    page.wait_for_load_state("networkidle")

%(retrieval)s

    # 2. Action (A7): footer Contact Us is rendered on every page
    # (Footer.jsx:26-36, storeConfig.json footerLinks).
    page.get_by_role("link", name="Contact Us").first.click()
    page.wait_for_load_state("networkidle")

    # Name and Email are prefilled from state.customer; only the comment is
    # authored. The form MUST be submitted - ContactPage.jsx:17-21 keeps typed
    # values in React useState and only submitContact persists them.
    page.fill("#comment", "$" + DERIVED_TOTAL)
    page.get_by_role("button", name="Submit").click()
    page.wait_for_load_state("networkidle")
'''


def replay_retrieval(task):
    lines = ["    # Rows in scope, as they render in the grid:"]
    for c in task["criteria"][1:]:
        lines.append("    #   " + c)
    if task["setup"]:
        lines.append("    # An injected order from initial_setup.py participates in this sum.")
    if "merchandise" in task["id"]:
        lines.append("    # Each subtotal needs the order's own page: click View Order in the")
        lines.append("    # row, read the Subtotal line, then click My Orders again.")
    return "\n".join(lines)


def write_bundle(task):
    d = os.path.join(OUT, task["id"])
    os.makedirs(d, exist_ok=True)

    ti = {
        "task_id": task["id"],
        "task_instruction": task["instruction"],
        "app_dir": APP_DIR,
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": task["criteria"],
    }
    with open(os.path.join(d, "task_instruction.json"), "w") as f:
        json.dump(ti, f, indent=2)
        f.write("\n")

    setup_src = setup_py(task)
    if setup_src is not None:
        with open(os.path.join(d, "initial_setup.py"), "w") as f:
            f.write(setup_src)
        injected = [task["setup"]["why"]]
    else:
        injected = []

    manifest = {
        "schema_version": 2,
        "task_id": task["id"],
        "instruction": task["instruction"],
        "apps": [
            {
                "name": APP_DIR,
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
            "style": task["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R3", "A7"],
            "skill_chain": (
                "sum the order totals over a stated month or window of the order history "
                "-> submit the Contact Us form quoting that figure"
            ),
            "derived_from": task["derived_from"],
            "official_analogues": task["analogues"],
            "injected_preconditions": injected,
            "topic": "month_spend_contact_form",
            "batch": "batch-6 lane 35 (shopping / R3 -> A7)",
            "lane": "month_spend_contact_form",
            "inspiration_ids": [],
            "authoring_notes": task["notes"],
        },
    }
    with open(os.path.join(d, "task.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    with open(os.path.join(d, "reward.py"), "w") as f:
        f.write(reward_py(task))
    nemo_src = nemo_reward_py(task)
    with open(os.path.join(d, "nemo_reward.py"), "w") as f:
        f.write(nemo_src)

    row = {
        "task_payload": {
            "task_id": task["id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task["id"],
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": nemo_src,
            },
        }
    }
    with open(os.path.join(d, "nemo_task.json"), "w") as f:
        json.dump(row, f, indent=2)
        f.write("\n")

    with open(os.path.join(REPLAYS, task["id"] + ".py"), "w") as f:
        f.write(REPLAY_TEMPLATE % {
            "id": task["id"],
            "amount": task["amount"],
            "retrieval": replay_retrieval(task),
        })
    return row


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    rows = []
    for task in TASKS:
        rows.append(write_bundle(task))

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    with open(os.path.join(BATCH, "index.json"), "w") as f:
        json.dump(
            {
                "schema_version": 2,
                "tasks": [
                    {"task_id": t["id"], "path": "%s/task.json" % t["id"]}
                    for t in TASKS
                ],
            },
            f,
            indent=2,
        )
        f.write("\n")

    print("wrote %d bundles" % len(TASKS))
    for t in TASKS:
        print("  %-58s %-8s %-9s $%s" % (
            t["id"], t["style"], "injected" if t["setup"] else "pristine", t["amount"]))


if __name__ == "__main__":
    main()

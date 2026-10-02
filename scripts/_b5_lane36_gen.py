#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 36 (shopping / refund_request_from_order).

Writes ten task bundles under output/tasks/shopping/<task_id>/ plus the lane's
GENERATION.md and golden-replay drafts. Reading-only against ./hub; this script
never touches the mock.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE = os.path.join(ROOT, "output", "tasks", "shopping")
BATCH = os.path.join(SITE, "_batches", "refund_request_from_order")
REPLAYS = os.path.join(BATCH, "replays")

APP = "webarena_shopping_mock"
ENV = "CUA_GYM_WEBARENA_SHOPPING_URL"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

AN_528 = (
    "Fill out the contact us form with this refund message for the phone screen "
    "protector bought March 2023: \"I need a refund. Order: <order_id>. Amount: "
    "<amount>. Reason: It broke after three days of use.\" Leave the filled form "
    "ready for review and do not submit it. Fill in the order id and amount "
    "information from my order history."
)
AN_653 = (
    "Fill the \"contact us\" form in the site for a refund on the phone screen "
    "protector I bought, stating that \"it broke after just three days of use\". "
    "Also, ensure to include the order number #000000180 and the product SKU. You "
    "need to find the product SKU form the order. Don\"t submit yet, I will check."
)
AN_654 = (
    "Fill the \"contact us\" form in the site for a refund on the bluetooth speaker "
    "I bought, stating that \"it broke after just three days of use\". Also, ensure "
    "to include the order number #161 and the product SKU. You need to find the "
    "product SKU from the order. Don\"t submit yet, I will check."
)
AN_657 = (
    "Fill the \"contact us\" form in the site for a refund on the speaker I bought, "
    "stating that \"it broke after just three days of use\". Also, ensure to include "
    "the order number #148 and the product SKU. You need to find the product SKU "
    "from the order. Don\"t submit yet, I will check."
)
AN_532 = (
    "Fill out the contact us form with this refund message for the PS3 remote "
    "controller bought early 2023: \"I need a refund. Order: <order_id>. Amount: "
    "<amount>. Reason: It broke after three days of use.\" Leave the filled form "
    "ready for review and do not submit it. Fill in the order id and amount "
    "information from my order history."
)
AN_320 = (
    "How much refund I should expect from my order cancelled in Feb 2023, "
    "including shipping fee"
)
AN_321 = (
    "How much refund I should expect from all my order cancelled in 2022, "
    "including shipping fee"
)
AN_333 = (
    "How much did I spend on shopping at One Stop Market on November 2022? They "
    "gave me a 20% discount on the total amount for orders exceeding $200 in cash"
)
AN_146 = "What is the size configuration of the picture frame I bought Sep 2022"

DEVIATION = (
    "Deliberate deviation from the cited analogues: they say \"do not submit\". "
    "ContactPage.jsx:17-21 keeps the typed values in React useState and only "
    "submitContact (AppContext.jsx:495) persists anything, so an unsubmitted form "
    "is invisible to /go and unscorable in our state-only reward channel. This "
    "task therefore requires an actual Submit. The retrieval half is unchanged."
)


# --------------------------------------------------------------------------
# task definitions
# --------------------------------------------------------------------------

def content(name, weight, kind, values, describe):
    return {"name": name, "weight": weight, "kind": kind, "values": values,
            "describe": describe}


TASKS = [
    {
        "id": "refund_request_from_order_may_2022_poster_frame_001",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R2", "R9", "A7", "A2"],
        "chain": "filter the order grid to May 2022 -> open that order and read its "
                 "increment id, grand total and the poster-frame line's SKU -> compose "
                 "the three values into a refund message -> submit the Contact Us form",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_528, AN_653],
        "instruction": (
            "The poster frames from my only May 2022 order arrived warped. Send One "
            "Stop Market a refund request through Contact Us quoting that order's "
            "full number, its grand total and the frame line's SKU, callback "
            "4155550188."
        ),
        "phone": "4155550188",
        "rows": 1,
        "components": [
            content("comment_quotes_order_number", 0.25, "token", ["000000181"],
                    "the May 2022 order's increment id 000000181"),
            content("comment_quotes_grand_total", 0.25, "amount", ["298.65"],
                    "that order's grand total 298.65"),
            content("comment_quotes_frame_sku", 0.25, "token", ["B0015ZYB9K"],
                    "the DAX poster frame line's SKU B0015ZYB9K"),
        ],
        "setup": None,
        "notes": [
            "Target resolution: 2022-05 holds exactly one order, 000000181 "
            "(src/data/orders.json), so \"my only May 2022 order\" is unique. Month "
            "buckets are timezone-safe; day buckets are not (utils/format.js:4).",
            "\"Poster Frame\" matches exactly one line across all 37 seeded orders "
            "(B0015ZYB9K in 000000181), checked by scanning every order item name.",
            DEVIATION,
        ],
        "replay_target": ("000000181", 4),
    },
    {
        "id": "refund_request_from_order_canceled_july_2022_chair_002",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R2", "R9", "A7", "A2"],
        "chain": "filter the order grid to July 2022 and pick the canceled row -> open "
                 "it and read the increment id, grand total and the dining-chair line's "
                 "SKU -> compose them into the message -> submit Contact Us",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_653, AN_320],
        "instruction": (
            "I want the cancellation from July 2022 refunded properly. Message "
            "Contact Us with that order's full number, its grand total and the SKU of "
            "the dining chair on it, and leave 4155550241 as my number."
        ),
        "phone": "4155550241",
        "rows": 1,
        "components": [
            content("comment_quotes_order_number", 0.25, "token", ["000000149"],
                    "the canceled July 2022 order 000000149"),
            content("comment_quotes_grand_total", 0.25, "amount", ["354.66"],
                    "that order's grand total 354.66"),
            content("comment_quotes_chair_sku", 0.25, "token", ["B07DB4R43W"],
                    "the Christopher Knight dining chair SKU B07DB4R43W"),
        ],
        "setup": None,
        "notes": [
            "Target resolution: 2022-07 holds 000000167 (complete) and 000000149 "
            "(canceled), so status disambiguates to 000000149 with no tie.",
            "Only one line on 000000149 is a dining chair (B07DB4R43W); the other "
            "three are a bluetooth speaker, linen pants and a bikini set.",
            DEVIATION,
        ],
        "replay_target": ("000000149", 3),
    },
    {
        "id": "refund_request_from_order_sep_2022_tshirt_options_003",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R2", "R9", "A7", "A2"],
        "chain": "filter the order grid to September 2022 -> open the order holding the "
                 "Mickey Mouse t-shirt and read its increment id, that line's SKU and "
                 "its rendered Color/Size options -> compose all four values -> submit "
                 "Contact Us",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_146, AN_653],
        "instruction": (
            "The Mickey Mouse t-shirt from my September 2022 order came in the wrong "
            "size. Contact Us about it, quoting the full order number, that line's "
            "SKU and the colour and size I ordered. Callback 4155550143."
        ),
        "phone": "4155550143",
        "rows": 1,
        "components": [
            content("comment_quotes_order_number", 0.25, "token", ["000000175"],
                    "the September 2022 order 000000175"),
            content("comment_quotes_shirt_sku", 0.25, "token", ["B07JJJRJQP"],
                    "the Disney Mickey Mouse t-shirt SKU B07JJJRJQP"),
            content("comment_quotes_colour_and_size", 0.25, "token",
                    ["Silver", "Small"],
                    "the line's rendered options Color=Silver and Size=Small"),
        ],
        "setup": None,
        "notes": [
            "Target resolution: \"Mickey\" matches exactly one line in the whole "
            "order corpus - B07JJJRJQP in 000000175 - so the September qualifier and "
            "the product name agree.",
            "The options come from OrderViewPage.jsx:28-31, which renders "
            "items[].options as a dl.item-options; that line carries Color=Silver, "
            "Fit Type=Women, Size=Small.",
            DEVIATION,
        ],
        "replay_target": ("000000175", 3),
    },
    {
        "id": "refund_request_from_order_november_2022_spend_004",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R2", "R3", "R1", "A7"],
        "chain": "filter the order grid to November 2022 -> sum that month's order "
                 "totals and pick its dearest and cheapest rows -> compose the three "
                 "derived values into a Contact Us message and submit it",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_333, AN_321],
        "instruction": (
            "I'm querying my November 2022 spending with One Stop Market. Send a "
            "Contact Us message stating the combined grand total of that month's "
            "orders plus the full order numbers of the dearest and cheapest of them."
        ),
        "phone": None,
        "rows": 1,
        "components": [
            content("comment_quotes_month_total", 0.25, "amount", ["403.18"],
                    "the November 2022 combined grand total 403.18"),
            content("comment_quotes_dearest_order", 0.25, "token", ["000000164"],
                    "the dearest November order 000000164"),
            content("comment_quotes_cheapest_order", 0.25, "token", ["000000183"],
                    "the cheapest November order 000000183"),
        ],
        "setup": None,
        "notes": [
            "November 2022 holds exactly three orders: 000000183 $51.94, 000000171 "
            "$133.07, 000000164 $218.17. Sum 403.18. Dearest margin 218.17 vs 133.07 "
            "and cheapest margin 51.94 vs 133.07 - no tie at either end.",
            "Grand totals already include the $5-per-item flat rate "
            "(utils/orders.js:9-11), so the figure is the amount actually charged.",
            DEVIATION,
        ],
        "replay_target": ("000000164", 2),
    },
    {
        "id": "refund_request_from_order_injected_april_2023_005",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R2", "R9", "A7", "A2"],
        "chain": "filter the order grid to April 2023 -> open the single order there "
                 "and read its increment id, grand total and the SKU of the line whose "
                 "Ordered qty is 2 -> compose them -> submit Contact Us",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_528, AN_657],
        "instruction": (
            "My April 2023 order turned up damaged. Write to Contact Us with that "
            "order's full number, its grand total and the SKU of the item I bought two "
            "of. My callback number is 4155550176."
        ),
        "phone": "4155550176",
        "rows": 1,
        "components": [
            content("comment_quotes_order_number", 0.25, "token", ["000000190"],
                    "the injected April 2023 order 000000190"),
            content("comment_quotes_grand_total", 0.25, "amount", ["64.97"],
                    "that order's grand total 64.97"),
            content("comment_quotes_double_qty_sku", 0.25, "token", ["B0049UKKP2"],
                    "the SKU of the only line with qtyOrdered 2"),
        ],
        "setup": "april",
        "injected": [
            "orders[] gains 000000190 (entityId 190) dated 2023-04-18 12:00:00Z, "
            "status/state complete/complete, two lines itemId 900/901 on real "
            "products 13806 and 22562. April 2023 is empty in the pristine seed, so "
            "the whole temporal filter has no answer without it and the correct "
            "answer cannot be memorised from the frozen seed.",
            "nextOrderEntityId and nextOrderIncrementId bumped to 191 so a later "
            "placeOrder cannot mint a duplicate id.",
        ],
        "notes": [
            "Injected row obeys the census checklist: createdAt later than the "
            "page-1 cutoff, UTC clock pinned to 12:00:00 so America/New_York cannot "
            "shift the calendar day, entityId 190 with both counters bumped, line "
            "itemIds 900/901 above the seeded max 544, real productIds, coherent "
            "(complete, complete) pair, shippingAmount 15 == 5 * totalQtyOrdered 3 "
            "and grandTotal 64.97 == subtotal 49.97 + 15.",
            "Only one of the two lines has qtyOrdered 2, so \"the item I bought two "
            "of\" is unique by construction.",
            DEVIATION,
        ],
        "replay_target": ("000000190", 1),
    },
    {
        "id": "refund_request_from_order_injected_on_hold_may_2023_006",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R2", "R9", "A7", "A2"],
        "chain": "scan May 2023 in the order grid for the row whose Status reads On "
                 "Hold -> open it and read its increment id, grand total and the SKU of "
                 "its dearest line -> compose them -> submit Contact Us",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_654, AN_320],
        "instruction": (
            "One of my May 2023 orders is sitting On Hold. Chase it through Contact "
            "Us, quoting that order's full number, its grand total and the SKU of its "
            "most expensive line. Callback 4155550164."
        ),
        "phone": "4155550164",
        "rows": 1,
        "components": [
            content("comment_quotes_order_number", 0.25, "token", ["000000191"],
                    "the injected On Hold order 000000191"),
            content("comment_quotes_grand_total", 0.25, "amount", ["162.98"],
                    "that order's grand total 162.98"),
            content("comment_quotes_dearest_line_sku", 0.25, "token", ["B07Z6CFMS8"],
                    "the dearest line's SKU B07Z6CFMS8"),
        ],
        "setup": "onhold",
        "injected": [
            "orders[] gains 000000191 (entityId 191) dated 2023-05-10 12:00:00Z with "
            "status \"On Hold\" and state \"holded\". Emma's seeded history holds "
            "only complete/canceled/pending, so the status predicate has no answer "
            "without it; On Hold is a stock Magento status and statusLabel() "
            "(utils/format.js:64-67) renders the pre-cased string verbatim.",
            "nextOrderEntityId and nextOrderIncrementId bumped to 192.",
        ],
        "notes": [
            "May 2023 already holds three pending orders and one canceled one, so the "
            "status predicate genuinely has to be applied rather than eyeballed.",
            "Dearest line margin is $108.00 vs $19.99 - no tie. Invariants held: "
            "totalQtyOrdered 3, shippingAmount 15, grandTotal 162.98 == 147.98 + 15.",
            "\"Out for delivery\" was NOT used: it is not a stock Magento status and "
            "official 093/099 exist because the gold answer is \"there is none\".",
            DEVIATION,
        ],
        "replay_target": ("000000191", 1),
    },
    {
        "id": "refund_request_from_order_followup_feb_2023_lamp_007",
        "style": "explicit",
        "difficulty": "hard",
        "skills": ["R2", "R9", "A7", "A2"],
        "chain": "filter the order grid to the canceled February 2023 table-lamp order "
                 "-> open it and read the increment id, grand total and the lamp line's "
                 "SKU -> compose a follow-up message carrying all three -> submit it as "
                 "a second Contact Us entry",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_653, AN_528],
        "instruction": (
            "I contacted One Stop Market a while ago about the table lamp order from "
            "February 2023 that ended up cancelled, and nobody has come back to me. "
            "Please send a follow-up through the Contact Us page. In the message quote "
            "the full order number exactly as the order page prints it, the grand "
            "total charged for that order, and the SKU of the table lamp line itself; "
            "you will have to open the order from My Orders to read the SKU. Put "
            "4155550157 in the Phone Number field, leave the Name and Email boxes as "
            "the form prefills them, and submit the form once."
        ),
        "phone": "4155550157",
        "rows": 2,
        "components": [
            content("comment_quotes_order_number", 0.25, "token", ["000000158"],
                    "the canceled February 2023 order 000000158"),
            content("comment_quotes_grand_total", 0.25, "amount", ["174.99"],
                    "that order's grand total 174.99"),
            content("comment_quotes_lamp_sku", 0.25, "token", ["B072XS3F6W"],
                    "the Hugh table lamp SKU B072XS3F6W"),
        ],
        "setup": "followup",
        "injected": [
            "contactSubmissions[] pre-seeded with one earlier message dated "
            "2023-05-20 that mentions the February table lamp in prose but carries no "
            "order number, no amount and no SKU. This turns the errand into a "
            "follow-up (the census's shape 29) and makes the scored row the SECOND "
            "entry, so the pristine-seed answer of \"write a first message\" is not "
            "the task. Nothing in the rubric is pre-satisfied: the injected row is "
            "index 0 and the reward reads index 1 of a two-row collection.",
        ],
        "notes": [
            "Two canceled orders contain a table lamp - 000000158 (Feb 2023) and "
            "000000170 (May 2023) - so the February qualifier is load-bearing and is "
            "stated in both the injected prior message and the instruction.",
            "Explicit style: the ordering (open the order before writing) and the "
            "prefill rule are spelled out because an unguided reading could send the "
            "message without the SKU.",
            DEVIATION,
        ],
        "replay_target": ("000000158", 1),
    },
    {
        "id": "refund_request_from_order_march_2023_pair_total_008",
        "style": "explicit",
        "difficulty": "hard",
        "skills": ["R2", "R3", "A7", "A2"],
        "chain": "filter the order grid to March 2023 -> add the two order totals "
                 "together -> compose both increment ids and the combined figure into "
                 "one Contact Us message and submit it",
        "hard_criteria": ["derived_target", "cross_page"],
        "analogues": [AN_321, AN_333],
        "instruction": (
            "Both of the orders I placed in March 2023 went wrong and I want them "
            "dealt with together. Open the Contact Us page and send one single message "
            "that quotes the full order number of each of those two March 2023 orders "
            "and the combined amount I paid across the pair, shipping included. The "
            "order history grid shows the order totals, and the shipping charge is "
            "already inside them. Put 4155550208 in the Phone Number field, leave Name "
            "and Email as the form prefills them, and submit once."
        ),
        "phone": "4155550208",
        "rows": 1,
        "components": [
            content("comment_quotes_first_order", 0.25, "token", ["000000166"],
                    "March 2023 order 000000166"),
            content("comment_quotes_second_order", 0.25, "token", ["000000180"],
                    "March 2023 order 000000180"),
            content("comment_quotes_combined_total", 0.25, "amount", ["83.31"],
                    "the combined March 2023 total 83.31"),
        ],
        "setup": None,
        "notes": [
            "March 2023 holds exactly two orders, 000000166 ($17.99) and 000000180 "
            "($65.32); 17.99 + 65.32 = 83.31. Both grand totals already include "
            "shipping (taxAmount and discountAmount are 0 on all 37 seeded orders), "
            "so \"shipping included\" is derivable rather than a second sum.",
            "Timezone note: 000000166 stores 2023-03-11 02:01:11 UTC and renders "
            "3/10/23, but it stays inside March either way, so the month bucket is "
            "safe. No day-level fact is used.",
            DEVIATION,
        ],
        "replay_target": ("000000180", 1),
    },
    {
        "id": "refund_request_from_order_named_order_kneeling_chair_009",
        "style": "terse",
        "difficulty": "medium",
        "skills": ["R9", "A7"],
        "chain": "open the named order 000000161 and read the kneeling-chair line's SKU "
                 "and the order's grand total -> carry both into a Contact Us message "
                 "and submit it",
        "hard_criteria": None,
        "analogues": [AN_654, AN_653],
        "instruction": (
            "Order 000000161's kneeling chair was misdescribed. Send a Contact Us "
            "refund request quoting that line's SKU and the order's grand total, with "
            "4155550132 as my callback number."
        ),
        "phone": "4155550132",
        "rows": 1,
        "components": [
            content("comment_quotes_chair_sku", 0.3, "token", ["B099TZT2XR"],
                    "the Varier kneeling chair SKU B099TZT2XR"),
            content("comment_quotes_grand_total", 0.3, "amount", ["762.18"],
                    "order 000000161's grand total 762.18"),
        ],
        "message_weight": 0.4,
        "setup": None,
        "notes": [
            "Medium, honestly: the order is named outright, so there is no temporal "
            "filter - one attribute lookup (R9) feeding one composed writeback (A7).",
            "\"Kneeling\" matches exactly one line across all 37 orders "
            "(B099TZT2XR in 000000161).",
            DEVIATION,
        ],
        "replay_target": ("000000161", 1),
    },
    {
        "id": "refund_request_from_order_june_2022_grid_total_010",
        "style": "terse",
        "difficulty": "medium",
        "skills": ["R2", "A7"],
        "chain": "page the order grid back to June 2022 to find the single order there "
                 "-> read its increment id and order total straight off the row -> "
                 "carry both into a Contact Us message and submit it",
        "hard_criteria": None,
        "analogues": [AN_320, AN_532],
        "instruction": (
            "My only June 2022 order was never refunded after it was cancelled. Send a "
            "Contact Us message quoting that order's full number and the order total "
            "shown for it."
        ),
        "phone": None,
        "rows": 1,
        "components": [
            content("comment_quotes_order_number", 0.3, "token", ["000000182"],
                    "the June 2022 order 000000182"),
            content("comment_quotes_order_total", 0.3, "amount", ["173.56"],
                    "the order total 173.56 shown on the grid row"),
        ],
        "message_weight": 0.4,
        "setup": None,
        "notes": [
            "Medium: both values render on the order history grid row itself, so the "
            "chain is one temporal filter (R2) feeding one composed writeback (A7) "
            "with no drill-in.",
            "2022-06 holds exactly one order, 000000182, and it is canceled - the "
            "premise and the uniqueness both hold.",
            "000000182 is row 31 of 37, so the agent must use the pager or the "
            "\"Show N per page\" limiter; both render real controls "
            "(OrderHistoryPage.jsx:75-85).",
            DEVIATION,
        ],
        "replay_target": ("000000182", 4),
    },
]


# --------------------------------------------------------------------------
# shared code fragments
# --------------------------------------------------------------------------

HELPERS = '''

def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _digits(value):
    return re.sub(r"[^0-9]", "", _text(value))


def _rows(state):
    rows = state.get("contactSubmissions")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _target_row(state):
    rows = _rows(state)
    if len(rows) != EXPECTED_ROW_COUNT:
        return None
    return rows[EXPECTED_ROW_COUNT - 1]


def _has_token(haystack, needle):
    pattern = r"(?<![0-9A-Za-z])" + re.escape(needle) + r"(?![0-9A-Za-z])"
    return re.search(pattern, haystack, re.IGNORECASE) is not None


def _has_amount(haystack, needle):
    pattern = r"(?<![0-9.])" + re.escape(needle) + r"(?![0-9])"
    return re.search(pattern, haystack) is not None


def _checks(state):
    row = _target_row(state)
    comment = _text(row.get("comment")) if isinstance(row, dict) else ""
    submitted = (
        isinstance(row, dict)
        and comment != ""
        and _text(row.get("name")) != ""
        and _text(row.get("email")) != ""
    )
    if submitted and REQUIRED_PHONE_DIGITS is not None:
        submitted = _digits(row.get("telephone")) == REQUIRED_PHONE_DIGITS
    results = {MESSAGE_COMPONENT: submitted}
    for name in CONTENT_TOKENS:
        results[name] = all(_has_token(comment, v) for v in CONTENT_TOKENS[name])
    for name in CONTENT_AMOUNTS:
        results[name] = all(_has_amount(comment, v) for v in CONTENT_AMOUNTS[name])
    return results
'''

EVAL_TAIL = '''

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

NEMO_TAIL = '''

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
        state = response.json().get("current_state") or {}
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


MESSAGE_COMPONENT_NAME = "refund_message_submitted"


def weights_block(task):
    msg_weight = task.get("message_weight", 0.25)
    lines = ["COMPONENT_WEIGHTS = {",
             '    "%s": %s,' % (MESSAGE_COMPONENT_NAME, msg_weight)]
    for comp in task["components"]:
        lines.append('    "%s": %s,' % (comp["name"], comp["weight"]))
    lines.append("}")
    return "\n".join(lines)


def constants_block(task):
    tokens = {c["name"]: c["values"] for c in task["components"] if c["kind"] == "token"}
    amounts = {c["name"]: c["values"] for c in task["components"] if c["kind"] == "amount"}
    phone = task["phone"]
    out = []
    out.append("MESSAGE_COMPONENT = \"%s\"" % MESSAGE_COMPONENT_NAME)
    out.append("EXPECTED_ROW_COUNT = %d" % task["rows"])
    if phone is None:
        out.append("REQUIRED_PHONE_DIGITS = None")
    else:
        out.append("REQUIRED_PHONE_DIGITS = \"%s\"" % phone)
    out.append("CONTENT_TOKENS = json.loads(r\"\"\"%s\"\"\")"
               % json.dumps(tokens, indent=1))
    out.append("CONTENT_AMOUNTS = json.loads(r\"\"\"%s\"\"\")"
               % json.dumps(amounts, indent=1))
    return "\n".join(out)


def criteria_prose(task):
    lines = []
    phone = task["phone"]
    if task["rows"] == 1:
        lines.append(
            "  * state.contactSubmissions holds exactly one row, with a non-empty "
            "comment, name and email"
            + (" and telephone %s." % phone if phone else ".")
        )
    else:
        lines.append(
            "  * state.contactSubmissions holds exactly %d rows and the last one has a "
            "non-empty comment, name and email" % task["rows"]
            + (" and telephone %s." % phone if phone else ".")
        )
    for comp in task["components"]:
        lines.append("  * that row's comment quotes %s." % comp["describe"])
    return "\n".join(lines)


def reward_source(task):
    doc = (
        '"""Deterministic reward for %s.\n\n'
        "Success criteria, all read from the persisted contact-form record that\n"
        "submitContact (AppContext.jsx:495) writes:\n\n%s\n\n"
        "Every value scored here is derived from the order history by the agent; none\n"
        "of them appears in the instruction, so an agent that skipped the retrieval\n"
        "cannot score. Only current browser state is inspected.\n"
        '"""\n'
    ) % (task["id"], criteria_prose(task))
    parts = [doc, "\nimport json\nimport re\n\n",
             constants_block(task), "\n\n", weights_block(task),
             "\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n",
             HELPERS, EVAL_TAIL]
    return "".join(parts)


def nemo_reward_source(task):
    doc = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Implements exactly the rubric of reward.py, reading the current state from\n"
        "GET /go?sid=... instead of a frozen evidence bundle, and printing\n"
        "REWARD: <float> on every output path including the error path.\n\n"
        "Self-contained: standard library plus requests, which is present in\n"
        "cuagym/requirements.txt.\n"
        '"""\n'
    ) % task["id"]
    parts = [
        doc,
        "\nimport json\nimport re\nimport sys\n\nimport requests\n\n",
        'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % PLACEHOLDER,
        constants_block(task), "\n\n", weights_block(task),
        "\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n",
        HELPERS, NEMO_TAIL,
    ]
    return "".join(parts)


# --------------------------------------------------------------------------
# initial_setup programs
# --------------------------------------------------------------------------

SETUP_HEAD = '''"""NeMo-Gym setup program for %s.

%s

The pristine session document is read back from /go first and patched in place,
so every one of the mock's fifteen persisted top-level keys survives the write
and the /go baseline equals the current state afterwards.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%s"

'''

SETUP_TAIL = '''

def verify():
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: baseline and current state disagree", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    read = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    read.raise_for_status()
    body = read.json()
    state = body.get("current_state") or body.get("initial_state") or {}
    if not isinstance(state, dict) or not state:
        print("SETUP FAILED: could not read the pristine state", file=sys.stderr)
        raise SystemExit(1)
    state = patch(state)
    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()
    verify()


main()
'''

APRIL_ORDER = {
    "entityId": 190,
    "incrementId": "000000190",
    "status": "complete",
    "state": "complete",
    "createdAt": "2023-04-18 12:00:00",
    "grandTotal": 64.97,
    "subtotal": 49.97,
    "shippingAmount": 15,
    "taxAmount": 0,
    "discountAmount": 0,
    "totalQtyOrdered": 3,
    "shippingDescription": "Flat Rate - Fixed",
    "customerEmail": "emma.lopez@gmail.com",
    "shippingMethod": "flatrate_flatrate",
    "paymentMethod": "checkmo",
    "paymentTitle": "Check / Money order",
    "billingAddress": {
        "firstname": "Emma", "lastname": "Lopez", "street": "101 S San Mateo Dr",
        "city": "San Mateo", "region": "California", "postcode": "94010",
        "country_id": "US", "telephone": "6505551212", "company": None, "email": None,
    },
    "shippingAddress": {
        "firstname": "Emma", "lastname": "Lopez", "street": "101 S San Mateo Dr",
        "city": "San Mateo", "region": "California", "postcode": "94010",
        "country_id": "US", "telephone": "6505551212", "company": None, "email": None,
    },
    "items": [
        {"itemId": 900, "productId": 13806, "sku": "B09PMKP5YS",
         "name": "Goose Creek Meadow Orchid Large 3-Wick Candle",
         "price": 19.99, "qtyOrdered": 1, "rowTotal": 19.99,
         "productType": "simple", "options": []},
        {"itemId": 901, "productId": 22562, "sku": "B0049UKKP2",
         "name": "Japanese Green Tea (100 Tea Bags)",
         "price": 14.99, "qtyOrdered": 2, "rowTotal": 29.98,
         "productType": "simple", "options": []},
    ],
}

ONHOLD_ORDER = {
    "entityId": 191,
    "incrementId": "000000191",
    "status": "On Hold",
    "state": "holded",
    "createdAt": "2023-05-10 12:00:00",
    "grandTotal": 162.98,
    "subtotal": 147.98,
    "shippingAmount": 15,
    "taxAmount": 0,
    "discountAmount": 0,
    "totalQtyOrdered": 3,
    "shippingDescription": "Flat Rate - Fixed",
    "customerEmail": "emma.lopez@gmail.com",
    "shippingMethod": "flatrate_flatrate",
    "paymentMethod": "checkmo",
    "paymentTitle": "Check / Money order",
    "billingAddress": {
        "firstname": "Emma", "lastname": "Lopez", "street": "101 S San Mateo Dr",
        "city": "San Mateo", "region": "California", "postcode": "94010",
        "country_id": "US", "telephone": "6505551212", "company": None, "email": None,
    },
    "shippingAddress": {
        "firstname": "Emma", "lastname": "Lopez", "street": "101 S San Mateo Dr",
        "city": "San Mateo", "region": "California", "postcode": "94010",
        "country_id": "US", "telephone": "6505551212", "company": None, "email": None,
    },
    "items": [
        {"itemId": 910, "productId": 27193, "sku": "B07Z6CFMS8",
         "name": "Reyn Spooner Deep Sea Jive Hawaiian Aloha Shirt",
         "price": 108, "qtyOrdered": 1, "rowTotal": 108,
         "productType": "simple",
         "options": [{"label": "Size", "value": "Large"}]},
        {"itemId": 911, "productId": 6516, "sku": "B0912T6WWG",
         "name": "Tweezers For Succulents Duo",
         "price": 19.99, "qtyOrdered": 2, "rowTotal": 39.98,
         "productType": "simple", "options": []},
    ],
}

PRIOR_CONTACT = {
    "name": "Emma Lopez",
    "email": "emma.lopez@gmail.com",
    "telephone": "",
    "comment": (
        "I wrote to you last week about the table lamp I ordered in February that "
        "ended up cancelled, and I have still had no reply. Please can somebody look "
        "at this."
    ),
    "submittedAt": "2023-05-20 14:02:11",
}


def order_setup_source(task_id, purpose, order, next_id):
    fixture = json.dumps(order, indent=1)
    body = (
        'INJECTED_ORDER = json.loads(r"""%s""")\n\n'
        "NEXT_ID = %d\n\n\n"
        "def patch(state):\n"
        "    orders = state.get(\"orders\")\n"
        "    if not isinstance(orders, list):\n"
        "        orders = []\n"
        "    keep = [o for o in orders\n"
        "            if not (isinstance(o, dict)\n"
        "                    and o.get(\"incrementId\") == INJECTED_ORDER[\"incrementId\"])]\n"
        "    state[\"orders\"] = keep + [INJECTED_ORDER]\n"
        "    state[\"nextOrderEntityId\"] = NEXT_ID\n"
        "    state[\"nextOrderIncrementId\"] = NEXT_ID\n"
        "    return state\n"
    ) % (fixture, next_id)
    return (SETUP_HEAD % (task_id, purpose, PLACEHOLDER)) + body + SETUP_TAIL


def contact_setup_source(task_id, purpose, row):
    fixture = json.dumps(row, indent=1)
    body = (
        'PRIOR_SUBMISSION = json.loads(r"""%s""")\n\n\n'
        "def patch(state):\n"
        "    state[\"contactSubmissions\"] = [PRIOR_SUBMISSION]\n"
        "    return state\n"
    ) % fixture
    return (SETUP_HEAD % (task_id, purpose, PLACEHOLDER)) + body + SETUP_TAIL


SETUPS = {
    "april": lambda tid: order_setup_source(
        tid,
        "April 2023 is empty in the pristine seed, so the task's temporal filter has\n"
        "no answer without this row. One complete order 000000190 dated\n"
        "2023-04-18 12:00:00Z is appended, with the UTC clock pinned to midday so the\n"
        "America/New_York render cannot shift its calendar day, entityId 190 above the\n"
        "seeded maximum, line itemIds 900/901 above the seeded maximum 544, real\n"
        "catalog productIds, and the seed invariants shippingAmount == 5 *\n"
        "totalQtyOrdered and grandTotal == subtotal + shippingAmount preserved. Both\n"
        "next-order counters are bumped so a later placeOrder cannot mint a duplicate.",
        APRIL_ORDER, 191),
    "onhold": lambda tid: order_setup_source(
        tid,
        "Emma's seeded history holds only complete, canceled and pending orders, so a\n"
        "task that selects by an On Hold status has no answer without this row. On\n"
        "Hold is a stock Magento status and statusLabel (utils/format.js:64-67) only\n"
        "capitalises the first character, so the label is written pre-cased. Same\n"
        "checklist as every injected order: midday UTC clock, entityId above the\n"
        "seeded maximum, line itemIds above 544, real productIds, coherent\n"
        "status/state pair, and both shipping and grand-total invariants preserved.",
        ONHOLD_ORDER, 192),
    "followup": lambda tid: contact_setup_source(
        tid,
        "contactSubmissions is empty on the pristine seed, so \"chase up the message I\n"
        "already sent\" is not expressible. One earlier submission is injected. It\n"
        "names the February table lamp in prose only - no order number, no amount, no\n"
        "SKU - so it cannot pre-satisfy any part of the rubric, and the reward scores\n"
        "the SECOND row of a two-row collection.",
        PRIOR_CONTACT),
}


# --------------------------------------------------------------------------
# replay drafts
# --------------------------------------------------------------------------

REPLAY = '''"""Golden replay DRAFT for %(tid)s.

Click-only: the landing page is the only URL opened. Every later page is reached
through a rendered link or form control.

  /  -> header "My Account" -> account nav "My Orders" -> order grid
     -> (limiter "Show 50 per page" when the target row is not on page 1)
     -> the target row's "View Order" link
     -> footer "Contact Us" -> fill the form -> Submit

Values the agent must READ, recorded here only so a reviewer can check the
replay against the rubric:
%(values)s
"""

from playwright.sync_api import sync_playwright

MESSAGE = %(message)r
PHONE = %(phone)r


def run(page, base_url):
    page.goto(base_url + "/")

    # 1. account area
    page.click("text=My Account")
    page.click("a:has-text('My Orders')")

    # 2. widen the grid so every one of the 37 rows renders, then read the target
    page.select_option("#order-limiter", "50")
    row = page.locator("#my-orders-table tbody tr", has_text=%(order)r)
    row.wait_for()
%(open_order)s
    # 3. contact form, reached from the footer link that renders on every page
    page.click("footer a:has-text('Contact Us')")
    page.fill("#telephone", PHONE) if PHONE else None
    page.fill("#comment", MESSAGE)
    page.click("button.action.submit.primary")
    page.wait_for_selector(".message")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        run(page, "http://localhost:8004")
        browser.close()


if __name__ == "__main__":
    main()
'''

OPEN_ORDER = """    row.locator("a.action.view").click()
    # the order view renders the line table with a SKU column the grid never has
    page.wait_for_selector("#my-orders-table th.col.sku")

"""

NO_OPEN = """
"""


REPLAY_MESSAGES = {
    "refund_request_from_order_may_2022_poster_frame_001":
        "I need a refund. Order: 000000181. Amount: $298.65. SKU: B0015ZYB9K. The "
        "poster frames arrived warped.",
    "refund_request_from_order_canceled_july_2022_chair_002":
        "Please refund my cancelled order 000000149, grand total $354.66. The dining "
        "chair on it is SKU B07DB4R43W.",
    "refund_request_from_order_sep_2022_tshirt_options_003":
        "Order 000000175, SKU B07JJJRJQP. I ordered Color Silver in Size Small and the "
        "shirt that arrived is the wrong size.",
    "refund_request_from_order_november_2022_spend_004":
        "Query on my November 2022 spending: the three orders come to $403.18 in "
        "total. The dearest was 000000164 and the cheapest was 000000183.",
    "refund_request_from_order_injected_april_2023_005":
        "My April order 000000190 arrived damaged. Grand total $64.97. The item I "
        "bought two of is SKU B0049UKKP2.",
    "refund_request_from_order_injected_on_hold_may_2023_006":
        "Order 000000191 is still On Hold. Grand total $162.98. Its most expensive "
        "line is SKU B07Z6CFMS8. Please release or refund it.",
    "refund_request_from_order_followup_feb_2023_lamp_007":
        "Following up on my earlier message: order 000000158, grand total $174.99, "
        "table lamp SKU B072XS3F6W. It was cancelled and I have had no reply.",
    "refund_request_from_order_march_2023_pair_total_008":
        "Both my March 2023 orders went wrong: 000000166 and 000000180. Together they "
        "came to $83.31 including shipping. Please deal with them as one case.",
    "refund_request_from_order_named_order_kneeling_chair_009":
        "Refund request for the kneeling chair on order 000000161, SKU B099TZT2XR. The "
        "order's grand total was $762.18.",
    "refund_request_from_order_june_2022_grid_total_010":
        "My June 2022 order 000000182 was cancelled and never refunded. The order "
        "total shown is $173.56.",
}


def replay_source(task):
    order, _page = task["replay_target"]
    values = "\n".join(
        "  - %s" % c["describe"] for c in task["components"]
    )
    needs_open = any(
        "SKU" in c["describe"] or "options" in c["describe"]
        for c in task["components"]
    )
    return REPLAY % {
        "tid": task["id"],
        "values": values,
        "message": REPLAY_MESSAGES[task["id"]],
        "phone": task["phone"] or "",
        "order": order,
        "open_order": OPEN_ORDER if needs_open else NO_OPEN,
    }


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def success_criteria(task):
    out = []
    phone = task["phone"]
    if task["rows"] == 1:
        out.append(
            "contactSubmissions holds exactly one submitted record whose name, email "
            "and comment are non-empty"
            + (" and whose telephone is %s" % phone if phone else "")
        )
    else:
        out.append(
            "contactSubmissions holds exactly %d records and the second one has "
            "non-empty name, email and comment" % task["rows"]
            + (" plus telephone %s" % phone if phone else "")
        )
    for comp in task["components"]:
        out.append("that record's comment quotes %s" % comp["describe"])
    return out


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    nemo_lines = []

    for task in TASKS:
        tid = task["id"]
        bundle = os.path.join(SITE, tid)
        os.makedirs(bundle, exist_ok=True)

        reward = reward_source(task)
        nemo_reward = nemo_reward_source(task)
        setup = SETUPS[task["setup"]](tid) if task["setup"] else None

        write(os.path.join(bundle, "reward.py"), reward)
        write(os.path.join(bundle, "nemo_reward.py"), nemo_reward)
        if setup is not None:
            write(os.path.join(bundle, "initial_setup.py"), setup)

        instruction_doc = {
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP,
            "start_path": "/",
            "difficulty": task["difficulty"],
            "success_criteria": success_criteria(task),
        }
        write(os.path.join(bundle, "task_instruction.json"),
              json.dumps(instruction_doc, indent=2, ensure_ascii=False) + "\n")

        metadata = {
            "style": task["style"],
            "difficulty": task["difficulty"],
            "shape": "retrieval_writeback",
            "skills": task["skills"],
            "skill_chain": task["chain"],
            "official_analogues": task["analogues"],
            "topic": "shopping storefront refund request from order history",
            "inspiration_ids": [
                "webarena-528", "webarena-532", "webarena-653", "webarena-654",
                "webarena-657", "webarena-320", "webarena-321", "webarena-333",
                "webarena-146",
            ],
            "authoring_notes": task["notes"],
        }
        if task["hard_criteria"]:
            metadata["hard_criteria"] = task["hard_criteria"]
        if task.get("injected"):
            metadata["injected_preconditions"] = task["injected"]

        manifest = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
            "apps": [{
                "name": APP,
                "source_name": "shopping",
                "base_url_env": ENV,
                "start_path": "/",
                "initial_state": None,
                "golden_state": None,
            }],
            "source_evaluator": {},
            "reward_path": "reward.py",
            "requirements_path": None,
            "evidence": [],
            "source": "webarena",
            "metadata": metadata,
        }
        write(os.path.join(bundle, "task.json"),
              json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

        row = {
            "task_payload": {
                "task_id": tid,
                "dataset": "cuagym",
                "dataset_version": "v1",
                "sites": [APP],
                "start_urls": [],
                "intent": task["instruction"],
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": None,
                    "note": "unused - CUA-Gym reward code is authoritative",
                },
                "cuagym": {
                    "bundle_id": tid,
                    "app_dir": APP,
                    "initial_setup": setup,
                    "eval_reward_code": nemo_reward,
                },
            }
        }
        write(os.path.join(bundle, "nemo_task.json"),
              json.dumps(row, indent=2, ensure_ascii=False) + "\n")
        nemo_lines.append(json.dumps(row, ensure_ascii=False))

        write(os.path.join(REPLAYS, tid + ".py"), replay_source(task))
        index["tasks"].append({"task_id": tid, "path": tid + "/task.json"})

    write(os.path.join(BATCH, "index.json"),
          json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    write(os.path.join(BATCH, "nemo_tasks.jsonl"), "\n".join(nemo_lines) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()

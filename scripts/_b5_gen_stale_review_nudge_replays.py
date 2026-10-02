#!/usr/bin/env python3
"""Emit the click-only golden replay DRAFTS for batch-5 lane 10 (gitlab)."""
import pathlib

BATCH = pathlib.Path("/home/ubuntu/CUA-Gym/output/tasks/gitlab/_batches/stale_review_nudge")
REPLAYS = BATCH / "replays"

HEADER = '''#!/usr/bin/env python3
"""Golden replay DRAFT for {task_id}.

TASK4 S6: click-reachability. The only `goto` is the landing page named by
`start_path` ("/"); everything after it is a rendered link, button or form
control. No URL is constructed.

Run shape (the verification harness supplies `page` and `sid`):

    from playwright.sync_api import sync_playwright
    ...
    run(page, sid)

Reward expectation: 0.0 before `run`, 1.0 after.
"""
BASE = "http://localhost:8001"

COMMENT_FIELD = "[data-qa-selector='comment_field']"
COMMENT_BUTTON = "[data-qa-selector='comment_button']"
MR_COUNTER = "a.dashboard-shortcuts-merge_requests"
SORT_TOGGLE = ".sort-dropdown-container [data-testid='base-dropdown-toggle']"
SORT_DIRECTION = ".sort-dropdown-container a[title='Sort direction']"
ROW_TITLE = "[data-qa-selector='issuable_title_link']"
ROW_COMMENTS = "[data-testid='issuable-comments']"


def _settle(page):
    page.wait_for_timeout(900)


def land(page, sid):
    """The one permitted navigation: start_path, with the session id."""
    page.goto(BASE + "/?sid=" + sid, wait_until="networkidle")
    _settle(page)


def open_mr_dashboard(page, which):
    """`which` is 'Assigned to you' or 'Review requests for you'."""
    page.click(MR_COUNTER)          # the counter toggles its own dropdown
    _settle(page)
    page.click("a:has-text('%s')" % which)
    _settle(page)


def sort_by_updated(page, ascending):
    page.click(SORT_TOGGLE)
    _settle(page)
    page.click(".sort-dropdown-container a.dropdown-item:has-text('Updated date')")
    _settle(page)
    if ascending:
        page.click(SORT_DIRECTION)   # Updated date defaults to updated_desc
        _settle(page)


def open_row(page, index):
    page.locator(ROW_TITLE).nth(index).click()
    _settle(page)


def post_comment(page, body):
    page.fill(COMMENT_FIELD, body)
    page.click(COMMENT_BUTTON)
    _settle(page)


'''

FIND_PROJECT = '''
def open_project_merge_requests(page, needle, project_link_text):
    """Reach a project's merge-request list from the navbar search form."""
    page.click("#search")
    page.fill("#search", needle)
    page.keyboard.press("Enter")     # the search box is a real <form>
    _settle(page)
    page.click("a:has-text('%s')" % project_link_text)
    _settle(page)
    page.click(".nav-sidebar a:has-text('Merge requests')")
    _settle(page)

'''

TASKS = {
    "stale_review_nudge_assigned_open_stalest_nudge_001": '''
BODY = "Any update on this? @davepgreene"


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Assigned to you")
    # Default state tab is Open; three rows (!1270, !1485, !40).
    sort_by_updated(page, ascending=True)
    # Row 0 is byteblaze/a11y-webring.club!40, updated 2023-03-27 23:14:48.4197.
    assert "Add verification functions" in page.locator(ROW_TITLE).nth(0).inner_text()
    open_row(page, 0)
    post_comment(page, BODY)
''',
    "stale_review_nudge_review_queue_stalest_bump_002": '''
BODY = "Bumping this for review. @jimbateson"


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Review requests for you")
    sort_by_updated(page, ascending=True)
    # Row 0 is a11yproject/a11yproject.com!1472, updated 2023-03-23 07:43:13.800501.
    assert "accessible nav" in page.locator(ROW_TITLE).nth(0).inner_text()
    open_row(page, 0)
    post_comment(page, BODY)
''',
    "stale_review_nudge_review_queue_freshest_pickup_003": '''
BODY = "Picking this up next. @aguscha333"


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Review requests for you")
    sort_by_updated(page, ascending=False)   # Updated date, newest first
    # Row 0 is a11yproject/a11yproject.com!1270, updated 2023-03-27 23:21:22.709901.
    assert "WCAG levels" in page.locator(ROW_TITLE).nth(0).inner_text()
    open_row(page, 0)
    post_comment(page, BODY)
''',
    "stale_review_nudge_review_queue_quietest_offer_004": '''
BODY = "Happy to look at this - anything blocking? @mxmason"


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Review requests for you")
    # Five open rows; IssuablesList.jsx:822 renders each row's user_notes_count.
    counts = [int(t.strip() or "0") for t in page.locator(ROW_COMMENTS).all_inner_texts()]
    assert sorted(counts) == [1, 17, 22, 26, 50], counts
    quietest = counts.index(min(counts))
    assert "focus edge cases" in page.locator(ROW_TITLE).nth(quietest).inner_text()
    open_row(page, quietest)
    post_comment(page, BODY)
''',
    "stale_review_nudge_conditional_thanks_stalest_review_005": '''
BODY = "Thank you"


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Review requests for you")
    sort_by_updated(page, ascending=True)
    open_row(page, 0)                        # !1472, opened by @jimbateson
    # The timeline is oldest-first by default, so the newest comment is last.
    last = page.locator("li.note-wrapper .note-headline-light").last.inner_text()
    assert "@jimbateson" in last, last       # injected note 900101 -> Thank-you arm
    post_comment(page, BODY)
''',
    "stale_review_nudge_conditional_reminder_busiest_assigned_006": '''
BODY = "@aguscha333"


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Assigned to you")
    counts = [int(t.strip() or "0") for t in page.locator(ROW_COMMENTS).all_inner_texts()]
    assert sorted(counts) == [0, 0, 17], counts
    busiest = counts.index(max(counts))
    assert "WCAG levels" in page.locator(ROW_TITLE).nth(busiest).inner_text()
    open_row(page, busiest)                  # !1270, opened by @aguscha333
    last = page.locator("li.note-wrapper .note-headline-light").last.inner_text()
    assert "@mxmason" in last, last          # injected note 900201 -> tag-the-author arm
    post_comment(page, BODY)
''',
    "stale_review_nudge_own_open_mr_status_note_007": '''
BODY = "Still relevant - rebasing this week."


def run(page, sid):
    land(page, sid)
    page.click("#search")                    # focuses the navbar search dropdown
    _settle(page)
    page.click("#default-mrs-created")
    _settle(page)
    # author_username=byteblaze + the default Open tab leaves exactly one row.
    assert page.locator(ROW_TITLE).count() == 1
    assert "color utility classes" in page.locator(ROW_TITLE).nth(0).inner_text()
    open_row(page, 0)
    post_comment(page, BODY)
''',
    "stale_review_nudge_primer_design_stalest_open_chase_008": '''
BODY = "This one has gone stale - is it still wanted? @JoshBowdenConcepts"


def run(page, sid):
    land(page, sid)
    open_project_merge_requests(page, "design", "primer / design")
    sort_by_updated(page, ascending=True)
    # setup moved !450's updated_at to 2021-08-11, ahead of !191's 2021-12-10.
    assert "Octovisuals Page" in page.locator(ROW_TITLE).nth(0).inner_text()
    open_row(page, 0)
    post_comment(page, BODY)
''',
    "stale_review_nudge_review_queue_two_oldest_ping_009": '''
BODY = "Ping - this is still in my review queue."


def run(page, sid):
    land(page, sid)
    open_mr_dashboard(page, "Review requests for you")
    sort_by_updated(page, ascending=True)
    titles = page.locator(ROW_TITLE).all_inner_texts()
    assert "accessible nav" in titles[0] and "Pitfalls" in titles[1], titles[:2]

    open_row(page, 0)                                    # !1472 -> @jimbateson
    post_comment(page, BODY + " @jimbateson")

    page.go_back()                                       # back to the clicked list
    _settle(page)
    open_row(page, 1)                                    # !1490 -> @erikkroes
    post_comment(page, BODY + " @erikkroes")
''',
    "stale_review_nudge_primer_design_reviewed_but_stalled_010": '''
BODY = "Reviewer assigned but no movement - can we close the loop? @langermank"


def run(page, sid):
    land(page, sid)
    open_project_merge_requests(page, "design", "primer / design")

    # Reviewer = Any, built through the filtered-search token bar.
    page.click(".gl-filtered-search-token-segment, input.gl-filtered-search-term-input")
    _settle(page)
    page.click("li:has-text('Reviewer')")
    _settle(page)
    page.click("li:has-text('=')")
    _settle(page)
    page.click("li:has-text('Any')")
    _settle(page)
    page.click(".gl-search-box-by-click-search-button")
    _settle(page)

    sort_by_updated(page, ascending=True)
    # Eleven open rows carry a reviewer; oldest-updated is !294 (2023-01-31).
    assert "Single page component docs" in page.locator(ROW_TITLE).nth(0).inner_text()
    open_row(page, 0)
    post_comment(page, BODY)
''',
}

NEEDS_PROJECT = {
    "stale_review_nudge_primer_design_stalest_open_chase_008",
    "stale_review_nudge_primer_design_reviewed_but_stalled_010",
}


def main():
    REPLAYS.mkdir(parents=True, exist_ok=True)
    for task_id, body in TASKS.items():
        text = HEADER.format(task_id=task_id)
        if task_id in NEEDS_PROJECT:
            text += FIND_PROJECT
        text += body
        (REPLAYS / (task_id + ".py")).write_text(text, encoding="utf-8")
        print("wrote", task_id)


main()

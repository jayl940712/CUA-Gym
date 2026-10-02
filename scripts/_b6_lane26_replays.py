#!/usr/bin/env python3
"""Writes the golden-replay DRAFTS for batch-6 lane 26 (reddit R9 -> A1)."""

import os

LANE = "/home/ubuntu/CUA-Gym/output/tasks/reddit/_batches/named_own_post_body_line"
REPLAYS = os.path.join(LANE, "replays")

HOST_TEMPLATE = '''"""Golden replay DRAFT for {task_id}.

Click-only from "/": the nav search box finds my own submission, the result
card shows the source site next to the title (Submission.jsx:146-148 ->
displayHost), and the card's Edit link opens the author-only edit form where
the body is set to the credit line naming that site.

Retrieval step: the host is READ off the page, never typed from memory.
"""

import re

SEARCH = {search!r}
CARD_TEXT = {card_text!r}
EXPECTED_HOST = {host!r}
BODY = {body!r}


async def run(lane, task):
    page = lane.page("reddit")

    # Site-wide search from the nav bar (present on "/").
    box = page.get_by_label("Search query")
    await box.click()
    await box.fill(SEARCH)
    await box.press("Enter")
    await page.wait_for_url(re.compile(r"/search"))

    card = page.locator("article.submission").filter(has_text=CARD_TEXT).first
    await card.wait_for(state="visible")

    # RETRIEVAL: the source site rendered beside the title.
    host = (await card.locator(".submission__host").first.inner_text()).strip()
    assert host == EXPECTED_HOST, host

    # ACTION: the author-only edit form, body set to the credit line.
    await card.get_by_role("link", name="Edit").click()
    await page.wait_for_url(re.compile(r"/edit(\\?|$)"))

    body_field = page.get_by_label("Body")
    await body_field.fill("Source: " + host if BODY.startswith("Source:") else "Credit: " + host)

    await page.get_by_role("button", name="Edit submission").click()
    await page.get_by_text("The submission was edited.").wait_for(state="visible")
'''

TOPCOMMENT_TEMPLATE = '''"""Golden replay DRAFT for {task_id}.

Click-only from "/": the nav search box finds my own submission, the card's
comment-count link opens the post, the first rendered comment is the
highest-scored top-level one (Comment.jsx:23-33 sorts netScore DESC, id ASC),
and its author name is written into the post body through the author-only
edit form.

Retrieval step: the username is READ off the comment listing, never typed
from memory.
"""

import re

SEARCH = {search!r}
CARD_TEXT = {card_text!r}
EXPECTED_AUTHOR = {author!r}
PREFIX = {prefix!r}


async def run(lane, task):
    page = lane.page("reddit")

    box = page.get_by_label("Search query")
    await box.click()
    await box.fill(SEARCH)
    await box.press("Enter")
    await page.wait_for_url(re.compile(r"/search"))

    card = page.locator("article.submission").filter(has_text=CARD_TEXT).first
    await card.wait_for(state="visible")

    # Open the post itself via the comment-count link (the title link is
    # external for this user's submissionLinkDestination preference).
    await card.get_by_role("link", name=re.compile(r"comment", re.I)).click()
    await page.wait_for_url(re.compile(r"/f/\\w+/\\d+/"))

    # RETRIEVAL: the first comment on the page is the top-scored one.
    first_comment = page.locator("article.comment, .comment").first
    await first_comment.wait_for(state="visible")
    author = (await first_comment.locator("a.comment__author, .comment__author")
              .first.inner_text()).strip()
    assert author == EXPECTED_AUTHOR, author

    # ACTION: the author-only edit form on this same submission.
    await page.get_by_role("link", name="Edit").first.click()
    await page.wait_for_url(re.compile(r"/edit(\\?|$)"))

    body_field = page.get_by_label("Body")
    await body_field.fill(PREFIX + author)

    await page.get_by_role("button", name="Edit submission").click()
    await page.get_by_text("The submission was edited.").wait_for(state="visible")
'''

URL_TEMPLATE = '''"""Golden replay DRAFT for named_own_post_body_line_secret_invasion_link_fix_009.

Starts on the target submission's own permalink and navigates by clicking
only. The nav search box returns exactly the two "Secret Invasion"
submissions, both mine; the Samuel L. Jackson one supplies the address (read
out of its own edit form's URL field), and the June 21 one receives it.

Retrieval step: the address is READ out of the other post, never typed from
memory.
"""

import re

EXPECTED_URL = "https://www.vanityfair.com/hollywood/2023/03/secret-invasion-marvel-exclusive"


async def run(lane, task):
    page = lane.page("reddit")

    box = page.get_by_label("Search query")
    await box.click()
    await box.fill("Secret Invasion")
    await box.press("Enter")
    await page.wait_for_url(re.compile(r"/search"))

    # RETRIEVAL: the Samuel L. Jackson interview post -> its stored URL.
    source_card = page.locator("article.submission").filter(
        has_text="Samuel L. Jackson").first
    await source_card.wait_for(state="visible")
    await source_card.get_by_role("link", name="Edit").click()
    await page.wait_for_url(re.compile(r"/135204/.*/edit"))
    url_value = await page.get_by_label("URL").input_value()
    assert url_value.strip() == EXPECTED_URL, url_value

    # Back to the search results (a page reached by clicking), then the target.
    await page.go_back()
    await page.wait_for_url(re.compile(r"/search"))

    target_card = page.locator("article.submission").filter(
        has_text="Premieres June 21").first
    await target_card.wait_for(state="visible")
    await target_card.get_by_role("link", name="Edit").click()
    await page.wait_for_url(re.compile(r"/135185/.*/edit"))

    # ACTION: point the June 21 post at the same article.
    url_field = page.get_by_label("URL")
    await url_field.fill(url_value.strip())

    await page.get_by_role("button", name="Edit submission").click()
    await page.get_by_text("The submission was edited.").wait_for(state="visible")
'''

HOSTS = [
    ("named_own_post_body_line_umbrella_academy_source_host_001",
     "David Cross Joins the Final Season of 'The Umbrella Academy'",
     "Umbrella Academy", "deadline.com", "Source: deadline.com"),
    ("named_own_post_body_line_sue_baker_obit_source_host_002",
     "Sue Baker Dies at 67", "Sue Baker", "theguardian.com",
     "Credit: theguardian.com"),
    ("named_own_post_body_line_last_of_us_posters_source_host_003",
     "The Last of Us Character Posters", "Character Posters",
     "bloody-disgusting.com", "Source: bloody-disgusting.com"),
    ("named_own_post_body_line_grogu_short_source_host_004",
     "Zen - Grogu and Dust Bunnies", "Grogu", "ign.com", "Source: ign.com"),
]

TOPCOMMENTS = [
    ("named_own_post_body_line_flower_moon_top_comment_005",
     "Killers of the Flower Moon", "Killers of the Flower Moon",
     "Xenomorph_kills", "Top comment by "),
    ("named_own_post_body_line_dead_to_me_top_comment_006",
     "TVLine Performer of the Week: Christina Applegate", "Christina Applegate",
     "mikexmachina", "Best comment: "),
    ("named_own_post_body_line_wilko_johnson_top_comment_007",
     "Wilko Johnson", "Wilko Johnson", "BordersRanger01", "Top comment by "),
    ("named_own_post_body_line_tokyo_vice_top_comment_008",
     "Tokyo Vice Season 2", "Tokyo Vice", "SprinklesCharming382", "Best comment: "),
    ("named_own_post_body_line_orlando_brown_top_comment_010",
     "Orlando Brown Arrested", "Orlando Brown", "callmemacready", "Top comment by "),
]


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    for task_id, search, card_text, host, body in HOSTS:
        with open(os.path.join(REPLAYS, task_id + ".py"), "w") as fh:
            fh.write(HOST_TEMPLATE.format(task_id=task_id, search=search,
                                          card_text=card_text, host=host, body=body))
    for task_id, search, card_text, author, prefix in TOPCOMMENTS:
        with open(os.path.join(REPLAYS, task_id + ".py"), "w") as fh:
            fh.write(TOPCOMMENT_TEMPLATE.format(task_id=task_id, search=search,
                                                card_text=card_text, author=author,
                                                prefix=prefix))
    with open(os.path.join(
            REPLAYS, "named_own_post_body_line_secret_invasion_link_fix_009.py"), "w") as fh:
        fh.write(URL_TEMPLATE)
    print("wrote 10 replay drafts")


if __name__ == "__main__":
    main()

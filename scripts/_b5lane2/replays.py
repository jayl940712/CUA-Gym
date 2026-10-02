# -*- coding: utf-8 -*-
"""Golden-replay drafts for batch-5 lane 2 (gitlab / grant_access_top_repos)."""
import os

OUT = "/home/ubuntu/CUA-Gym/output/tasks/gitlab/_batches/grant_access_top_repos/replays"

HEADER = '''"""Golden replay DRAFT for {task_id}.

Click-only: the episode lands on `/` and every later page is reached by
clicking a rendered link or button. No page.goto() after the landing, no URL
construction, no go_back() to a page that was never navigated to by a click
({back_note}).

Route used throughout:
    /  ->  project row link on the dashboard "Your projects" list
       ->  sidebar "Project information" (lands on /activity)
       ->  sidebar child "Members"       (/-/project_members)
       ->  "Invite members" / the row's Max-role dropdown / "Remove member"

Sidebar sub-items are hidden until the section's own link is clicked; hovering
does not reveal them, so the two-click gesture above is mandatory.
"""


BYTEBLAZE_REPOS = [
    "a11y-webring.club",
    "remove-board-movement-events-from-the-github-issue-timeline",
    "ericwbailey.website",
    "empathy-prompts",
    "gimmiethat.space",
    "accessible-html-content-patterns",
    "a11y-syntax-highlighting",
    "millennials-to-snake-people",
    "solarized-prism-theme",
    "cloud-to-butt",
    "timeit",
    "dotfiles",
]


def read_commit_counts(page):
    """Rank byteblaze's own repos the way the task asks: open each overview and
    read the `N Commits` figure out of the project-stats row."""
    counts = {{}}
    for name in BYTEBLAZE_REPOS:
        page.click('a[href="/byteblaze/%s"]' % name)
        page.wait_for_selector("nav.project-stats")
        raw = page.inner_text("nav.project-stats li:first-child .project-stat-value")
        counts[name] = int(raw.replace(",", "").strip())
        page.go_back()
        page.wait_for_selector('a[href="/byteblaze/dotfiles"]')
    return counts


def open_members(page, repo):
    """/ -> project -> Project information -> Members."""
    page.click('a[href="/byteblaze/%s"]' % repo)
    page.click("a.shortcuts-project-information")
    page.wait_for_url("**/activity")
    page.click("#js-onboarding-members-link")
    page.wait_for_selector('[data-testid="members-table"]')


def back_to_dashboard(page):
    """Return to `/` the way we came: three clicked pages back."""
    page.go_back()
    page.go_back()
    page.go_back()
    page.wait_for_selector('a[href="/byteblaze/dotfiles"]')


def invite(page, usernames, role_value, expires=None):
    page.click('[data-qa-selector="invite_members_button"]')
    page.wait_for_selector("#invite-members-search")
    for username in usernames:
        page.fill("#invite-members-search", username)
        page.click('.dropdown-menu.show .dropdown-item:has-text("@%s")' % username)
    page.select_option("#invite-members-role", role_value)
    if expires:
        page.fill("#invite-members-expires", expires)
    page.click('[data-qa-selector="invite_button"]')
    page.wait_for_selector('[data-qa-selector="invite_button"]', state="detached")


def set_role(page, username, role_label):
    page.click('button[aria-label="Change role of %s"]' % username)
    page.click('.dropdown-menu.show button[data-qa-selector="access_level_link"]'
               ':has-text("%s")' % role_label)


def remove_member(page, username):
    row = 'tr[data-username="%s"]' % username
    page.click('%s [data-qa-selector="delete_member_button"]' % row)
    page.click('.modal-footer button.btn-danger:has-text("Remove member")')
    page.wait_for_selector(row, state="detached")


def run(page):
{body}
'''


def emit(task_id, back_note, body):
    with open(os.path.join(OUT, task_id + ".py"), "w") as fh:
        fh.write(HEADER.format(task_id=task_id, back_note=back_note, body=body))


BACK = "page.go_back() only ever retraces a link this replay clicked"

emit("grant_access_top_repos_001", BACK, '''    counts = read_commit_counts(page)
    top3 = [r for r, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:3]]
    # ericwbailey.website 1615, dotfiles 552, accessible-html-content-patterns 188
    assert set(top3) == {"ericwbailey.website", "dotfiles",
                         "accessible-html-content-patterns"}, top3
    for repo in top3:
        open_members(page, repo)
        invite(page, ["vinta", "lahwaacz"], "30")
        back_to_dashboard(page)
''')

emit("grant_access_top_repos_002", BACK, '''    counts = read_commit_counts(page)
    bottom3 = [r for r, _ in sorted(counts.items(), key=lambda kv: kv[1])[:3]]
    # gimmiethat.space 3, solarized-prism-theme 7, remove-board-... 8
    assert set(bottom3) == {
        "gimmiethat.space", "solarized-prism-theme",
        "remove-board-movement-events-from-the-github-issue-timeline"}, bottom3
    for repo in bottom3:
        open_members(page, repo)
        invite(page, ["davepgreene"], "40")
        back_to_dashboard(page)
''')

emit("grant_access_top_repos_003", BACK, '''    # The private repos are the dashboard rows carrying the lock visibility icon:
    # accessible-html-content-patterns, solarized-prism-theme, gimmiethat.space.
    counts = read_commit_counts(page)
    private = ["accessible-html-content-patterns", "solarized-prism-theme",
               "gimmiethat.space"]
    target = max(private, key=lambda r: counts[r])
    assert target == "accessible-html-content-patterns", target
    open_members(page, target)
    invite(page, ["yjlou"], "20")
''')

emit("grant_access_top_repos_004", BACK, '''    counts = read_commit_counts(page)
    bottom3 = [r for r, _ in sorted(counts.items(), key=lambda kv: kv[1])[:3]]
    assert set(bottom3) == {
        "gimmiethat.space", "solarized-prism-theme",
        "remove-board-movement-events-from-the-github-issue-timeline"}, bottom3
    for repo in bottom3:
        open_members(page, repo)
        already = page.query_selector('tr[data-username="abisubramanya27"]')
        if already:
            # solarized-prism-theme: seeded Guest, so the invite picker will not
            # offer him. Raise the Max role in place instead.
            set_role(page, "abisubramanya27", "Developer")
        else:
            invite(page, ["abisubramanya27"], "30")
        back_to_dashboard(page)
''')

emit("grant_access_top_repos_005", BACK, '''    counts = read_commit_counts(page)
    ordered = [r for r, _ in sorted(counts.items(), key=lambda kv: -kv[1])]
    second = ordered[1]
    assert second == "dotfiles", second
    open_members(page, second)
    invite(page, ["a11yproject", "westurner"], "20")
''')

emit("grant_access_top_repos_006", BACK, '''    counts = read_commit_counts(page)
    public = [r for r in BYTEBLAZE_REPOS if r not in (
        "accessible-html-content-patterns", "solarized-prism-theme",
        "gimmiethat.space")]
    top3 = sorted(public, key=lambda r: -counts[r])[:3]
    # ericwbailey.website 1615, dotfiles 552, empathy-prompts 150
    assert set(top3) == {"ericwbailey.website", "dotfiles", "empathy-prompts"}, top3
    for repo in top3:
        open_members(page, repo)
        invite(page, ["convexegg", "patrickhlauke", "westurner"], "20",
               expires="2024-06-30")
        back_to_dashboard(page)
''')

emit("grant_access_top_repos_007", BACK, '''    counts = read_commit_counts(page)
    target = min(counts, key=lambda r: counts[r])
    assert target == "gimmiethat.space", target
    open_members(page, target)
    # Guest is the modal's default; select it explicitly so the replay is exact.
    invite(page, ["lahwaacz"], "10")
''')

emit("grant_access_top_repos_008", BACK, '''    # Find the one repo of mine where yjlou holds a membership, and read his role.
    target = None
    role = None
    for repo in BYTEBLAZE_REPOS:
        open_members(page, repo)
        row = page.query_selector('tr[data-username="yjlou"]')
        if row:
            target = repo
            role = row.query_selector("td.col-max-role").inner_text().strip()
            break
        back_to_dashboard(page)
    assert target == "gimmiethat.space", target
    assert role == "Developer", role
    remove_member(page, "yjlou")
    invite(page, ["lahwaacz"], "30")
''')

emit("grant_access_top_repos_009", BACK, '''    counts = read_commit_counts(page)
    top3 = [r for r, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:3]]
    assert set(top3) == {"ericwbailey.website", "dotfiles",
                         "accessible-html-content-patterns"}, top3
    for repo in top3:
        open_members(page, repo)
        already = page.query_selector('tr[data-username="lahwaacz"]')
        if already:
            # dotfiles: the injected Reporter row, promoted in place.
            set_role(page, "lahwaacz", "Maintainer")
        else:
            invite(page, ["lahwaacz"], "40")
        back_to_dashboard(page)
''')

emit("grant_access_top_repos_010", BACK, '''    counts = read_commit_counts(page)
    ordered = [r for r, _ in sorted(counts.items(), key=lambda kv: -kv[1])]
    source, target = ordered[0], ordered[1]
    assert (source, target) == ("ericwbailey.website", "dotfiles"), (source, target)

    # Read who has what on the source project.
    open_members(page, source)
    wanted = []
    for row in page.query_selector_all('tr[data-qa-selector="member_row"]'):
        username = row.get_attribute("data-username")
        label = row.query_selector("td.col-max-role").inner_text().strip()
        if username != "byteblaze":
            wanted.append((username, label))
    assert sorted(wanted) == [("vinta", "Developer"), ("westurner", "Reporter")], wanted
    back_to_dashboard(page)

    open_members(page, target)
    levels = {"Guest": "10", "Reporter": "20", "Developer": "30",
              "Maintainer": "40", "Owner": "50"}
    for username, label in wanted:
        invite(page, [username], levels[label])
''')

print("wrote 10 replay drafts")

#!/usr/bin/env python3
"""Batch-6 lane 3 (gitlab, R9 -> A12) bundle writer.

Authoring helper only: it emits the ten bundles under
output/tasks/gitlab/<task_id>/ plus the lane's GENERATION.md, index.json,
nemo_tasks.jsonl and replay drafts. It runs no validation.
"""
import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/gitlab")
BATCH = os.path.join(OUT, "_batches/named_issue_assign_due")
REPLAYS = os.path.join(BATCH, "replays")

CURRENT_USER = (
    '{"id": 2330, "username": "byteblaze", "name": "Byte Blaze", '
    '"email": "ericwbailey@fakegithub.com", "state": "active", '
    '"created_at": "2023-03-23 07:30:04.033203", "location": "Boston, MA", '
    '"organization": "@github ", '
    '"bio": "Inclusive design and accessibility advocate. Accessibility and design systems wonk for @primer.", '
    '"followers": 2, "following": 3, "feed_token": "TMN_bBn9Z48qVbUFZV45", "status": null}'
)

ANALOGUE = {
    "a11y": 'Create an issue in a11yproject repo with title "401 bad gateway". Assign the issue to Roshanjossey (you can invite users to the project if needed). Set due date to be the end of 2030',
    "empathy": 'Create an issue in my empathy-prompts repo with title "Integrating LLMs for better prompts". Assign the issue to Roshanjossey (you can invite users to the project if needed). Set due date to be the beginning of Q2 2033',
    "dotfiles": 'Create an issue in my dotfiles repo with title "add support for oh-my-zsh". Assign the issue to Abishek (you can invite users to the project if needed). Set due date to be July 18 2033',
    "c2b": 'Create an issue in cloud-to-butt repo with title "Let\'s keep the project alive". Assign the issue to myself (you can invite users to the project if needed). Set due date to be the end of Q1 2033. Stay on the page after clicking on Create issue.',
    "a11y2": 'Create an issue in a11yproject repo with title "404 for many URLs". Assign the issue to myself (you can invite users to the project if needed). Set due date to be 2030-1-3. Stay on the page after clicking on Create issue.',
    "projid": "Get the project ID(s) of my personal project(s) that received more than 100 stars",
    "gimmie": "Get the usernames of other users who have access to my repo gimmiethat.space",
    "prism": "Get the usernames of other users who have access to my repo prism-theme",
    "assign_rohan": "Assign the issue regarding linking to an accessibility statement in a11y-webring.club to Rohan.",
    "primer_reviewer": "Submit a merge request for dialog-component in the current repository to be merged into dialog branch, assign Primer as the reviewer",
}


def member(mid, source_id, user_id, level, label, created_at, created_by):
    return {
        "id": mid,
        "source_type": "project",
        "source_id": source_id,
        "user_id": user_id,
        "access_level": level,
        "access_label": label,
        "created_at": created_at,
        "expires_at": None,
        "created_by_id": created_by,
    }


MILLENNIALS_EDIT = {
    "187": {
        "id": 187,
        "full_path": "byteblaze/millennials-to-snake-people",
        "path": "millennials-to-snake-people",
        "name": "millennials-to-snake-people",
        "namespace": {"id": 2505, "path": "byteblaze", "name": "Byte Blaze", "kind": "user"},
        "description": "\U0001f40d Chrome extension that replaces occurrences of 'Millennials' with 'Snake People'",
        "visibility": "public",
        "star_count": 6,
        "forks_count": 0,
        "archived": False,
        "created_at": "2023-03-27 20:33:53.647975",
        "last_activity_at": "2023-03-27 20:33:53.647975",
        "default_branch": "master",
        "commit_count": 137,
        "repo_size": 812345,
        "open_issues_count": 4,
        "closed_issues_count": 4,
        "open_mrs_count": 2,
        "merged_mrs_count": 17,
        "closed_mrs_count": 10,
        "auto_devops_quick_link": True,
    }
}


TASKS = [
    {
        "id": "named_issue_assign_due_dotfiles_project_id_001",
        "style": "terse",
        "project_id": 193,
        "full_path": "byteblaze/dotfiles",
        "instruction": (
            'My dotfiles repo needs a restore rehearsal scheduled. File an issue there titled '
            '"Restore drill for project N", where N is that repository\'s own numeric project ID, '
            'assign it to me, and set the due date to 30 June 2033.'
        ),
        "display_title": "Restore drill for project 193",
        "titles": ["Restore drill for project 193"],
        "assignee_id": 2330,
        "assignee": "Byte Blaze (@byteblaze)",
        "due": "2033-06-30",
        "derived": "the project ID 193, rendered as 'Project ID: 193' on the project overview (ProjectOverview.jsx:297)",
        "chain": "read the numeric project ID off byteblaze/dotfiles' overview -> create an issue in that repo carrying the ID in its title, assigned to byteblaze and due 2033-06-30",
        "analogues": [ANALOGUE["dotfiles"], ANALOGUE["projid"]],
        "inspiration_ids": ["webarena-660", "webarena-168"],
        "derived_from": None,
        "setup": None,
        "injections": [],
        "notes": [
            "Project ID is unique per project, so there is no tie to break: 193 is the only value byteblaze/dotfiles renders.",
            "dotfiles holds zero seeded issues (issues_index.json), so the created issue gets iid 1 and the Issues page shows the empty-state 'New issue' button (IssuablesList.jsx:862).",
            "No initial_setup: pristine newIssues is empty, so the untouched lane scores 0.0.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/byteblaze/dotfiles']", "project overview renders 'Project ID: 193'"),
        ],
        "assign_mode": "me",
        "assign_query": None,
    },
    {
        "id": "named_issue_assign_due_empathy_prompts_newest_tag_002",
        "style": "terse",
        "project_id": 183,
        "full_path": "byteblaze/empathy-prompts",
        "instruction": (
            'empathy-prompts needs release notes. Open an issue there titled '
            '"Release notes since T", where T is the name of the repository\'s most recent tag, '
            'assign it to Roshan Jossy, and set the due date to 15 May 2033.'
        ),
        "display_title": "Release notes since v0.3.0",
        "titles": ["Release notes since v0.3.0"],
        "assignee_id": 2264,
        "assignee": "Roshan Jossy (@Roshanjossey)",
        "due": "2033-05-15",
        "derived": "the newest tag name v0.3.0, top row of the Tags page (Tags.jsx:54 default sort updated_desc)",
        "chain": "read the newest tag off byteblaze/empathy-prompts' Tags page -> create an issue in that repo whose title carries the tag name, assigned to Roshan Jossy and due 2033-05-15",
        "analogues": [ANALOGUE["empathy"]],
        "inspiration_ids": ["webarena-659"],
        "derived_from": None,
        "setup": {"repo": {"tagOverlay": {"byteblaze/empathy-prompts": [
            {"name": "v0.3.0", "sha": "3d54c962", "date": "2019-11-08T14:22:10-05:00",
             "message": "Prompt deck refresh"}]}}},
        "injections": [
            "repo.tagOverlay['byteblaze/empathy-prompts'] gains one tag v0.3.0 dated 2019-11-08, in the {name, sha, date, message} shape src/data/tags.json uses and getTags() merges (dataManager.js:571). Without it the answer is the frozen v0.1.0, which is memorisable from the seed; with it the correct answer is the injected tag and the agent has to actually read the Tags page.",
            "Tie margin: v0.3.0 (2019-11-08) vs v0.1.0 (2017-05-18) is 2 years 5 months on the default updated_desc sort, and the overview stat row now reads '2 Tags'.",
        ],
        "notes": [
            "The injection touches only repo.tagOverlay; the rubric reads newIssues only, so nothing is pre-satisfied.",
            "empathy-prompts already has 15 issues, so the issue list renders normally and 'New issue' is the header button (IssuablesList.jsx:191).",
        ],
        "retrieval_steps": [
            ("click", "a[href='/byteblaze/empathy-prompts']", "project overview"),
            ("click", "a.shortcuts-tree", "Repository section opens on /-/tree/main"),
            ("click", "a:has-text('Tags')", "Tags page: v0.3.0 is the first row"),
        ],
        "assign_mode": "search",
        "assign_query": "Roshan",
        "assign_username": "Roshanjossey",
    },
    {
        "id": "named_issue_assign_due_a11yproject_branch_count_003",
        "style": "explicit",
        "project_id": 174,
        "full_path": "a11yproject/a11yproject.com",
        "instruction": (
            "The a11yproject.com repository has collected a lot of branches and I want a cleanup "
            "ticket on the books before the content freeze. Starting from the GitLab landing page, "
            "find a11yproject/a11yproject.com and read how many branches it currently has - the "
            "count sits on the project overview's stats row, between Commits and Tags. Then open a "
            "new issue on that same project titled \"Audit N branches before the freeze\", "
            "substituting the number you read for N, assign the issue to me (Byte Blaze), and give "
            "it a due date of 31 January 2034. Leave the repository's existing issues and branches "
            "exactly as they are."
        ),
        "display_title": "Audit 17 branches before the freeze",
        "titles": ["Audit 17 branches before the freeze"],
        "assignee_id": 2330,
        "assignee": "Byte Blaze (@byteblaze)",
        "due": "2034-01-31",
        "derived": "the branch count 17, rendered as '17 Branches' on the overview stats row (ProjectOverview.jsx:352)",
        "chain": "read the branch count off a11yproject/a11yproject.com's overview -> create an issue in that repo whose title carries the count, assigned to byteblaze and due 2034-01-31",
        "analogues": [ANALOGUE["a11y2"], ANALOGUE["a11y"]],
        "inspiration_ids": ["webarena-809", "webarena-658"],
        "derived_from": None,
        "setup": {"repo": {"branchOverlay": {"a11yproject/a11yproject.com": [
            {"name": "chore/upgrade-eleventy", "sha": "ed37a2f2",
             "subject": "Bump eleventy to 2.0", "committed_date": "2023-03-20T10:04:11-04:00"},
            {"name": "fix/skip-link-focus", "sha": "35b52ef0",
             "subject": "Restore skip-link focus outline", "committed_date": "2023-03-21T08:12:45-04:00"}]}}},
        "injections": [
            "repo.branchOverlay['a11yproject/a11yproject.com'] gains two branches in the {name, sha, subject, committed_date} shape src/data/by-project/174.json uses and getBranches() merges (dataManager.js:557), so the rendered count moves 15 -> 17 and the answer is not memorisable from the frozen seed.",
            "Neither injected name collides with the 15 seeded branches, so the de-duplicating filter at dataManager.js:566 keeps both and the count is exactly 17.",
        ],
        "notes": [
            "17 is a single rendered integer with no competing reading: the Branches page lists the same set and carries no separate total.",
            "The injection writes only repo.branchOverlay; the rubric reads newIssues, so nothing is pre-satisfied.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/a11yproject/a11yproject.com']", "overview stats row reads '17 Branches'"),
        ],
        "assign_mode": "me",
        "assign_query": None,
    },
    {
        "id": "named_issue_assign_due_cloud_to_butt_head_sha_004",
        "style": "terse",
        "project_id": 189,
        "full_path": "byteblaze/cloud-to-butt",
        "instruction": (
            'cloud-to-butt needs a regression ticket. Open an issue there titled '
            '"Regression triage from S", where S is the 8-character short SHA of its default '
            "branch's latest commit, assign it to Primer, and set the due date to 30 November 2032."
        ),
        "display_title": "Regression triage from 3251e612",
        "titles": [
            "Regression triage from 3251e612",
            "Regression triage from 3251e6125b17d27a77d625d132074ffcaeb3cb4c",
        ],
        "assignee_id": 2367,
        "assignee": "Primer (@primer)",
        "due": "2032-11-30",
        "derived": "the head commit's short SHA 3251e612 on master, rendered by the overview's last-commit banner (RepoTree.jsx:131 via shortSha, format.js:185)",
        "chain": "read the latest commit's short SHA off byteblaze/cloud-to-butt's default branch -> create an issue in that repo whose title carries the SHA, assigned to Primer and due 2032-11-30",
        "analogues": [ANALOGUE["c2b"], ANALOGUE["primer_reviewer"]],
        "inspiration_ids": ["webarena-808", "webarena-666"],
        "derived_from": None,
        "setup": None,
        "injections": [],
        "notes": [
            "cloud-to-butt's default_branch is master, not main (src/data/projects.json id 189). The task never writes a file, so the master/main trap costs nothing here - but the SHA must be read from master, and by-project/189.json commits.ref is 'master'.",
            "Head commit is 3251e6125b17d27a77d625d132074ffcaeb3cb4c, 'Merge pull request #70 from lionello/fix-node-tagName-classList'; the runner-up is a different SHA, so there is no tie.",
            "Both the 8-character rendering and the full 40-character SHA are accepted, because the commit page's own URL carries the long form and both are honest readings of the same fact. Neither is reachable without the lookup.",
            "No initial_setup: pristine newIssues is empty, so the untouched lane scores 0.0.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/byteblaze/cloud-to-butt']", "overview last-commit banner shows 3251e612"),
        ],
        "assign_mode": "search",
        "assign_query": "Primer",
        "assign_username": "primer",
    },
    {
        "id": "named_issue_assign_due_millennials_storage_005",
        "style": "terse",
        "project_id": 187,
        "full_path": "byteblaze/millennials-to-snake-people",
        "instruction": (
            'millennials-to-snake-people has grown. File an issue there titled "Trim the repo below X", '
            "where X is the project storage figure shown on its overview, assign it to Abishek S, and "
            "set the due date to 19 August 2033."
        ),
        "display_title": "Trim the repo below 793 KB",
        "titles": ["Trim the repo below 793 KB"],
        "assignee_id": 5,
        "assignee": "Abishek S (@abisubramanya27)",
        "due": "2033-08-19",
        "derived": "the storage figure '793 KB' on the overview stats row (ProjectOverview.jsx:366, humanSize at :164)",
        "chain": "read the project storage figure off byteblaze/millennials-to-snake-people's overview -> create an issue in that repo whose title carries the figure, assigned to Abishek S and due 2033-08-19",
        "analogues": [ANALOGUE["dotfiles"], ANALOGUE["projid"]],
        "inspiration_ids": ["webarena-660", "webarena-168"],
        "derived_from": None,
        "setup": {"projectEdits": MILLENNIALS_EDIT},
        "injections": [
            "projectEdits['187'] replaces the whole byteblaze/millennials-to-snake-people row with an identical copy whose repo_size is 812345 instead of 377562. The overlay's edits map stores the FULL record (overlay.js reconcileCollection), so every other field is carried over verbatim from src/data/projects.json.",
            "812345 / 1024 = 793.31, and humanSize rounds it to '793 KB' - not near a .5 boundary, so the rendering is stable. Uninjected the figure would be '369 KB', which is memorisable from the frozen seed.",
        ],
        "notes": [
            "Only the overview renders repo_size, so there is exactly one place the figure can be read and exactly one rendering of it.",
            "The injection touches projectEdits only; the rubric reads newIssues, so nothing is pre-satisfied.",
            "Abishek S is not a member of this project, but Controls.jsx:47-62 offers every user, and the dropdown's search box matches 'abishek' against exactly one row.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/byteblaze/millennials-to-snake-people']", "overview stats row reads '793 KB Project Storage'"),
        ],
        "assign_mode": "search",
        "assign_query": "Abishek",
        "assign_username": "abisubramanya27",
    },
    {
        "id": "named_issue_assign_due_gimmiethat_developer_006",
        "style": "terse",
        "project_id": 184,
        "full_path": "byteblaze/gimmiethat.space",
        "instruction": (
            'gimmiethat.space is changing hands. File an issue there titled "Handover notes for @H", '
            "where H is the handle of the project's only Developer, assign it to them, and set the "
            "due date to 28 February 2034."
        ),
        "display_title": "Handover notes for @yjlou",
        "titles": ["Handover notes for @yjlou"],
        "assignee_id": 168,
        "assignee": "yjlou (@yjlou)",
        "due": "2034-02-28",
        "derived": "the only Developer on the project's Members page, @yjlou (MembersTable.jsx:436 renders the Max role label)",
        "chain": "read byteblaze/gimmiethat.space's member list and pick the one Developer -> create an issue in that repo whose title carries their handle and whose assignee is that account, due 2034-02-28",
        "analogues": [ANALOGUE["gimmie"], ANALOGUE["a11y"]],
        "inspiration_ids": ["webarena-349", "webarena-658"],
        "derived_from": "top_contributor_join_issue_001",
        "setup": {"newMembers": [member(206, 184, 5, 10, "Guest", "2023-03-11 09:41:18.220417", 2330)],
                  "nextIds": {"member": 207}},
        "injections": [
            "newMembers adds Abishek S (user 5) as a Guest on project 184, in the exact shape mutations.js addMembers writes ({id, source_type, source_id, user_id, access_level, access_label, created_at, expires_at, created_by_id}). Pristine the table holds only byteblaze (Owner) and yjlou (Developer), so 'the only Developer' could be reached by taking the one row that is not me; the Guest distractor forces the Max-role column to actually be read.",
            "nextIds.member 206 -> 207 so a member the agent might add cannot collide with the injected id (overlayShape.js SEED_NEXT_IDS.member = 206).",
            "Uniqueness after injection: access levels on project 184 are 50 / 30 / 10, so exactly one row is a Developer.",
        ],
        "notes": [
            "gimmiethat.space is private and owned by byteblaze, so the members table and its Max-role column render for the current user.",
            "The handle renders as '@yjlou' in the Account cell (MembersTable.jsx:28 note), so the title token is legible without opening a profile.",
            "The injection writes newMembers and nextIds only; the rubric reads newIssues, so nothing is pre-satisfied.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/byteblaze/gimmiethat.space']", "project overview"),
            ("click", "a.shortcuts-project-information", "Project information opens on /activity"),
            ("click", "a[href='/byteblaze/gimmiethat.space/-/project_members']", "Members table: yjlou is the only Developer"),
        ],
        "assign_mode": "search",
        "assign_query": "yjlou",
        "assign_username": "yjlou",
    },
    {
        "id": "named_issue_assign_due_prism_theme_guest_007",
        "style": "terse",
        "project_id": 188,
        "full_path": "byteblaze/solarized-prism-theme",
        "instruction": (
            'The solarized-prism-theme repo needs a review ticket. Open an issue there titled '
            '"Theme review for @H", where H is the handle of the project\'s only Guest member, '
            "assign it to them, and set the due date to 1 October 2033."
        ),
        "display_title": "Theme review for @abisubramanya27",
        "titles": ["Theme review for @abisubramanya27"],
        "assignee_id": 5,
        "assignee": "Abishek S (@abisubramanya27)",
        "due": "2033-10-01",
        "derived": "the only Guest on the project's Members page, @abisubramanya27",
        "chain": "read byteblaze/solarized-prism-theme's member list and pick the one Guest -> create an issue in that repo whose title carries their handle and whose assignee is that account, due 2033-10-01",
        "analogues": [ANALOGUE["prism"], ANALOGUE["dotfiles"]],
        "inspiration_ids": ["webarena-350", "webarena-660"],
        "derived_from": "top_contributor_join_issue_001",
        "setup": {"newMembers": [member(206, 188, 168, 30, "Developer", "2023-03-14 17:02:55.913004", 2330)],
                  "nextIds": {"member": 207}},
        "injections": [
            "newMembers adds yjlou (user 168) as a Developer on project 188, in mutations.js addMembers' shape. Pristine the table is byteblaze (Owner) + Abishek S (Guest), so the Guest is simply 'the other row'; the Developer distractor makes the role column load-bearing.",
            "nextIds.member 206 -> 207 to clear the injected id.",
            "Uniqueness after injection: access levels on project 188 are 50 / 30 / 10, so exactly one row is a Guest.",
        ],
        "notes": [
            "solarized-prism-theme's default branch is master, but the task creates no branch or file, so nothing is keyed on a ref.",
            "The project holds zero seeded issues, so the Issues page shows the empty-state 'New issue' button (IssuablesList.jsx:862).",
            "The injection writes newMembers and nextIds only; the rubric reads newIssues, so nothing is pre-satisfied.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/byteblaze/solarized-prism-theme']", "project overview"),
            ("click", "a.shortcuts-project-information", "Project information opens on /activity"),
            ("click", "a[href='/byteblaze/solarized-prism-theme/-/project_members']", "Members table: Abishek S is the only Guest"),
        ],
        "assign_mode": "search",
        "assign_query": "Abishek",
        "assign_username": "abisubramanya27",
    },
    {
        "id": "named_issue_assign_due_osd_developer_008",
        "style": "explicit",
        "project_id": 171,
        "full_path": "opensourcediversity/opensourcediversity.org",
        "instruction": (
            "The opensourcediversity.org site needs its documentation swept and I want the ticket to "
            "land on whoever holds Developer access there. Starting from the GitLab landing page, "
            "find opensourcediversity/opensourcediversity.org, open its Members page (Project "
            "information, then Members) and read the Max role column to find the one member whose "
            "role is Developer. Then create a new issue on that project titled \"Docs sweep for @H\", "
            "where H is that person's @handle exactly as the members table shows it, set that same "
            "person as the issue's assignee, and give the issue a due date of 31 December 2033. Do "
            "not change anybody's role and do not remove any member."
        ),
        "display_title": "Docs sweep for @Roshanjossey",
        "titles": ["Docs sweep for @Roshanjossey"],
        "assignee_id": 2264,
        "assignee": "Roshan Jossy (@Roshanjossey)",
        "due": "2033-12-31",
        "derived": "the only Developer on the project's Members page, @Roshanjossey",
        "chain": "read opensourcediversity/opensourcediversity.org's member list and pick the one Developer -> create an issue in that repo whose title carries their handle and whose assignee is that account, due 2033-12-31",
        "analogues": [ANALOGUE["a11y"], ANALOGUE["assign_rohan"]],
        "inspiration_ids": ["webarena-658", "webarena-447"],
        "derived_from": "mention_participant_assign_wcag_references_a11yproject_004",
        "setup": {"newMembers": [member(206, 171, 5, 20, "Reporter", "2023-03-08 12:26:44.508122", 2325)],
                  "nextIds": {"member": 207}},
        "injections": [
            "newMembers adds Abishek S (user 5) as a Reporter on project 171, in mutations.js addMembers' shape. Pristine the table is Open Source Diversity (Owner) + Roshan Jossy (Developer); the Reporter distractor means the agent must distinguish Reporter from Developer rather than take the non-owner row.",
            "nextIds.member 206 -> 207 to clear the injected id.",
            "Uniqueness after injection: access levels on project 171 are 50 / 30 / 20, so exactly one row is a Developer.",
        ],
        "notes": [
            "byteblaze is not a member of opensourcediversity.org, so canManageMembers is false and the invite controls are hidden - the members TABLE still renders (ProjectMembers.jsx:26 renders MembersTable unconditionally), which is all the lookup needs.",
            "The New issue button carries no permission gate (IssuablesList.jsx:190), so a non-member can still file the issue.",
            "The handle's capital R matters to a human but the rubric compares titles case-insensitively after whitespace collapse, so '@roshanjossey' is also accepted; no other user's handle normalises to the same string.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/opensourcediversity/opensourcediversity.org']", "project overview"),
            ("click", "a.shortcuts-project-information", "Project information opens on /activity"),
            ("click", "a[href='/opensourcediversity/opensourcediversity.org/-/project_members']", "Members table: Roshan Jossy is the only Developer"),
        ],
        "assign_mode": "search",
        "assign_query": "Roshan",
        "assign_username": "Roshanjossey",
    },
    {
        "id": "named_issue_assign_due_primer_owner_009",
        "style": "terse",
        "project_id": 180,
        "full_path": "primer/design",
        "instruction": (
            'primer/design needs a sign-off recorded. Open an issue on that project titled '
            '"Design system sign-off from @H", where H is the handle of the project\'s Owner, '
            "assign it to them, and set the due date to 1 July 2032."
        ),
        "display_title": "Design system sign-off from @primer",
        "titles": ["Design system sign-off from @primer"],
        "assignee_id": 2367,
        "assignee": "Primer (@primer)",
        "due": "2032-07-01",
        "derived": "the Owner on the project's Members page, @primer",
        "chain": "read primer/design's member list and pick the Owner -> create an issue in that repo whose title carries their handle and whose assignee is that account, due 2032-07-01",
        "analogues": [ANALOGUE["primer_reviewer"], ANALOGUE["a11y"]],
        "inspiration_ids": ["webarena-666", "webarena-658"],
        "derived_from": "mention_participant_assign_link_targets_primer_008",
        "setup": {"newMembers": [member(206, 180, 2264, 40, "Maintainer", "2023-03-06 08:55:12.771903", 2367)],
                  "nextIds": {"member": 207}},
        "injections": [
            "newMembers adds Roshan Jossy (user 2264) as a Maintainer on project 180, in mutations.js addMembers' shape. Pristine the table is Primer (Owner) + byteblaze (Developer), so the Owner is the only non-me row; the Maintainer distractor puts a second high-privilege row in the table and forces the Owner label to be read.",
            "nextIds.member 206 -> 207 to clear the injected id.",
            "Uniqueness after injection: access levels on project 180 are 50 / 40 / 30, so exactly one row is an Owner.",
        ],
        "notes": [
            "byteblaze is only a Developer on primer/design, so the members page renders the heading and table but no invite paragraph (ProjectMembers.jsx:31, BUG-B10). The Max-role column still renders for every row.",
            "primer/design has 56 seeded issues, so the list page renders normally and 'New issue' is the header button.",
            "The injection writes newMembers and nextIds only; the rubric reads newIssues, so nothing is pre-satisfied.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/primer/design']", "project overview"),
            ("click", "a.shortcuts-project-information", "Project information opens on /activity"),
            ("click", "a[href='/primer/design/-/project_members']", "Members table: Primer is the Owner"),
        ],
        "assign_mode": "search",
        "assign_query": "Primer",
        "assign_username": "primer",
    },
    {
        "id": "named_issue_assign_due_robot_developer_010",
        "style": "terse",
        "project_id": 40,
        "full_path": "convexegg/super_awesome_robot",
        "instruction": (
            'convexegg/super_awesome_robot needs a retest logged. Open an issue there titled '
            '"Firmware retest for @H", where H is the handle of the project\'s only Developer, '
            "assign it to them, and set the due date to 30 April 2035."
        ),
        "display_title": "Firmware retest for @murale127",
        "titles": ["Firmware retest for @murale127"],
        "assignee_id": 6,
        "assignee": "Muralekrishnan R (@murale127)",
        "due": "2035-04-30",
        "derived": "the only Developer on the project's Members page, @murale127",
        "chain": "read convexegg/super_awesome_robot's member list and pick the one Developer -> create an issue in that repo whose title carries their handle and whose assignee is that account, due 2035-04-30",
        "analogues": [ANALOGUE["gimmie"], ANALOGUE["c2b"]],
        "inspiration_ids": ["webarena-349", "webarena-808"],
        "derived_from": None,
        "setup": {"newMembers": [member(206, 40, 2264, 20, "Reporter", "2023-03-04 19:33:07.640215", 43)],
                  "nextIds": {"member": 207}},
        "injections": [
            "newMembers adds Roshan Jossy (user 2264) as a Reporter on project 40, in mutations.js addMembers' shape. Pristine the table is Convex Eggtart (Owner) + Muralekrishnan R (Developer), so the Developer is the only non-owner row; the Reporter distractor forces the role column to be read.",
            "nextIds.member 206 -> 207 to clear the injected id.",
            "Uniqueness after injection: access levels on project 40 are 50 / 30 / 20, so exactly one row is a Developer.",
        ],
        "notes": [
            "byteblaze is not a member of convexegg/super_awesome_robot, but the project is public, the members table renders unconditionally and the New issue button carries no permission gate.",
            "The project holds zero seeded issues, so the Issues page shows the empty-state 'New issue' button.",
            "The injection writes newMembers and nextIds only; the rubric reads newIssues, so nothing is pre-satisfied.",
        ],
        "retrieval_steps": [
            ("click", "a[href='/convexegg/super_awesome_robot']", "project overview"),
            ("click", "a.shortcuts-project-information", "Project information opens on /activity"),
            ("click", "a[href='/convexegg/super_awesome_robot/-/project_members']", "Members table: Muralekrishnan R is the only Developer"),
        ],
        "assign_mode": "search",
        "assign_query": "Murale",
        "assign_username": "murale127",
    },
]


# --------------------------------------------------------------------------
# shared rubric body
# --------------------------------------------------------------------------

RUBRIC_BODY = '''
COMPONENT_WEIGHTS = {
    "issue_created_with_derived_title": 0.4,
    "assigned_to_target_user": 0.3,
    "due_date_recorded": 0.3,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

PROJECT_ID = %(project_id)d
ACCEPTED_TITLES = %(titles)s
DISPLAY_TITLE = %(display_title)r
ASSIGNEE_ID = %(assignee_id)d
DUE_DATE = %(due)r

_WS = re.compile(r"\\s+")
_ISO = re.compile(r"^(\\d{4}-\\d{2}-\\d{2})")


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _norm(value):
    if not isinstance(value, str):
        return ""
    return _WS.sub(" ", value.strip()).casefold()


def _int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and float(value).is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return None


def _ids(value):
    out = []
    for item in _list(value):
        got = _int(item)
        if got is not None:
            out.append(got)
    return out


def _iso_date(value):
    if not isinstance(value, str):
        return ""
    match = _ISO.match(value.strip())
    return match.group(1) if match else ""


WANTED_TITLES = [_norm(t) for t in ACCEPTED_TITLES]


def _new_issues(state):
    return [r for r in _list(_dict(state).get("newIssues")) if isinstance(r, dict)]


def _in_project(state):
    return [r for r in _new_issues(state) if _int(r.get("project_id")) == PROJECT_ID]


def _matched(state):
    return [r for r in _in_project(state) if _norm(r.get("title")) in WANTED_TITLES]


def score_state(state):
    in_project = _in_project(state)
    matched = _matched(state)
    issue = matched[0] if len(matched) == 1 else None
    assignees = _ids(issue.get("assignee_ids")) if issue is not None else []
    due = _iso_date(issue.get("due_date")) if issue is not None else ""

    facts = {
        "issue_created_with_derived_title": issue is not None,
        "assigned_to_target_user": issue is not None and assignees == [ASSIGNEE_ID],
        "due_date_recorded": issue is not None and due == DUE_DATE,
    }
    details = {
        "issue_created_with_derived_title": (
            "newIssues rows on project %%d == %%d; rows whose title matches %%r == %%d"
            %% (PROJECT_ID, len(in_project), DISPLAY_TITLE, len(matched))
        ),
        "assigned_to_target_user": "assignee_ids == %%r, wanted [%%d]" %% (assignees, ASSIGNEE_ID),
        "due_date_recorded": "due_date == %%r, wanted %%r" %% (due, DUE_DATE),
    }
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = bool(facts.get(name))
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": details.get(name, ""),
        })
    return components


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
'''


REWARD_TMPL = '''"""Deterministic reward for %(tid)s.

The derived value is %(derived)s. It is never stated in the instruction, and
every component below is gated on locating the created issue by that value, so
an agent that skips the lookup scores exactly 0.0.

Reads `current_state` only. The scored writeback is the record NewIssue.jsx:63
appends through `appendTo('issues', ...)`, which the overlay persists as a row
of `newIssues` (overlayShape.js:43).
"""

import re
%(body)s

def evaluate(evidence):
    state = _dict(_dict(_dict(_dict(evidence).get("apps")).get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''


NEMO_REWARD_TMPL = '''"""NeMo-Gym reward program for %(tid)s.

Same rubric as reward.py, read from GET /go?sid=... instead of a frozen
evidence bundle. Prints REWARD: <float> on every output path.

Self-contained: standard library plus `requests`.
"""

import re
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"
%(body)s

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %%s" %% exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %%.6f" %% _clamp(float(total)))


main()
'''


SETUP_TMPL = '''"""NeMo-Gym setup program for %(tid)s.

%(summary)s

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"

BASE_STATE = json.loads(r"""
{
  "currentUser": %(current_user)s,
  "snippets": [],
  "repo": {"fileOverlay": {}, "treeOverlay": {}, "commitOverlay": {}, "branchOverlay": {},
           "tagOverlay": {}, "branchDeletions": {}, "tagDeletions": {}, "forkOrigin": {}},
  "ui": {"notificationLevels": {}, "sidebarCollapsed": false, "dismissedAlerts": [],
         "preferences": {"colorScheme": "light", "syntaxTheme": "white"},
         "projectSettings": {}},
  "nextIds": %(next_ids)s
}
""")

OVERLAY_COLLECTIONS = [
    ("newUsers", "userEdits", "deletedUsers"),
    ("newProjects", "projectEdits", "deletedProjects"),
    ("newGroups", "groupEdits", "deletedGroups"),
    ("newIssues", "issueEdits", "deletedIssues"),
    ("newMergeRequests", "mergeRequestEdits", "deletedMergeRequests"),
    ("newNotes", "noteEdits", "deletedNotes"),
    ("newLabels", "labelEdits", "deletedLabels"),
    ("newMilestones", "milestoneEdits", "deletedMilestones"),
    ("newMembers", "memberEdits", "deletedMembers"),
    ("newTodos", "todoEdits", "deletedTodos"),
    ("newStars", "starEdits", "deletedStars"),
    ("newFollows", "followEdits", "deletedFollows"),
]

INJECTED = json.loads(r"""
%(injected)s
""")


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {}
        state[deleted] = []
    for key, value in INJECTED.items():
        if key == "repo":
            merged = dict(state["repo"])
            merged.update(value)
            state["repo"] = merged
        else:
            state[key] = value
    return state


def publish(state):
    response = requests.post(BASE_URL + "/post?sid=" + SID,
                             json={"action": "set", "state": state}, timeout=30)
    response.raise_for_status()
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: baseline and current disagree after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


publish(build_state())
'''

DEFAULT_NEXT_IDS = {"project": 194, "group": 7, "issue": 83821, "mr": 139278,
                    "note": 310827, "label": 1927, "milestone": 590, "member": 206}


def build_setup(task):
    setup = task["setup"]
    if not setup:
        return None
    injected = {k: v for k, v in setup.items() if k != "nextIds"}
    next_ids = dict(DEFAULT_NEXT_IDS)
    next_ids.update(setup.get("nextIds", {}))
    summary = " ".join(task["injections"][:1])
    return SETUP_TMPL % {
        "tid": task["id"],
        "summary": summary,
        "current_user": CURRENT_USER,
        "next_ids": json.dumps(next_ids),
        "injected": json.dumps(injected, indent=2),
    }


def build_reward(task, nemo):
    body = RUBRIC_BODY % {
        "project_id": task["project_id"],
        "titles": repr(task["titles"]),
        "display_title": task["display_title"],
        "assignee_id": task["assignee_id"],
        "due": task["due"],
    }
    tmpl = NEMO_REWARD_TMPL if nemo else REWARD_TMPL
    return tmpl % {"tid": task["id"], "derived": task["derived"], "body": body}


def build_replay(task):
    lines = [
        '"""Golden replay draft for %s.' % task["id"],
        "",
        "Click-only: after the initial goto of start_path every navigation is a",
        "click on a rendered link or button. No constructed URLs.",
        '"""',
        "",
        "",
        "def run(page, base_url):",
        '    page.goto(base_url + "/")',
        '    page.wait_for_load_state("networkidle")',
        "",
        "    # --- find the named project from the landing page (navbar search) ---",
        '    page.fill("#search", %r)' % task["full_path"].split("/")[-1],
        '    page.press("#search", "Enter")',
        '    page.wait_for_load_state("networkidle")',
    ]
    for _, selector, note in task["retrieval_steps"]:
        lines.append("    # %s" % note)
        lines.append('    page.click(%r)' % selector)
        lines.append('    page.wait_for_load_state("networkidle")')
    lines += [
        "",
        "    # --- back to the project, then Issues -> New issue ------------------",
        '    page.click("a.shortcuts-project")',
        '    page.wait_for_load_state("networkidle")',
        '    page.click("a.shortcuts-issues")',
        '    page.wait_for_load_state("networkidle")',
        '    page.click("[data-qa-selector=\'new_issue_link\'], a:has-text(\'New issue\')")',
        '    page.wait_for_load_state("networkidle")',
        '    page.fill("#issue_title", %r)' % task["display_title"],
    ]
    if task["assign_mode"] == "me":
        lines.append('    page.click("[data-qa-selector=\'assign_to_me_link\']")')
    else:
        lines += [
            '    page.click(".js-assignee-search")',
            '    page.fill("input[placeholder=\'Search users\']", %r)' % task["assign_query"],
            '    page.click(".dropdown-menu-user li:has-text(\'@%s\')")' % task["assign_username"],
        ]
    lines += [
        '    page.fill("#issuable-due-date", %r)' % task["due"],
        '    page.click("[data-qa-selector=\'issuable_create_button\']")',
        '    page.wait_for_load_state("networkidle")',
        "    page.wait_for_timeout(500)",
        "",
    ]
    return "\n".join(lines)


def success_criteria(task):
    titles = " or ".join(repr(t) for t in task["titles"])
    return [
        "newIssues holds exactly one record for project %d (%s) whose title is %s."
        % (task["project_id"], task["full_path"], titles),
        "That record's assignee_ids is exactly [%d] (%s)." % (task["assignee_id"], task["assignee"]),
        "That record's due_date is '%s'." % task["due"],
    ]


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    nemo_rows = []

    for task in TASKS:
        tid = task["id"]
        bundle = os.path.join(OUT, tid)
        os.makedirs(bundle, exist_ok=True)

        setup_src = build_setup(task)
        reward_src = build_reward(task, nemo=False)
        nemo_reward_src = build_reward(task, nemo=True)

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": tid,
                "task_instruction": task["instruction"],
                "app_dir": "webarena_gitlab_mock",
                "start_path": "/",
                "difficulty": "medium",
                "success_criteria": success_criteria(task),
            }, fh, indent=2)
            fh.write("\n")

        manifest = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
            "apps": [{
                "name": "webarena_gitlab_mock",
                "source_name": "gitlab",
                "base_url_env": "CUA_GYM_WEBARENA_GITLAB_URL",
                "start_path": "/",
                "initial_state": None,
                "golden_state": None,
            }],
            "reward_path": "reward.py",
            "requirements_path": None,
            "evidence": [],
            "source_evaluator": {},
            "source": "webarena",
            "metadata": {
                "style": task["style"],
                "difficulty": "medium",
                "shape": "retrieval_writeback",
                "skills": ["R9", "A12"],
                "skill_chain": task["chain"],
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "topic": "gitlab named repo issue with assignee and due date",
                "inspiration_ids": task["inspiration_ids"],
                "authoring_notes": task["notes"],
                "injected_preconditions": task["injections"],
            },
        }
        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)
            fh.write("\n")

        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_src)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward_src)
        if setup_src is not None:
            with open(os.path.join(bundle, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        row = {"task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_gitlab_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": "webarena_gitlab_mock",
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward_src,
            },
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        nemo_rows.append(row)

        with open(os.path.join(REPLAYS, tid + ".py"), "w") as fh:
            fh.write(build_replay(task))

        index["tasks"].append({"task_id": tid, "path": "../../%s/task.json" % tid})

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in nemo_rows:
            fh.write(json.dumps(row) + "\n")

    print("wrote %d bundles" % len(TASKS))


main()

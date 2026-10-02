import json, os, re

TPL = "/home/ubuntu/.claude/jobs/a721f968/tmp/tpl_%s.txt"
_cache = {}

def intents(site):
    if site not in _cache:
        rows = []
        for line in open(TPL % site):
            parts = line.rstrip("\n").split("\t", 3)
            rows.append(parts[3])
        _cache[site] = rows
    return _cache[site]

def an(site, *idx):
    """Resolve analogues verbatim from the official corpus by template index."""
    rows = intents(site)
    return [rows[i] for i in idx]

DIST = ("The hub serves the prebuilt dist/ (built 2026-08-17) under vite preview and never "
        "reads src/; a claim read from src/ is only as good as the build.")
PARTIAL = ("Partial `set`: reddit REPLACES initial_state with the partial object, shopping and "
           "shopping_admin shallow-merge over createInitialData(); gitlab is unmeasured. Read the "
           "mock's own vite.config.js before writing a partial set.")
GITLAB_ENV = (DIST + " On gitlab the consequence is concrete: clicking Settings on a project lands "
              "on the legacy /:ns/:proj/edit route and the sidebar expands Repository, so "
              "/-/settings/repository, /-/settings/ci_cd, /-/hooks and /-/settings/access_tokens are "
              "NOT click-reachable and ui.projectSettings is not a fair writeback. Sidebar sub-items "
              "never appear on hover: click the section link, land on its default page, then click "
              "the child. CI/CD Analytics and Repository Analytics both live under Analytics, not "
              "CI/CD. Never size a task off SCHEMA.md (stale ~30x: real corpus is 19,705 issues, "
              "23,236 MRs, 2,199 users, 1,254 labels, 343 milestones).")
REDDIT_ENV = (DIST + " On reddit, Sidebars.jsx, layout/SiteNav.jsx and ForumModeratorsPage.jsx are "
              "newer than the served bundle and their changes are NOT live: the `Mod trash` user-menu "
              "item is absent from the bundle entirely, and the `|| currentUser.admin` fallback that "
              "would unlock the forum Toolbox is absent too (probed: admin:true left the Toolbox at "
              "['Bans','Moderation log'] and /f/DIY/edit at 403). Reddit's partial `set` REPLACES "
              "initial_state, so seed the full state document or diff against current_state, never "
              "state_diff.")
SHOP_ENV = ("shopping's dist/ is newer than its src/, so source-reading is sound here (unlike gitlab "
            "and reddit). /post shallow-merges over createInitialData() (vite.config.js:441-449), "
            "confirmed three independent times, so a partial patch yields a complete 15-key document. "
            "SCHEMA.md is stale ~2x: 22,721 products (22,460 listable), 76,378 reviews over 6,044 products.")
ADMIN_ENV = ("shopping_admin's dist/ is newer than its src/, so source-reading is sound here. /post "
             "shallow-merges (vite.config.js:371-377) but the merge is SHALLOW: a nested key such as "
             "systemConfig.variables needs systemConfig re-posted whole - read it back from /go and "
             "patch. There is no `ui` object and no `ui` key among the 44 persisted state keys, so "
             "nothing may be graded on ui.dismissedAlerts here (that finding is TRUE of gitlab only).")

def write(topics, path="/home/ubuntu/CUA-Gym/output/topics.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)
        f.write("\n")

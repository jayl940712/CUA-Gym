# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Generated constants for the CUA-Gym-Hub deployment.

APP_DIRS mirrors `deploy-all.sh` in CUA-Gym-Hub commit e40c1188: mock apps are the
sorted `websites/webarena*_mock` directories, served on consecutive ports from the
base port (default 8000). PLACEHOLDER_MAP mirrors the dataset's url_variables.json.
Regenerate against a new hub commit rather than editing by hand.
"""

from __future__ import annotations


HUB_COMMIT = "e40c118804cdc9653eab0a183ddbdb4182a9e519"

APP_DIRS: list[str] = [
    "webarena_classifieds_mock",
    "webarena_gitlab_mock",
    "webarena_reddit_mock",
    "webarena_shopping_admin_mock",
    "webarena_shopping_mock",
]

# placeholder -> {app_dir, kind}; kind "url" gets http://host:port, "host" gets host:port
PLACEHOLDER_MAP: dict[str, dict[str, str]] = {
    "__CUA_GYM_WEBARENA_CLASSIFIEDS_HOST__": {"app_dir": "webarena_classifieds_mock", "kind": "host"},
    "__CUA_GYM_WEBARENA_CLASSIFIEDS_URL__": {"app_dir": "webarena_classifieds_mock", "kind": "url"},
    "__CUA_GYM_WEBARENA_GITLAB_HOST__": {"app_dir": "webarena_gitlab_mock", "kind": "host"},
    "__CUA_GYM_WEBARENA_GITLAB_URL__": {"app_dir": "webarena_gitlab_mock", "kind": "url"},
    "__CUA_GYM_WEBARENA_REDDIT_HOST__": {"app_dir": "webarena_reddit_mock", "kind": "host"},
    "__CUA_GYM_WEBARENA_REDDIT_URL__": {"app_dir": "webarena_reddit_mock", "kind": "url"},
    "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_HOST__": {"app_dir": "webarena_shopping_admin_mock", "kind": "host"},
    "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__": {"app_dir": "webarena_shopping_admin_mock", "kind": "url"},
    "__CUA_GYM_WEBARENA_SHOPPING_HOST__": {"app_dir": "webarena_shopping_mock", "kind": "host"},
    "__CUA_GYM_WEBARENA_SHOPPING_URL__": {"app_dir": "webarena_shopping_mock", "kind": "url"},
}

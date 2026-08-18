import json

from cua_gym_web.importer import import_jsonl, import_row

SUPPORTED = {
    "webarena_gitlab_mock",
    "webarena_reddit_mock",
    "webarena_shopping_mock",
}


def test_import_row_preserves_cross_site_metadata_and_evaluator():
    row = {
        "id": "webarena-42",
        "ques": "Copy the project name into a Reddit post.",
        "web_name": ["gitlab", "reddit"],
        "web": ["__GITLAB__/group/project", "__REDDIT__/submit"],
        "eval": {"eval_types": ["program_html"], "program_html": []},
    }

    task = import_row(row, SUPPORTED, "webarena.jsonl")

    assert task is not None
    assert [app.source_name for app in task.apps] == ["gitlab", "reddit"]
    assert [app.start_path for app in task.apps] == ["/group/project", "/submit"]
    assert task.source_evaluator == row["eval"]


def test_import_row_rejects_task_with_any_unsupported_site():
    row = {
        "id": "webarena-99",
        "ques": "Use GitLab and Wikipedia.",
        "web_name": ["gitlab", "wikipedia"],
        "web": ["__GITLAB__/", "__WIKIPEDIA__/wiki/Test"],
        "eval": {},
    }

    assert import_row(row, SUPPORTED, "webarena.jsonl") is None


def test_import_jsonl_writes_versioned_bundles(tmp_path):
    source = tmp_path / "webarena.jsonl"
    source.write_text(
        json.dumps(
            {
                "id": "webarena-1",
                "ques": "Open the repository.",
                "web_name": "gitlab",
                "web": "__GITLAB__/group/repo",
                "eval": {
                    "eval_types": ["url_match"],
                    "reference_url": "__GITLAB__/group/repo",
                },
            }
        )
        + "\n"
    )

    tasks = import_jsonl(source, tmp_path / "out", SUPPORTED)

    assert len(tasks) == 1
    assert (tmp_path / "out" / "webarena-1" / "task.json").is_file()
    assert (tmp_path / "out" / "webarena-1" / "reward.py").is_file()
    index = json.loads((tmp_path / "out" / "index.json").read_text())
    assert index["task_count"] == 1


def test_import_raw_webarena_array_format(tmp_path):
    source = tmp_path / "test.raw.json"
    source.write_text(
        json.dumps(
            [
                {
                    "task_id": 7,
                    "intent": "Find the cheapest blue kayak.",
                    "sites": ["classifieds"],
                    "start_url": "__CLASSIFIEDS__",
                    "eval": {
                        "eval_types": ["url_match"],
                        "reference_url": "__CLASSIFIEDS__/index.php?page=item&id=4799",
                        "url_note": "EXACT",
                    },
                }
            ]
        )
    )

    tasks = import_jsonl(
        source,
        tmp_path / "out",
        {*SUPPORTED, "webarena_classifieds_mock"},
        id_prefix="visualwebarena",
    )

    assert tasks[0].task_id == "visualwebarena-7"
    assert tasks[0].source == "visualwebarena"
    assert tasks[0].instruction == "Find the cheapest blue kayak."
    assert tasks[0].apps[0].start_path == "/"


def test_answer_only_task_is_excluded_without_browser_writeback(tmp_path):
    source = tmp_path / "answers.json"
    source.write_text(
        json.dumps(
            [
                {
                    "task_id": 8,
                    "intent": "What is the project name?",
                    "sites": ["gitlab"],
                    "start_url": "__GITLAB__",
                    "eval": {
                        "eval_types": ["string_match"],
                        "reference_answers": {"exact_match": "Example"},
                    },
                }
            ]
        )
    )

    tasks = import_jsonl(source, tmp_path / "out", SUPPORTED)

    assert tasks == []
    index = json.loads((tmp_path / "out" / "index.json").read_text())
    assert index["skipped_by_reason"] == {
        "answer-only task has no verifiable browser writeback": 1
    }

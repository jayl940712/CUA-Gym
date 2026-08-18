from scripts.sample_webarena_inspirations import sample_rows, summarize


def row(task_id, site, question, eval_type):
    return {
        "id": task_id,
        "web_name": [site],
        "ques": question,
        "eval": {"eval_types": [eval_type]},
    }


def test_sampler_uses_only_supported_sites_and_requested_topic():
    rows = [
        row("1", "gitlab", "Create an issue", "program_html"),
        row("2", "reddit", "Create a post", "program_html"),
        row("3", "map", "Find an airport", "string_match"),
    ]

    selected = sample_rows(
        rows,
        count=10,
        sites={"gitlab"},
        eval_types=set(),
        keyword="issue",
        seed=0,
    )

    assert [item["id"] for item in selected] == ["1"]


def test_summary_marks_retrieval_pattern_for_writeback():
    value = summarize(
        row("1", "shopping_admin", "Find the top product", "string_match")
    )

    assert value["requires_observable_writeback"] is True
    assert "reference_answers" not in value

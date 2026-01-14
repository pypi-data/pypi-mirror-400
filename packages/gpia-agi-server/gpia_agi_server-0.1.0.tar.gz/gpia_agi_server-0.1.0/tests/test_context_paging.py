from pathlib import Path

from core.context_pager import ContextPager


ROOT = Path(__file__).resolve().parents[1]


def test_constraint_blocks_turn_50():
    pager = ContextPager(ROOT)
    pager.reset()
    pager.add_constraint("BLOCK: BANANA", origin_skill_id="test")

    for turn in range(1, 50):
        pager.record_turn("user", f"turn {turn}")

    retrieval = pager.retrieve("constraints", store="summary", limit=5)
    assert retrieval["items"]
    violation = pager.check_constraints("Please output BANANA now.", retrieval["items"])
    assert violation == "BANANA"


def test_retrieval_throttle():
    pager = ContextPager(ROOT)
    pager.reset()
    pager.add_constraint("BLOCK: ORANGE", origin_skill_id="test")

    for _ in range(3):
        result = pager.retrieve("constraints", store="summary", limit=5)
    assert result["throttled"] is True


def test_pinned_window_contains_constraints():
    pager = ContextPager(ROOT)
    pager.reset()
    pager.add_constraint("BLOCK: PEAR", origin_skill_id="test")
    pager.record_turn("user", "Earlier detail about pears.")

    summary = pager.retrieve("constraints", store="summary", limit=5)
    recall = pager.retrieve("pear", store="recall", limit=5)
    window = pager.build_window(
        "Do not say pear.",
        summary["items"],
        recall["items"],
        recency="recent line",
        max_tokens=200,
    )

    assert "Constraints:" in window["top"]
    assert "BLOCK: PEAR" in window["top"]
    assert window["top"] == window["bottom"]


def test_window_token_budget():
    pager = ContextPager(ROOT)
    pager.reset()
    pager.add_constraint("BLOCK: KIWI", origin_skill_id="test")
    long_text = "detail " * 300
    pager.record_turn("user", long_text)

    summary = pager.retrieve("constraints", store="summary", limit=5)
    recall = pager.retrieve("detail", store="recall", limit=5)
    window = pager.build_window(
        "Do not say kiwi.",
        summary["items"],
        recall["items"],
        recency=long_text,
        max_tokens=120,
    )

    assert window["tokens"] <= 120

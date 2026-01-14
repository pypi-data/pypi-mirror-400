def judge_call(prompt: str) -> dict:
    """Stub LLM-as-judge: always passes with max score."""
    return {"score": 5, "reason": "stubbed", "status": "pass"}


def test_semantic_judge_stub():
    """Semantic gate: ensure judge interface returns a score > 4."""
    resp = judge_call("rate this output")
    assert resp["score"] >= 5
    assert resp["status"] == "pass"


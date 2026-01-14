import os


def judge_call(prompt: str) -> dict:
    """Stub governance judge."""
    return {"status": "pass", "reason": "stubbed"}


def test_governance_cleanup_stub(tmp_path):
    """Governance gate: placeholder cleanup check."""
    # Create a temp file to simulate an artifact, then delete it
    artifact = tmp_path / "artifact.tmp"
    artifact.write_text("temp")
    assert artifact.exists()
    artifact.unlink()
    assert not artifact.exists()
    resp = judge_call("cleanup ok?")
    assert resp["status"] == "pass"


import json
from pathlib import Path

from gpia import GPIA


ROOT = Path(__file__).resolve().parents[1]


def test_dag_plan_requires_approval():
    plan_path = ROOT / "runs" / "plan_approve.json"
    if plan_path.exists():
        plan_path.unlink()

    agent = GPIA(verbose=False)
    result = agent.run("Organize my downloads folder by file type.")
    cap = agent.get_capsule(result.capsule_id)
    plan_record = cap.context.get("plan_record")

    assert plan_record is not None
    assert plan_record["status"] == "PENDING_APPROVAL"
    assert plan_record["plan"]["dag"][0]["instruction"].lower().startswith("scan")
    assert "pending approval" in result.response.lower()

    data = json.loads(plan_path.read_text(encoding="utf-8"))
    assert data["status"] == "PENDING_APPROVAL"

from __future__ import annotations

from pathlib import Path

from skills.base import SkillContext
from skills.research.bsd_gap_closure_framework.skill import BSDGapClosureFrameworkSkill


def test_gap_closure_runs_and_finds_2_torsion(tmp_path: Path):
    skill = BSDGapClosureFrameworkSkill()
    ctx = SkillContext(user_id="test", session_id="test", agent_role="test")

    report_path = tmp_path / "report.md"
    result = skill.execute(
        {
            "capability": "run",
            "curve": {"a": -1, "b": 0},  # y^2 = x^3 - x has 2-torsion at x in {-1,0,1}
            "search": {"x_bound": 10, "u_bound": 10, "v_bound": 5, "torsion_order_max": 12},
            "primes": [101],
            "write_report": True,
            "report_path": str(report_path),
        },
        ctx,
    )

    assert result.success
    assert result.artifacts["report_path"].endswith("report.md")
    assert report_path.exists()

    gap1 = result.output["gaps"]["effective_descent"]
    torsion = [p["x"] for p in gap1["rational_2_torsion_points"]]
    assert torsion == ["-1", "0", "1"]

    gap2 = result.output["gaps"]["local_global_bridge"]
    primes = [p for p in gap2["primes"] if p.get("status") == "good_reduction"]
    assert primes and primes[0]["p"] == 101


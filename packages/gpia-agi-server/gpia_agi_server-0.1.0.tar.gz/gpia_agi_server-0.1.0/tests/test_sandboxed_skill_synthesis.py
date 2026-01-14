import os
from pathlib import Path

from core.sandboxed_skill_synthesizer import SandboxedSkillSynthesizer
from gpia import GPIA


ROOT = Path(__file__).resolve().parents[1]


def test_sandboxed_fibonacci_local():
    os.environ["SANDBOX_FORCE_LOCAL"] = "1"
    synthesizer = SandboxedSkillSynthesizer(ROOT)
    result = synthesizer.synthesize("Calculate the Fibonacci sequence to 7.")
    assert result["success"] is True
    assert result["sandbox_used"] == "local"


def test_dangerous_code_blocked():
    synthesizer = SandboxedSkillSynthesizer(ROOT)
    assert synthesizer._has_dangerous_code("import os\\nos.system('rm -rf /')") is True


def test_gpia_uses_sandboxed_skill():
    os.environ["SANDBOX_FORCE_LOCAL"] = "1"
    agent = GPIA(verbose=False)
    result = agent.run("Calculate the Fibonacci sequence to 7.")
    cap = agent.get_capsule(result.capsule_id)
    auto = cap.context.get("auto_draft", {})
    assert auto.get("success") is True
    assert auto.get("sandbox_used") == "local"

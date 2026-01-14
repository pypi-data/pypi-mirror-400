from skills.base import SkillContext
from skills.loader import SkillLoader
from skills.registry import get_registry


def test_reflex_patch_proposal_and_validation():
    context = SkillContext(agent_role="test")
    loader = SkillLoader()
    loader.scan_all(lazy=False)
    registry = get_registry()
    synthesizer = registry.get_skill("cognition/proposal-synthesizer")
    validator = registry.get_skill("system/reflex-patch-validator")
    assert synthesizer is not None
    assert validator is not None
    weakness = {"skill": "reasoning/test", "delta": 0.5}

    result = synthesizer.execute(
        {"capability": "draft_reflex_edit_v1", "weakness": weakness},
        context,
    )

    assert result.success is True
    patch = result.output.get("patch")
    assert patch is not None

    validation = validator.execute(
        {"capability": "simulate_shadow_run", "patch": patch},
        context,
    )

    assert validation.success is True
    assert validation.output.get("validation_status") == "SIMULATED"

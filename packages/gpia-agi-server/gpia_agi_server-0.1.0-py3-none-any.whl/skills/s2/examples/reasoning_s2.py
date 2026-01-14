"""
S² Explainable Reasoning - Multi-Scale Decomposition
=====================================================

Demonstrates how to decompose a monolithic skill into S² multi-scale architecture.

Original: reasoning/explainable-reasoning (single L2 macro skill)
S² Decomposed:
  L3 (Meta):  reasoning-orchestrator - Coordinates reasoning workflow
  L2 (Macro): explain-conclusion     - Bundles analysis into explanation
  L1 (Meso):  analyze-premises       - Composes premise analysis
              build-argument         - Constructs logical chain
  L0 (Micro): extract-claims         - Atomic claim extraction
              validate-logic         - Single logic check
              format-step            - Format one reasoning step
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

from ..context_stack import S2ContextStack, ScaleLevel, create_s2_context
from ..composer import S2Composer, CompositionPlan, SkillNode
from ..transforms import S2Projector

logger = logging.getLogger(__name__)


# ==============================================================================
# L0 MICRO SKILLS (Atomic operations, ≤10 tokens each)
# ==============================================================================

def micro_extract_claims(text: str, **kwargs) -> Dict[str, Any]:
    """L0: Extract individual claims from text."""
    # Simple extraction - in production would use NLP
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    claims = []
    for i, sentence in enumerate(sentences[:5]):  # Limit to 5
        if len(sentence) > 10:
            claims.append({
                "id": f"claim_{i}",
                "text": sentence,
                "type": "assertion"
            })
    return {"claims": claims, "count": len(claims)}


def micro_validate_logic(claim_a: str, claim_b: str, relation: str = "implies", **kwargs) -> Dict[str, Any]:
    """L0: Validate logical relationship between two claims."""
    # Simplified logic check
    valid = True
    confidence = 0.8

    # Check for obvious contradictions
    negation_words = ["not", "never", "no", "false"]
    a_neg = any(w in claim_a.lower() for w in negation_words)
    b_neg = any(w in claim_b.lower() for w in negation_words)

    if relation == "implies" and a_neg != b_neg:
        confidence = 0.5  # Potential issue

    return {
        "valid": valid,
        "confidence": confidence,
        "relation": relation,
        "notes": "Basic validation"
    }


def micro_format_step(step_num: int, description: str, justification: str, **kwargs) -> Dict[str, Any]:
    """L0: Format a single reasoning step for output."""
    return {
        "step": step_num,
        "formatted": f"Step {step_num}: {description}\n  Justification: {justification}"
    }


# ==============================================================================
# L1 MESO SKILLS (Composed operations, 30-50 tokens each)
# ==============================================================================

def meso_analyze_premises(
    claims: List[Dict[str, Any]],
    child_results: Optional[List[Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L1: Analyze and validate premises using L0 micros."""
    # Would compose micro_extract_claims and micro_validate_logic
    analyzed = []
    for i, claim in enumerate(claims):
        validation = micro_validate_logic(
            claim.get("text", ""),
            claims[(i + 1) % len(claims)].get("text", "") if len(claims) > 1 else "",
            "supports"
        )
        analyzed.append({
            "claim": claim,
            "validation": validation,
            "is_premise": i < len(claims) // 2
        })

    premises = [a for a in analyzed if a["is_premise"]]
    return {
        "premises": premises,
        "all_valid": all(a["validation"]["valid"] for a in analyzed),
        "avg_confidence": sum(a["validation"]["confidence"] for a in analyzed) / len(analyzed) if analyzed else 0
    }


def meso_build_argument(
    premises: List[Dict[str, Any]],
    conclusion: str,
    child_results: Optional[List[Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L1: Build logical argument chain from premises to conclusion."""
    steps = []
    for i, premise in enumerate(premises):
        step = micro_format_step(
            i + 1,
            premise["claim"]["text"],
            f"Established premise with {premise['validation']['confidence']:.0%} confidence"
        )
        steps.append(step)

    # Add conclusion step
    final_step = micro_format_step(
        len(steps) + 1,
        conclusion,
        "Follows from premises above"
    )
    steps.append(final_step)

    return {
        "argument_chain": steps,
        "step_count": len(steps),
        "is_valid": True
    }


# ==============================================================================
# L2 MACRO SKILL (Bundled workflow, 80-120 tokens)
# ==============================================================================

def macro_explain_conclusion(
    text: str,
    question: str,
    child_results: Optional[List[Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L2: Generate full explanation by composing L1 mesos."""
    # Extract claims
    extraction = micro_extract_claims(text)
    claims = extraction["claims"]

    # Analyze premises
    premise_analysis = meso_analyze_premises(claims)

    # Build argument
    argument = meso_build_argument(
        premise_analysis["premises"],
        question
    )

    # Compose explanation
    explanation_parts = []
    explanation_parts.append(f"Analysis of {len(claims)} claims:")
    for step in argument["argument_chain"]:
        explanation_parts.append(step["formatted"])

    explanation_parts.append(f"\nConclusion: The reasoning is {'valid' if argument['is_valid'] else 'questionable'}")
    explanation_parts.append(f"Confidence: {premise_analysis['avg_confidence']:.0%}")

    return {
        "explanation": "\n".join(explanation_parts),
        "claims_found": len(claims),
        "premises_valid": premise_analysis["all_valid"],
        "confidence": premise_analysis["avg_confidence"],
        "steps": argument["step_count"]
    }


# ==============================================================================
# L3 META SKILL (Orchestrator)
# ==============================================================================

def meta_reasoning_orchestrator(
    task: str,
    context: Optional[Dict[str, Any]] = None,
    child_results: Optional[List[Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L3: Orchestrate the full reasoning workflow."""
    context = context or {}

    # Parse task to determine what kind of reasoning is needed
    text = context.get("text", task)
    question = context.get("question", "What is the conclusion?")

    # Execute the macro skill
    result = macro_explain_conclusion(text, question)

    # Add orchestration metadata
    result["orchestrated"] = True
    result["task"] = task
    result["workflow"] = "S2_explainable_reasoning"

    return result


# ==============================================================================
# S² COMPOSITION SETUP
# ==============================================================================

def create_reasoning_composer() -> S2Composer:
    """Create an S2Composer configured for explainable reasoning."""
    composer = S2Composer()

    # Register all skills at their appropriate scales
    # L0 Micros
    composer.register_skill("reasoning/extract-claims", micro_extract_claims, ScaleLevel.L0)
    composer.register_skill("reasoning/validate-logic", micro_validate_logic, ScaleLevel.L0)
    composer.register_skill("reasoning/format-step", micro_format_step, ScaleLevel.L0)

    # L1 Mesos
    composer.register_skill("reasoning/analyze-premises", meso_analyze_premises, ScaleLevel.L1)
    composer.register_skill("reasoning/build-argument", meso_build_argument, ScaleLevel.L1)

    # L2 Macro
    composer.register_skill("reasoning/explain-conclusion", macro_explain_conclusion, ScaleLevel.L2)

    # L3 Meta
    composer.register_skill("reasoning/orchestrator", meta_reasoning_orchestrator, ScaleLevel.L3)

    return composer


def get_reasoning_skill_tree() -> Dict[str, List[str]]:
    """Get the skill tree for reasoning decomposition."""
    return {
        "reasoning/orchestrator": ["reasoning/explain-conclusion"],
        "reasoning/explain-conclusion": ["reasoning/analyze-premises", "reasoning/build-argument"],
        "reasoning/analyze-premises": ["reasoning/extract-claims", "reasoning/validate-logic"],
        "reasoning/build-argument": ["reasoning/format-step"],
    }


# ==============================================================================
# EXAMPLE EXECUTION
# ==============================================================================

def run_example():
    """Run an example S² reasoning workflow."""
    print("=" * 60)
    print("S2 EXPLAINABLE REASONING EXAMPLE")
    print("=" * 60)

    # Create composer for planning
    composer = create_reasoning_composer()
    skill_tree = get_reasoning_skill_tree()

    # Create execution plan (for visualization and planning)
    plan = composer.create_plan(
        goal="Analyze and explain reasoning in text",
        meta_skill_id="reasoning/orchestrator",
        skill_tree=skill_tree
    )

    print(f"\nExecution Plan:")
    print(f"  Goal: {plan.goal}")
    print(f"  Skills: {[s for _, s in plan.flatten()]}")
    print(f"  Estimated tokens: {plan.estimated_tokens}")

    # Create context with sample text
    context = create_s2_context(
        goal="Explain reasoning",
        initial_data={
            "text": "All humans are mortal. Socrates is a human. Therefore Socrates is mortal.",
            "question": "Is the conclusion valid?"
        }
    )

    # Execute using orchestrator-driven model
    # The orchestrator internally calls lower-level skills
    print("\nExecuting S2 workflow (orchestrator-driven)...")

    import time
    start = time.time()

    # Push to meta level for tracking
    context.push(ScaleLevel.L3)

    # Execute the orchestrator which orchestrates internally
    result = meta_reasoning_orchestrator(
        task="Analyze reasoning in provided text",
        context=context.get_context()
    )

    # Record execution at meta level
    context.add_result(result)
    context.record_skill("reasoning/orchestrator")

    execution_time = int((time.time() - start) * 1000)

    print(f"\nExecution complete in {execution_time}ms")
    print(f"Context summary: {context.get_execution_summary()['total_skills']} skills tracked")

    # Show result
    if "explanation" in result:
        print(f"\n--- EXPLANATION ---")
        print(result["explanation"])
        print(f"-------------------")
        print(f"Confidence: {result.get('confidence', 0):.0%}")
        print(f"Workflow: {result.get('workflow', 'unknown')}")

    return result


def run_example_with_composer():
    """Run example using full composer execution (for testing composition)."""
    print("=" * 60)
    print("S2 REASONING - COMPOSER EXECUTION")
    print("=" * 60)

    composer = create_reasoning_composer()
    skill_tree = get_reasoning_skill_tree()

    plan = composer.create_plan(
        goal="Test composer execution",
        meta_skill_id="reasoning/orchestrator",
        skill_tree=skill_tree
    )

    context = create_s2_context(
        goal="Explain reasoning",
        initial_data={
            "text": "All humans are mortal. Socrates is a human. Therefore Socrates is mortal.",
            "question": "Is the conclusion valid?"
        }
    )

    # Custom executor that handles internal orchestration
    def orchestrated_executor(skill_id: str, inputs: dict, ctx: S2ContextStack):
        """Execute skills allowing internal orchestration."""
        info = composer.skill_registry.get(skill_id)
        if not info:
            return {"error": f"Skill not found: {skill_id}"}

        skill = info["skill"]
        merged_context = ctx.get_context()

        # For macro/meta skills, pass context and let them orchestrate internally
        if skill_id in ["reasoning/orchestrator", "reasoning/explain-conclusion"]:
            if skill_id == "reasoning/orchestrator":
                return skill(task=merged_context.get("goal", "analyze"), context=merged_context)
            else:
                return skill(
                    text=merged_context.get("text", ""),
                    question=merged_context.get("question", "")
                )

        # For lower-level skills, they're called internally by higher levels
        # Just return empty success (they were already executed)
        return {"status": "executed_internally", "skill": skill_id}

    result = composer.execute(plan, context, executor=orchestrated_executor)

    print(f"\nExecution time: {result['execution_time_ms']}ms")
    print(f"Skills in tree: {list(result['all_results'].keys())}")

    # Get the orchestrator result
    final = result["all_results"].get("reasoning/orchestrator", {})
    if "explanation" in final:
        print(f"\n--- EXPLANATION ---")
        print(final["explanation"])
        print(f"-------------------")

    return result


if __name__ == "__main__":
    run_example()

"""
S2 Hybrid Orchestrator - Multi-Scale Decomposition
===================================================

Demonstrates S2 decomposition of the automation/hybrid-orchestrator skill.

Original: automation/hybrid-orchestrator (single L2 macro skill)
S2 Decomposed:
  L3 (Meta):  workflow-coordinator    - Top-level workflow management
  L2 (Macro): plan-workflow           - Create execution plan from task
              execute-workflow        - Run workflow with checkpoints
              summarize-results       - Aggregate and report outcomes
  L1 (Meso):  decompose-task          - Break task into steps
              validate-step           - Check step preconditions
              handle-handoff          - Manage step transitions
  L0 (Micro): parse-intent            - Extract action type from step
              check-precondition      - Verify single condition
              format-result           - Format step output
              log-checkpoint          - Record execution checkpoint
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import logging
import time
import json

from ..context_stack import S2ContextStack, ScaleLevel, create_s2_context
from ..composer import S2Composer, CompositionPlan

logger = logging.getLogger(__name__)


# ==============================================================================
# L0 MICRO SKILLS (Atomic operations, <=10 tokens each)
# ==============================================================================

def micro_parse_intent(step_description: str, **kwargs) -> Dict[str, Any]:
    """L0: Extract action type from step description."""
    # Simple keyword-based intent extraction
    keywords = {
        "retrieve": ["get", "fetch", "retrieve", "load", "read"],
        "analyze": ["analyze", "process", "check", "validate", "evaluate"],
        "transform": ["transform", "convert", "format", "map", "modify"],
        "store": ["save", "store", "write", "persist", "cache"],
        "notify": ["notify", "alert", "send", "email", "message"],
    }

    step_lower = step_description.lower()
    detected_intent = "unknown"
    confidence = 0.5

    for intent, words in keywords.items():
        for word in words:
            if word in step_lower:
                detected_intent = intent
                confidence = 0.9
                break
        if detected_intent != "unknown":
            break

    return {
        "intent": detected_intent,
        "confidence": confidence,
        "original": step_description
    }


def micro_check_precondition(
    condition: str,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L0: Verify a single precondition."""
    context = context or {}

    # Simulate precondition checks
    is_met = True
    reason = "Condition satisfied"

    # Check for common preconditions
    if "requires_auth" in condition.lower():
        is_met = context.get("authenticated", True)
        reason = "Authentication check" if is_met else "Authentication required"
    elif "file_exists" in condition.lower():
        is_met = context.get("file_available", True)
        reason = "File availability check"
    elif "connection" in condition.lower():
        is_met = context.get("connected", True)
        reason = "Connection check"

    return {
        "condition": condition,
        "is_met": is_met,
        "reason": reason
    }


def micro_format_result(
    step_name: str,
    output: Any,
    status: str = "success",
    **kwargs
) -> Dict[str, Any]:
    """L0: Format step output for workflow result."""
    return {
        "step": step_name,
        "status": status,
        "output": output if isinstance(output, (str, int, float, bool, list, dict)) else str(output),
        "formatted": f"[{status.upper()}] {step_name}: {str(output)[:100]}"
    }


def micro_log_checkpoint(
    checkpoint_id: str,
    step_name: str,
    state: str = "reached",
    **kwargs
) -> Dict[str, Any]:
    """L0: Record execution checkpoint."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "checkpoint_id": checkpoint_id,
        "step": step_name,
        "state": state,
        "timestamp": timestamp,
        "logged": True
    }


# ==============================================================================
# L1 MESO SKILLS (Composed operations, 30-50 tokens each)
# ==============================================================================

def meso_decompose_task(
    task: str,
    max_steps: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """L1: Break task into executable steps."""
    # Parse intent to understand task type
    intent = micro_parse_intent(task)

    # Generate steps based on task (simplified decomposition)
    steps = []

    # Default workflow pattern based on intent
    patterns = {
        "retrieve": ["validate_source", "fetch_data", "validate_data", "return_result"],
        "analyze": ["load_data", "preprocess", "analyze", "generate_report"],
        "transform": ["load_input", "validate_schema", "transform", "validate_output", "save_result"],
        "store": ["validate_data", "prepare_storage", "write_data", "confirm_write"],
        "unknown": ["parse_task", "execute_action", "verify_result"],
    }

    step_names = patterns.get(intent["intent"], patterns["unknown"])[:max_steps]

    for i, step_name in enumerate(step_names):
        step_intent = micro_parse_intent(step_name)
        steps.append({
            "id": f"step_{i+1}",
            "name": step_name,
            "order": i + 1,
            "intent": step_intent["intent"],
            "dependencies": [f"step_{i}"] if i > 0 else []
        })

    return {
        "task": task,
        "task_intent": intent["intent"],
        "steps": steps,
        "step_count": len(steps),
        "is_parallel": False  # Could analyze dependencies for parallelism
    }


def meso_validate_step(
    step: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L1: Check step preconditions before execution."""
    context = context or {}

    # Define preconditions based on step type
    preconditions = []
    if step.get("intent") == "retrieve":
        preconditions = ["connection_available", "source_accessible"]
    elif step.get("intent") == "store":
        preconditions = ["target_writable", "data_valid"]
    elif step.get("intent") == "analyze":
        preconditions = ["data_loaded", "resources_available"]

    # Check all preconditions
    results = []
    all_met = True
    for precond in preconditions:
        check = micro_check_precondition(precond, context)
        results.append(check)
        if not check["is_met"]:
            all_met = False

    return {
        "step_id": step.get("id", "unknown"),
        "step_name": step.get("name", "unknown"),
        "preconditions_checked": len(preconditions),
        "all_met": all_met,
        "checks": results,
        "can_proceed": all_met
    }


def meso_handle_handoff(
    from_step: Dict[str, Any],
    to_step: Dict[str, Any],
    result: Any,
    **kwargs
) -> Dict[str, Any]:
    """L1: Manage transition between workflow steps."""
    # Log checkpoint at handoff point
    checkpoint = micro_log_checkpoint(
        checkpoint_id=f"handoff_{from_step.get('id', '?')}_{to_step.get('id', '?')}",
        step_name=from_step.get("name", "unknown"),
        state="completed"
    )

    # Format the handoff data
    handoff_data = {
        "from_step": from_step.get("id"),
        "to_step": to_step.get("id"),
        "data_transferred": result is not None,
        "checkpoint": checkpoint,
        "handoff_successful": True
    }

    return handoff_data


# ==============================================================================
# L2 MACRO SKILLS (Bundled workflows, 80-120 tokens)
# ==============================================================================

def macro_plan_workflow(
    task: str,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L2: Create execution plan from task description."""
    options = options or {}

    # Decompose task into steps
    decomposition = meso_decompose_task(
        task,
        max_steps=options.get("max_steps", 5)
    )

    # Validate each step can be executed
    validations = []
    for step in decomposition["steps"]:
        validation = meso_validate_step(step, options.get("context"))
        validations.append(validation)

    all_valid = all(v["can_proceed"] for v in validations)

    # Build execution plan
    plan = {
        "task": task,
        "intent": decomposition["task_intent"],
        "steps": decomposition["steps"],
        "step_count": decomposition["step_count"],
        "validations": validations,
        "is_valid": all_valid,
        "checkpoints": [f"after_step_{i+1}" for i in range(len(decomposition["steps"]))],
        "estimated_duration_ms": len(decomposition["steps"]) * 100
    }

    return plan


def macro_execute_workflow(
    plan: Dict[str, Any],
    executors: Optional[Dict[str, Callable]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L2: Run workflow with checkpoints and validation gates."""
    executors = executors or {}
    results = []
    checkpoints = []
    errors = []

    steps = plan.get("steps", [])
    prev_result = None

    for i, step in enumerate(steps):
        step_start = time.time()

        # Check if we can proceed
        validation = meso_validate_step(step)
        if not validation["can_proceed"]:
            errors.append({
                "step": step["id"],
                "error": "Precondition not met",
                "details": validation
            })
            break

        # Execute step (simulated)
        executor = executors.get(step["name"])
        if executor:
            try:
                step_result = executor(prev_result)
            except Exception as e:
                step_result = {"error": str(e)}
                errors.append({"step": step["id"], "error": str(e)})
        else:
            # Default simulation
            step_result = f"Completed {step['name']}"

        # Format and record result
        formatted = micro_format_result(step["name"], step_result)
        results.append(formatted)
        prev_result = step_result

        # Log checkpoint
        checkpoint = micro_log_checkpoint(
            checkpoint_id=f"cp_{i+1}",
            step_name=step["name"],
            state="completed"
        )
        checkpoints.append(checkpoint)

        # Handle handoff to next step
        if i < len(steps) - 1:
            handoff = meso_handle_handoff(step, steps[i+1], step_result)

    execution_time = sum(100 for _ in results)  # Simulated timing

    return {
        "task": plan.get("task", "unknown"),
        "steps_executed": len(results),
        "total_steps": len(steps),
        "results": results,
        "checkpoints": checkpoints,
        "errors": errors,
        "success": len(errors) == 0,
        "execution_time_ms": execution_time
    }


def macro_summarize_results(
    execution: Dict[str, Any],
    include_details: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """L2: Aggregate and report workflow outcomes."""
    results = execution.get("results", [])
    errors = execution.get("errors", [])
    checkpoints = execution.get("checkpoints", [])

    # Build summary
    summary = {
        "task": execution.get("task", "unknown"),
        "outcome": "success" if execution.get("success") else "failed",
        "steps_completed": execution.get("steps_executed", 0),
        "total_steps": execution.get("total_steps", 0),
        "completion_rate": f"{100 * execution.get('steps_executed', 0) / max(1, execution.get('total_steps', 1)):.0f}%",
        "errors_count": len(errors),
        "checkpoints_logged": len(checkpoints),
        "execution_time_ms": execution.get("execution_time_ms", 0)
    }

    if include_details:
        summary["step_outputs"] = [
            f"{r['step']}: {r['status']}"
            for r in results
        ]
        if errors:
            summary["error_details"] = [
                f"{e['step']}: {e['error']}"
                for e in errors
            ]

    # Generate human-readable report
    report_lines = [
        f"Workflow: {summary['task']}",
        f"Outcome: {summary['outcome'].upper()}",
        f"Progress: {summary['steps_completed']}/{summary['total_steps']} steps ({summary['completion_rate']})",
        f"Duration: {summary['execution_time_ms']}ms"
    ]

    if summary["errors_count"] > 0:
        report_lines.append(f"Errors: {summary['errors_count']}")

    summary["report"] = "\n".join(report_lines)

    return summary


# ==============================================================================
# L3 META SKILL (Orchestrator)
# ==============================================================================

def meta_workflow_coordinator(
    task: str,
    options: Optional[Dict[str, Any]] = None,
    executors: Optional[Dict[str, Callable]] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L3: Top-level workflow management and coordination."""
    options = options or {}
    context = context or {}

    # Phase 1: Plan
    plan = macro_plan_workflow(task, options)

    if not plan["is_valid"]:
        return {
            "orchestrated": True,
            "workflow": "S2_hybrid_orchestrator",
            "phase": "planning",
            "success": False,
            "error": "Workflow validation failed",
            "plan": plan
        }

    # Phase 2: Execute
    execution = macro_execute_workflow(plan, executors)

    # Phase 3: Summarize
    summary = macro_summarize_results(execution)

    return {
        "orchestrated": True,
        "workflow": "S2_hybrid_orchestrator",
        "success": execution.get("success", False),
        "plan": plan,
        "execution": execution,
        "summary": summary,
        "report": summary.get("report", "")
    }


# ==============================================================================
# S2 COMPOSITION SETUP
# ==============================================================================

def create_orchestrator_composer() -> S2Composer:
    """Create an S2Composer configured for hybrid orchestration."""
    composer = S2Composer()

    # L0 Micros
    composer.register_skill("orchestrator/parse-intent", micro_parse_intent, ScaleLevel.L0)
    composer.register_skill("orchestrator/check-precondition", micro_check_precondition, ScaleLevel.L0)
    composer.register_skill("orchestrator/format-result", micro_format_result, ScaleLevel.L0)
    composer.register_skill("orchestrator/log-checkpoint", micro_log_checkpoint, ScaleLevel.L0)

    # L1 Mesos
    composer.register_skill("orchestrator/decompose-task", meso_decompose_task, ScaleLevel.L1)
    composer.register_skill("orchestrator/validate-step", meso_validate_step, ScaleLevel.L1)
    composer.register_skill("orchestrator/handle-handoff", meso_handle_handoff, ScaleLevel.L1)

    # L2 Macros
    composer.register_skill("orchestrator/plan-workflow", macro_plan_workflow, ScaleLevel.L2)
    composer.register_skill("orchestrator/execute-workflow", macro_execute_workflow, ScaleLevel.L2)
    composer.register_skill("orchestrator/summarize-results", macro_summarize_results, ScaleLevel.L2)

    # L3 Meta
    composer.register_skill("orchestrator/coordinator", meta_workflow_coordinator, ScaleLevel.L3)

    return composer


def get_orchestrator_skill_tree() -> Dict[str, List[str]]:
    """Get the skill tree for orchestrator decomposition."""
    return {
        "orchestrator/coordinator": [
            "orchestrator/plan-workflow",
            "orchestrator/execute-workflow",
            "orchestrator/summarize-results"
        ],
        "orchestrator/plan-workflow": [
            "orchestrator/decompose-task",
            "orchestrator/validate-step"
        ],
        "orchestrator/execute-workflow": [
            "orchestrator/validate-step",
            "orchestrator/handle-handoff"
        ],
        "orchestrator/summarize-results": [
            "orchestrator/format-result"
        ],
        "orchestrator/decompose-task": [
            "orchestrator/parse-intent"
        ],
        "orchestrator/validate-step": [
            "orchestrator/check-precondition"
        ],
        "orchestrator/handle-handoff": [
            "orchestrator/log-checkpoint",
            "orchestrator/format-result"
        ],
    }


# ==============================================================================
# EXAMPLE EXECUTION
# ==============================================================================

def run_example():
    """Run an example S2 hybrid orchestrator workflow."""
    print("=" * 60)
    print("S2 HYBRID ORCHESTRATOR EXAMPLE")
    print("=" * 60)

    # Create composer for planning
    composer = create_orchestrator_composer()
    skill_tree = get_orchestrator_skill_tree()

    # Create execution plan
    plan = composer.create_plan(
        goal="Coordinate multi-step workflow",
        meta_skill_id="orchestrator/coordinator",
        skill_tree=skill_tree
    )

    print(f"\nExecution Plan:")
    print(f"  Goal: {plan.goal}")
    print(f"  Skills: {len([s for _, s in plan.flatten()])} skills in tree")
    print(f"  Estimated tokens: {plan.estimated_tokens}")

    # Example task
    task = "Retrieve user data, analyze patterns, and generate report"

    print(f"\n--- TASK ---")
    print(f"  {task}")

    # Execute workflow
    print("\n--- EXECUTING WORKFLOW ---")
    result = meta_workflow_coordinator(
        task=task,
        options={"max_steps": 4, "context": {"authenticated": True}}
    )

    print(f"\nWorkflow: {result['workflow']}")
    print(f"Success: {result['success']}")

    # Show plan
    print(f"\n--- PLAN ---")
    print(f"  Intent: {result['plan']['intent']}")
    print(f"  Steps: {result['plan']['step_count']}")
    for step in result['plan']['steps']:
        print(f"    {step['order']}. {step['name']} ({step['intent']})")

    # Show execution
    print(f"\n--- EXECUTION ---")
    exec_result = result['execution']
    print(f"  Steps completed: {exec_result['steps_executed']}/{exec_result['total_steps']}")
    for r in exec_result['results']:
        print(f"    {r['formatted']}")

    # Show summary
    print(f"\n--- SUMMARY ---")
    print(result['summary']['report'])

    print("\n" + "=" * 60)
    print("S2 Hybrid Orchestrator workflow complete!")

    return result


if __name__ == "__main__":
    run_example()

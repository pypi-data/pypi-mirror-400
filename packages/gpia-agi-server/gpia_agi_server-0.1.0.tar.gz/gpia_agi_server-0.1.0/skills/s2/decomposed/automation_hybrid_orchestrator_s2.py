"""
S2 Decomposed: Hybrid Orchestrator
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: automation/hybrid-orchestrator
Concept: Meta-controller that routes tasks between deterministic code, probabilistic LLMs, and external APIs

Scale structure:
  L0 (Micro): 6 operations
  L1 (Meso): 2 operations
  L2 (Macro): 1 operations
  L3 (Meta): 1 orchestrator

Model routing (5 LLM Partners: codegemma, qwen3, deepseek_r1, llava, gpt_oss_20b):
  L0 -> text:codegemma | reasoning:codegemma
  L1 -> text:qwen3 | reasoning:deepseek_r1
  L2 -> text:qwen3 | synthesis:gpt_oss_20b
  L3 -> text:deepseek_r1 | synthesis:gpt_oss_20b
"""


# Skill metadata
SKILL_METADATA = {
    "original_id": "automation/hybrid-orchestrator",
    "original_name": "Hybrid Orchestrator",
    "concept": "Meta-controller that routes tasks between deterministic code, probabilistic LLMs, and external APIs",
    "scale_structure": {
    "L0": [
        "analyze_task_complexity: Classify incoming prompt as simple (rule-based) or complex (agentic)",
        "decompose_to_dag: Break a complex goal into a Directed Acyclic Graph of sub-tasks",
        "select_execution_engine: Determine if sub-task needs Python script, SQL query, or LLM call",
        "dispatch_subtask: Send a unit of work to the selected engine",
        "aggregate_branch_results: Combine outputs from parallel execution branches",
        "handle_execution_failure: Trigger retry logic or fallback path upon error"
    ],
    "L1": [
        "plan_execution_strategy: Analyze complexity and decompose into DAG",
        "execute_task_branch: Select engine, dispatch, and handle results"
    ],
    "L2": [
        "orchestrate_hybrid_workflow: Complete task routing and execution"
    ],
    "L3": [
        "automation_hybrid-orchestrator_orchestrator"
    ]
},
    "skill_tree": {
    "automation/hybrid_orchestrator/orchestrator": [
        "automation/hybrid_orchestrator/orchestrate_hybrid_workflow"
    ],
    "automation/hybrid_orchestrator/orchestrate_hybrid_workflow": [
        "automation/hybrid_orchestrator/plan_execution_strategy",
        "automation/hybrid_orchestrator/execute_task_branch",
        "automation/hybrid_orchestrator/aggregate_branch_results"
    ],
    "automation/hybrid_orchestrator/plan_execution_strategy": [
        "automation/hybrid_orchestrator/analyze_task_complexity",
        "automation/hybrid_orchestrator/decompose_to_dag"
    ],
    "automation/hybrid_orchestrator/execute_task_branch": [
        "automation/hybrid_orchestrator/select_execution_engine",
        "automation/hybrid_orchestrator/dispatch_subtask",
        "automation/hybrid_orchestrator/handle_execution_failure"
    ]
},
    "model_routing": {
    "L0": {
        "text": "codegemma",
        "visual": "codegemma",
        "reasoning": "codegemma",
        "synthesis": "qwen3"
    },
    "L1": {
        "text": "qwen3",
        "visual": "qwen3",
        "reasoning": "deepseek_r1",
        "synthesis": "qwen3"
    },
    "L2": {
        "text": "qwen3",
        "visual": "qwen3",
        "reasoning": "deepseek_r1",
        "synthesis": "gpt_oss_20b"
    },
    "L3": {
        "text": "deepseek_r1",
        "visual": "deepseek_r1",
        "reasoning": "deepseek_r1",
        "synthesis": "gpt_oss_20b"
    }
},
}

"""
S2 Decomposed: Guardrails Control
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: governance/guardrails-control
Concept: Safety valve between user input and model output to prevent unsafe interactions

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
    "original_id": "governance/guardrails-control",
    "original_name": "Guardrails Control",
    "concept": "Safety valve between user input and model output to prevent unsafe interactions",
    "scale_structure": {
    "L0": [
        "intercept_input_stream: Capture user prompt before LLM inference",
        "scan_pii_patterns: Regex/model check for emails, SSNs, credit cards",
        "check_topic_allowlist: Verify subject matter matches allowed domain",
        "filter_output_stream: Scan generated text for banned keywords or tone",
        "truncate_response: Cut off output if safety threshold crossed",
        "inject_safety_preamble: Prepend required system instructions dynamically"
    ],
    "L1": [
        "validate_input: Intercept, scan PII, check allowlist",
        "sanitize_output: Filter, truncate, and inject safety preamble"
    ],
    "L2": [
        "enforce_guardrails: Complete input/output safety enforcement"
    ],
    "L3": [
        "governance_guardrails-control_orchestrator"
    ]
},
    "skill_tree": {
    "governance/guardrails_control/orchestrator": [
        "governance/guardrails_control/enforce_guardrails"
    ],
    "governance/guardrails_control/enforce_guardrails": [
        "governance/guardrails_control/validate_input",
        "governance/guardrails_control/sanitize_output"
    ],
    "governance/guardrails_control/validate_input": [
        "governance/guardrails_control/intercept_input_stream",
        "governance/guardrails_control/scan_pii_patterns",
        "governance/guardrails_control/check_topic_allowlist"
    ],
    "governance/guardrails_control/sanitize_output": [
        "governance/guardrails_control/filter_output_stream",
        "governance/guardrails_control/truncate_response",
        "governance/guardrails_control/inject_safety_preamble"
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

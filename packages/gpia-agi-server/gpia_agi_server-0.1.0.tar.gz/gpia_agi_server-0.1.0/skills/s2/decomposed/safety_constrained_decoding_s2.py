"""
S2 Decomposed: Constrained Decoding
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: safety/constrained-decoding
Concept: Forcing LLM to output exactly what is needed (e.g., valid JSON) by manipulating logit probabilities

Scale structure:
  L0 (Micro): 6 operations
  L1 (Meso): 3 operations
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
    "original_id": "safety/constrained-decoding",
    "original_name": "Constrained Decoding",
    "concept": "Forcing LLM to output exactly what is needed (e.g., valid JSON) by manipulating logit probabilities",
    "scale_structure": {
    "L0": [
        "load_grammar_schema: Ingest JSON Schema or BNF grammar",
        "calculate_token_mask: Determine which tokens are valid next-steps",
        "suppress_invalid_logits: Set probability of invalid tokens to -infinity",
        "enforce_stop_sequence: Hard stop generation at specific delimiters",
        "validate_partial_json: Check if incomplete stream is still valid JSON",
        "apply_repetition_penalty: Reduce probability of looping phrases"
    ],
    "L1": [
        "prepare_constraints: Load grammar and calculate token mask",
        "apply_constraints: Suppress invalid logits and enforce stop sequence",
        "validate_output: Validate partial JSON and apply repetition penalty"
    ],
    "L2": [
        "constrained_generation: Complete constrained decoding pipeline"
    ],
    "L3": [
        "safety_constrained-decoding_orchestrator"
    ]
},
    "skill_tree": {
    "safety/constrained_decoding/orchestrator": [
        "safety/constrained_decoding/constrained_generation"
    ],
    "safety/constrained_decoding/constrained_generation": [
        "safety/constrained_decoding/prepare_constraints",
        "safety/constrained_decoding/apply_constraints",
        "safety/constrained_decoding/validate_output"
    ],
    "safety/constrained_decoding/prepare_constraints": [
        "safety/constrained_decoding/load_grammar_schema",
        "safety/constrained_decoding/calculate_token_mask"
    ],
    "safety/constrained_decoding/apply_constraints": [
        "safety/constrained_decoding/suppress_invalid_logits",
        "safety/constrained_decoding/enforce_stop_sequence"
    ],
    "safety/constrained_decoding/validate_output": [
        "safety/constrained_decoding/validate_partial_json",
        "safety/constrained_decoding/apply_repetition_penalty"
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

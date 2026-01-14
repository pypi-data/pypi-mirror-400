"""
S2 Decomposed: Explainable Reasoning
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: reasoning/explainable-reasoning
Concept: Converting opaque model weights/decisions into human-readable rationale

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
    "original_id": "reasoning/explainable-reasoning",
    "original_name": "Explainable Reasoning",
    "concept": "Converting opaque model weights/decisions into human-readable rationale",
    "scale_structure": {
    "L0": [
        "trace_chain_of_thought: Log intermediate reasoning steps of the LLM",
        "extract_key_features: Identify which input tokens had highest attention weights",
        "generate_counterfactual: 'What if' analysis - how result changes if input changes",
        "summarize_decision_logic: Translate technical trace into natural language",
        "link_source_citations: Connect claims in output to source documents",
        "format_explanation_tree: JSON structure of the logic path"
    ],
    "L1": [
        "trace_reasoning: Trace chain of thought and extract key features",
        "explain_decision: Generate counterfactual and summarize logic",
        "document_explanation: Link citations and format tree"
    ],
    "L2": [
        "generate_xai_report: Complete explainable reasoning pipeline"
    ],
    "L3": [
        "reasoning_explainable-reasoning_orchestrator"
    ]
},
    "skill_tree": {
    "reasoning/explainable_reasoning/orchestrator": [
        "reasoning/explainable_reasoning/generate_xai_report"
    ],
    "reasoning/explainable_reasoning/generate_xai_report": [
        "reasoning/explainable_reasoning/trace_reasoning",
        "reasoning/explainable_reasoning/explain_decision",
        "reasoning/explainable_reasoning/document_explanation"
    ],
    "reasoning/explainable_reasoning/trace_reasoning": [
        "reasoning/explainable_reasoning/trace_chain_of_thought",
        "reasoning/explainable_reasoning/extract_key_features"
    ],
    "reasoning/explainable_reasoning/explain_decision": [
        "reasoning/explainable_reasoning/generate_counterfactual",
        "reasoning/explainable_reasoning/summarize_decision_logic"
    ],
    "reasoning/explainable_reasoning/document_explanation": [
        "reasoning/explainable_reasoning/link_source_citations",
        "reasoning/explainable_reasoning/format_explanation_tree"
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

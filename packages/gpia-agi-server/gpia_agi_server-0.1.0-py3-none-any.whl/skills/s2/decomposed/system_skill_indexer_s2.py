"""
S2 Decomposed: Skill Indexer
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: system/skill-indexer
Concept: Registry system that allows Orchestrator to know what tools are available

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
    "original_id": "system/skill-indexer",
    "original_name": "Skill Indexer",
    "concept": "Registry system that allows Orchestrator to know what tools are available",
    "scale_structure": {
    "L0": [
        "parse_skill_manifest: Read SKILL.md YAML/Frontmatter",
        "validate_skill_schema: Ensure required fields (inputs, outputs) exist",
        "generate_skill_description_embedding: Vectorize the 'What does this do?' text",
        "register_skill_endpoint: Map function name to execution path/API",
        "update_skill_metadata: Refresh version numbers or parameters",
        "optimize_retrieval_index: Rebalance vector tree for faster search"
    ],
    "L1": [
        "parse_and_validate: Parse manifest and validate schema",
        "index_skill: Generate embedding and register endpoint",
        "maintain_index: Update metadata and optimize retrieval"
    ],
    "L2": [
        "index_skill_catalog: Complete skill indexing pipeline"
    ],
    "L3": [
        "system_skill-indexer_orchestrator"
    ]
},
    "skill_tree": {
    "system/skill_indexer/orchestrator": [
        "system/skill_indexer/index_skill_catalog"
    ],
    "system/skill_indexer/index_skill_catalog": [
        "system/skill_indexer/parse_and_validate",
        "system/skill_indexer/index_skill",
        "system/skill_indexer/maintain_index"
    ],
    "system/skill_indexer/parse_and_validate": [
        "system/skill_indexer/parse_skill_manifest",
        "system/skill_indexer/validate_skill_schema"
    ],
    "system/skill_indexer/index_skill": [
        "system/skill_indexer/generate_skill_description_embedding",
        "system/skill_indexer/register_skill_endpoint"
    ],
    "system/skill_indexer/maintain_index": [
        "system/skill_indexer/update_skill_metadata",
        "system/skill_indexer/optimize_retrieval_index"
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

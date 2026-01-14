"""
S2 Decomposed: Memory Linker
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: conscience/memory-linker
Concept: Converting linear interaction logs into graph structure by linking related entities

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
    "original_id": "conscience/memory-linker",
    "original_name": "Memory Linker",
    "concept": "Converting linear interaction logs into graph structure by linking related entities",
    "scale_structure": {
    "L0": [
        "extract_named_entities: Identify People, Places, Concepts in text",
        "query_existing_nodes: Check graph for pre-existing entities (fuzzy match)",
        "calculate_semantic_affinity: Determine strength of relationship between two nodes",
        "create_edge_relationship: Define edge type (IS_A, WORKED_WITH, LOCATED_IN)",
        "merge_duplicate_nodes: Fuse two nodes identified as the same entity",
        "decay_edge_weight: Reduce importance of links not reinforced recently"
    ],
    "L1": [
        "extract_and_match_entities: Extract entities and query existing nodes",
        "build_relationship_graph: Calculate affinity and create edges"
    ],
    "L2": [
        "link_memory_graph: Complete entity extraction to graph linking"
    ],
    "L3": [
        "conscience_memory-linker_orchestrator"
    ]
},
    "skill_tree": {
    "conscience/memory_linker/orchestrator": [
        "conscience/memory_linker/link_memory_graph"
    ],
    "conscience/memory_linker/link_memory_graph": [
        "conscience/memory_linker/extract_and_match_entities",
        "conscience/memory_linker/build_relationship_graph",
        "conscience/memory_linker/decay_edge_weight"
    ],
    "conscience/memory_linker/extract_and_match_entities": [
        "conscience/memory_linker/extract_named_entities",
        "conscience/memory_linker/query_existing_nodes",
        "conscience/memory_linker/merge_duplicate_nodes"
    ],
    "conscience/memory_linker/build_relationship_graph": [
        "conscience/memory_linker/calculate_semantic_affinity",
        "conscience/memory_linker/create_edge_relationship"
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

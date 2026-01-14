"""
S2 Decomposed: Embedding Repair
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: conscience/embedding-repair
Concept: Diagnosing and fixing vector store degradation where semantic search results have become irrelevant

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
    "original_id": "conscience/embedding-repair",
    "original_name": "Embedding Repair",
    "concept": "Diagnosing and fixing vector store degradation where semantic search results have become irrelevant",
    "scale_structure": {
    "L0": [
        "assess_cluster_cohesion: Measure density of vector clusters to find loose/drifted points",
        "identify_retrieval_gaps: Log queries that returned low-confidence scores",
        "generate_synthetic_anchor: Create ideal 'golden' embedding for a specific concept",
        "reindex_vector_batch: Force refresh of embeddings for specific document set",
        "prune_orphan_vectors: Remove vectors that no longer link to valid source documents",
        "validate_repair_distance: Compare pre-fix and post-fix cosine similarity"
    ],
    "L1": [
        "diagnose_embedding_health: Assess clusters and identify retrieval gaps",
        "repair_vectors: Generate anchors, reindex, and prune orphans"
    ],
    "L2": [
        "full_embedding_repair: Complete diagnosis and repair cycle"
    ],
    "L3": [
        "conscience_embedding-repair_orchestrator"
    ]
},
    "skill_tree": {
    "conscience/embedding_repair/orchestrator": [
        "conscience/embedding_repair/full_embedding_repair"
    ],
    "conscience/embedding_repair/full_embedding_repair": [
        "conscience/embedding_repair/diagnose_embedding_health",
        "conscience/embedding_repair/repair_vectors",
        "conscience/embedding_repair/validate_repair_distance"
    ],
    "conscience/embedding_repair/diagnose_embedding_health": [
        "conscience/embedding_repair/assess_cluster_cohesion",
        "conscience/embedding_repair/identify_retrieval_gaps"
    ],
    "conscience/embedding_repair/repair_vectors": [
        "conscience/embedding_repair/generate_synthetic_anchor",
        "conscience/embedding_repair/reindex_vector_batch",
        "conscience/embedding_repair/prune_orphan_vectors"
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

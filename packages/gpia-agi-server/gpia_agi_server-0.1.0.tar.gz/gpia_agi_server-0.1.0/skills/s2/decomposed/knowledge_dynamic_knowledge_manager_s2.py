"""
S2 Decomposed: Dynamic Knowledge Manager
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: knowledge/dynamic-knowledge-manager
Concept: Managing lifecycle of facts, ensuring knowledge base remains current and non-contradictory

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
    "original_id": "knowledge/dynamic-knowledge-manager",
    "original_name": "Dynamic Knowledge Manager",
    "concept": "Managing lifecycle of facts, ensuring knowledge base remains current and non-contradictory",
    "scale_structure": {
    "L0": [
        "ingest_unstructured_source: Read PDF, HTML, or Text input",
        "segment_document_chunks: Split text into semantic overlapping windows",
        "detect_conflicting_facts: Compare new info against existing graph facts",
        "archive_stale_knowledge: Mark old data as deprecated rather than deleting",
        "map_ontology_schema: Align new terms to standard taxonomy",
        "commit_graph_transaction: Atomic write of new nodes/edges"
    ],
    "L1": [
        "ingest_and_segment: Read source and split into chunks",
        "validate_knowledge: Detect conflicts and archive stale data",
        "integrate_knowledge: Map ontology and commit transaction"
    ],
    "L2": [
        "manage_knowledge_lifecycle: Complete knowledge ingestion to integration"
    ],
    "L3": [
        "knowledge_dynamic-knowledge-manager_orchestrator"
    ]
},
    "skill_tree": {
    "knowledge/dynamic_knowledge_manager/orchestrator": [
        "knowledge/dynamic_knowledge_manager/manage_knowledge_lifecycle"
    ],
    "knowledge/dynamic_knowledge_manager/manage_knowledge_lifecycle": [
        "knowledge/dynamic_knowledge_manager/ingest_and_segment",
        "knowledge/dynamic_knowledge_manager/validate_knowledge",
        "knowledge/dynamic_knowledge_manager/integrate_knowledge"
    ],
    "knowledge/dynamic_knowledge_manager/ingest_and_segment": [
        "knowledge/dynamic_knowledge_manager/ingest_unstructured_source",
        "knowledge/dynamic_knowledge_manager/segment_document_chunks"
    ],
    "knowledge/dynamic_knowledge_manager/validate_knowledge": [
        "knowledge/dynamic_knowledge_manager/detect_conflicting_facts",
        "knowledge/dynamic_knowledge_manager/archive_stale_knowledge"
    ],
    "knowledge/dynamic_knowledge_manager/integrate_knowledge": [
        "knowledge/dynamic_knowledge_manager/map_ontology_schema",
        "knowledge/dynamic_knowledge_manager/commit_graph_transaction"
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

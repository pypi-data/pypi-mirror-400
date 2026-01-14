"""
Complex Skill Decomposition Strategy
=====================================

This module contains the manual decomposition strategies for the 11 skills
that were too abstract for automatic decomposition. These strategies provide
explicit atomic micro-operations that GPIA can use to generate S2 decompositions.

Based on the 5-LLM Partner routing:
- L0 (Micro): codegemma | llava | reasoning: codegemma | synthesis: qwen3
- L1 (Meso): qwen3 | llava | reasoning: deepseek_r1 | synthesis: qwen3
- L2 (Macro): qwen3 | llava | reasoning: deepseek_r1 | synthesis: gpt_oss_20b
- L3 (Meta): deepseek_r1 | llava | reasoning: deepseek_r1 | synthesis: gpt_oss_20b
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from pathlib import Path
import json

# Output directory for generated decompositions
DECOMPOSED_DIR = Path(__file__).parent / "decomposed"


@dataclass
class MicroOperation:
    """An atomic micro-operation (L0)."""
    name: str
    description: str
    model_hint: str = "codegemma"  # Default L0 model


@dataclass
class MesoOperation:
    """A composed meso-operation (L1) that bundles micros."""
    name: str
    description: str
    micros: List[str]
    model_hint: str = "qwen3"


@dataclass
class MacroOperation:
    """A macro workflow (L2) that bundles mesos."""
    name: str
    description: str
    mesos: List[str]
    model_hint: str = "qwen3"


@dataclass
class SkillDecompositionStrategy:
    """Complete decomposition strategy for a skill."""
    skill_id: str
    name: str
    concept: str
    micros: List[MicroOperation]
    mesos: List[MesoOperation] = field(default_factory=list)
    macros: List[MacroOperation] = field(default_factory=list)
    visual_potential: bool = False


# ============================================================================
# DECOMPOSITION STRATEGIES FOR ALL 11 REMAINING SKILLS
# ============================================================================

DECOMPOSITION_STRATEGIES: Dict[str, SkillDecompositionStrategy] = {

    # 1. AUTOMATION: HYBRID ORCHESTRATOR
    "automation/hybrid-orchestrator": SkillDecompositionStrategy(
        skill_id="automation/hybrid-orchestrator",
        name="Hybrid Orchestrator",
        concept="Meta-controller that routes tasks between deterministic code, probabilistic LLMs, and external APIs",
        micros=[
            MicroOperation("analyze_task_complexity", "Classify incoming prompt as simple (rule-based) or complex (agentic)", "codegemma"),
            MicroOperation("decompose_to_dag", "Break a complex goal into a Directed Acyclic Graph of sub-tasks", "deepseek_r1"),
            MicroOperation("select_execution_engine", "Determine if sub-task needs Python script, SQL query, or LLM call", "codegemma"),
            MicroOperation("dispatch_subtask", "Send a unit of work to the selected engine", "codegemma"),
            MicroOperation("aggregate_branch_results", "Combine outputs from parallel execution branches", "qwen3"),
            MicroOperation("handle_execution_failure", "Trigger retry logic or fallback path upon error", "codegemma"),
        ],
        mesos=[
            MesoOperation("plan_execution_strategy", "Analyze complexity and decompose into DAG", ["analyze_task_complexity", "decompose_to_dag"]),
            MesoOperation("execute_task_branch", "Select engine, dispatch, and handle results", ["select_execution_engine", "dispatch_subtask", "handle_execution_failure"]),
        ],
        macros=[
            MacroOperation("orchestrate_hybrid_workflow", "Complete task routing and execution", ["plan_execution_strategy", "execute_task_branch", "aggregate_branch_results"]),
        ],
    ),

    # 2. AUTOMATION: TELEMETRY ANOMALY
    "automation/telemetry-anomaly": SkillDecompositionStrategy(
        skill_id="automation/telemetry-anomaly",
        name="Telemetry Anomaly",
        concept="Real-time monitoring of system metrics to detect deviations from established baselines",
        micros=[
            MicroOperation("ingest_metric_stream", "Buffer incoming time-series data points", "codegemma"),
            MicroOperation("calculate_rolling_window", "Compute moving averages or z-scores for current window", "codegemma"),
            MicroOperation("detect_threshold_breach", "Identify when metric exceeds defined static limits", "codegemma"),
            MicroOperation("identify_trend_deviation", "Detect slope changes or gradual drift (non-static anomalies)", "deepseek_r1"),
            MicroOperation("correlate_logs_timebox", "Fetch system logs occurring within anomaly timestamp", "qwen3"),
            MicroOperation("dispatch_alert_webhook", "Send structured JSON payload to alerting system", "codegemma"),
        ],
        mesos=[
            MesoOperation("process_metric_window", "Ingest stream and calculate statistics", ["ingest_metric_stream", "calculate_rolling_window"]),
            MesoOperation("detect_anomaly", "Check thresholds and trends for anomalies", ["detect_threshold_breach", "identify_trend_deviation"]),
            MesoOperation("alert_with_context", "Correlate logs and dispatch alert", ["correlate_logs_timebox", "dispatch_alert_webhook"]),
        ],
        macros=[
            MacroOperation("monitor_and_alert", "Complete anomaly detection pipeline", ["process_metric_window", "detect_anomaly", "alert_with_context"]),
        ],
    ),

    # 3. CONSCIENCE: EMBEDDING REPAIR
    "conscience/embedding-repair": SkillDecompositionStrategy(
        skill_id="conscience/embedding-repair",
        name="Embedding Repair",
        concept="Diagnosing and fixing vector store degradation where semantic search results have become irrelevant",
        micros=[
            MicroOperation("assess_cluster_cohesion", "Measure density of vector clusters to find loose/drifted points", "deepseek_r1"),
            MicroOperation("identify_retrieval_gaps", "Log queries that returned low-confidence scores", "codegemma"),
            MicroOperation("generate_synthetic_anchor", "Create ideal 'golden' embedding for a specific concept", "qwen3"),
            MicroOperation("reindex_vector_batch", "Force refresh of embeddings for specific document set", "codegemma"),
            MicroOperation("prune_orphan_vectors", "Remove vectors that no longer link to valid source documents", "codegemma"),
            MicroOperation("validate_repair_distance", "Compare pre-fix and post-fix cosine similarity", "codegemma"),
        ],
        mesos=[
            MesoOperation("diagnose_embedding_health", "Assess clusters and identify retrieval gaps", ["assess_cluster_cohesion", "identify_retrieval_gaps"]),
            MesoOperation("repair_vectors", "Generate anchors, reindex, and prune orphans", ["generate_synthetic_anchor", "reindex_vector_batch", "prune_orphan_vectors"]),
        ],
        macros=[
            MacroOperation("full_embedding_repair", "Complete diagnosis and repair cycle", ["diagnose_embedding_health", "repair_vectors", "validate_repair_distance"]),
        ],
    ),

    # 4. CONSCIENCE: MEMORY LINKER
    "conscience/memory-linker": SkillDecompositionStrategy(
        skill_id="conscience/memory-linker",
        name="Memory Linker",
        concept="Converting linear interaction logs into graph structure by linking related entities",
        micros=[
            MicroOperation("extract_named_entities", "Identify People, Places, Concepts in text", "codegemma"),
            MicroOperation("query_existing_nodes", "Check graph for pre-existing entities (fuzzy match)", "codegemma"),
            MicroOperation("calculate_semantic_affinity", "Determine strength of relationship between two nodes", "deepseek_r1"),
            MicroOperation("create_edge_relationship", "Define edge type (IS_A, WORKED_WITH, LOCATED_IN)", "qwen3"),
            MicroOperation("merge_duplicate_nodes", "Fuse two nodes identified as the same entity", "codegemma"),
            MicroOperation("decay_edge_weight", "Reduce importance of links not reinforced recently", "codegemma"),
        ],
        mesos=[
            MesoOperation("extract_and_match_entities", "Extract entities and query existing nodes", ["extract_named_entities", "query_existing_nodes", "merge_duplicate_nodes"]),
            MesoOperation("build_relationship_graph", "Calculate affinity and create edges", ["calculate_semantic_affinity", "create_edge_relationship"]),
        ],
        macros=[
            MacroOperation("link_memory_graph", "Complete entity extraction to graph linking", ["extract_and_match_entities", "build_relationship_graph", "decay_edge_weight"]),
        ],
    ),

    # 5. ENTERPRISE: OPS COMPLIANCE RUNBOOK
    "enterprise/ops-compliance-runbook": SkillDecompositionStrategy(
        skill_id="enterprise/ops-compliance-runbook",
        name="Ops Compliance Runbook",
        concept="Automated enforcement of regulatory or internal policy standards during operations",
        micros=[
            MicroOperation("parse_policy_manifest", "Load rules (e.g., 'No S3 buckets open to public')", "codegemma"),
            MicroOperation("scan_resource_configuration", "Read current state of infrastructure/code", "codegemma"),
            MicroOperation("detect_compliance_violation", "Diff actual state against policy rules", "deepseek_r1"),
            MicroOperation("snapshot_violation_context", "Capture evidence of the breach for audit", "codegemma"),
            MicroOperation("execute_remediation_script", "Run the specific fix (e.g., close_port_80)", "codegemma"),
            MicroOperation("log_audit_trail", "Write immutable record of the check and action", "codegemma"),
        ],
        mesos=[
            MesoOperation("load_and_scan", "Parse policies and scan current configuration", ["parse_policy_manifest", "scan_resource_configuration"]),
            MesoOperation("detect_and_document", "Detect violations and snapshot context", ["detect_compliance_violation", "snapshot_violation_context"]),
            MesoOperation("remediate_and_log", "Execute fix and write audit trail", ["execute_remediation_script", "log_audit_trail"]),
        ],
        macros=[
            MacroOperation("run_compliance_check", "Complete compliance enforcement cycle", ["load_and_scan", "detect_and_document", "remediate_and_log"]),
        ],
    ),

    # 6. GOVERNANCE: GUARDRAILS CONTROL
    "governance/guardrails-control": SkillDecompositionStrategy(
        skill_id="governance/guardrails-control",
        name="Guardrails Control",
        concept="Safety valve between user input and model output to prevent unsafe interactions",
        micros=[
            MicroOperation("intercept_input_stream", "Capture user prompt before LLM inference", "codegemma"),
            MicroOperation("scan_pii_patterns", "Regex/model check for emails, SSNs, credit cards", "codegemma"),
            MicroOperation("check_topic_allowlist", "Verify subject matter matches allowed domain", "codegemma"),
            MicroOperation("filter_output_stream", "Scan generated text for banned keywords or tone", "qwen3"),
            MicroOperation("truncate_response", "Cut off output if safety threshold crossed", "codegemma"),
            MicroOperation("inject_safety_preamble", "Prepend required system instructions dynamically", "codegemma"),
        ],
        mesos=[
            MesoOperation("validate_input", "Intercept, scan PII, check allowlist", ["intercept_input_stream", "scan_pii_patterns", "check_topic_allowlist"]),
            MesoOperation("sanitize_output", "Filter, truncate, and inject safety preamble", ["filter_output_stream", "truncate_response", "inject_safety_preamble"]),
        ],
        macros=[
            MacroOperation("enforce_guardrails", "Complete input/output safety enforcement", ["validate_input", "sanitize_output"]),
        ],
    ),

    # 7. KNOWLEDGE: DYNAMIC KNOWLEDGE MANAGER
    "knowledge/dynamic-knowledge-manager": SkillDecompositionStrategy(
        skill_id="knowledge/dynamic-knowledge-manager",
        name="Dynamic Knowledge Manager",
        concept="Managing lifecycle of facts, ensuring knowledge base remains current and non-contradictory",
        micros=[
            MicroOperation("ingest_unstructured_source", "Read PDF, HTML, or Text input", "codegemma"),
            MicroOperation("segment_document_chunks", "Split text into semantic overlapping windows", "codegemma"),
            MicroOperation("detect_conflicting_facts", "Compare new info against existing graph facts", "deepseek_r1"),
            MicroOperation("archive_stale_knowledge", "Mark old data as deprecated rather than deleting", "codegemma"),
            MicroOperation("map_ontology_schema", "Align new terms to standard taxonomy", "qwen3"),
            MicroOperation("commit_graph_transaction", "Atomic write of new nodes/edges", "codegemma"),
        ],
        mesos=[
            MesoOperation("ingest_and_segment", "Read source and split into chunks", ["ingest_unstructured_source", "segment_document_chunks"]),
            MesoOperation("validate_knowledge", "Detect conflicts and archive stale data", ["detect_conflicting_facts", "archive_stale_knowledge"]),
            MesoOperation("integrate_knowledge", "Map ontology and commit transaction", ["map_ontology_schema", "commit_graph_transaction"]),
        ],
        macros=[
            MacroOperation("manage_knowledge_lifecycle", "Complete knowledge ingestion to integration", ["ingest_and_segment", "validate_knowledge", "integrate_knowledge"]),
        ],
    ),

    # 8. REASONING: EXPLAINABLE REASONING (XAI)
    "reasoning/explainable-reasoning": SkillDecompositionStrategy(
        skill_id="reasoning/explainable-reasoning",
        name="Explainable Reasoning",
        concept="Converting opaque model weights/decisions into human-readable rationale",
        micros=[
            MicroOperation("trace_chain_of_thought", "Log intermediate reasoning steps of the LLM", "deepseek_r1"),
            MicroOperation("extract_key_features", "Identify which input tokens had highest attention weights", "codegemma"),
            MicroOperation("generate_counterfactual", "'What if' analysis - how result changes if input changes", "deepseek_r1"),
            MicroOperation("summarize_decision_logic", "Translate technical trace into natural language", "qwen3"),
            MicroOperation("link_source_citations", "Connect claims in output to source documents", "codegemma"),
            MicroOperation("format_explanation_tree", "JSON structure of the logic path", "codegemma"),
        ],
        mesos=[
            MesoOperation("trace_reasoning", "Trace chain of thought and extract key features", ["trace_chain_of_thought", "extract_key_features"]),
            MesoOperation("explain_decision", "Generate counterfactual and summarize logic", ["generate_counterfactual", "summarize_decision_logic"]),
            MesoOperation("document_explanation", "Link citations and format tree", ["link_source_citations", "format_explanation_tree"]),
        ],
        macros=[
            MacroOperation("generate_xai_report", "Complete explainable reasoning pipeline", ["trace_reasoning", "explain_decision", "document_explanation"]),
        ],
    ),

    # 9. REASONING: SEMANTIC ID CONSTRUCTOR
    "reasoning/semantic-id-constructor": SkillDecompositionStrategy(
        skill_id="reasoning/semantic-id-constructor",
        name="Semantic ID Constructor",
        concept="Generating deterministic, meaningful unique identifiers based on content rather than random UUIDs",
        micros=[
            MicroOperation("normalize_input_content", "Lowercase, strip whitespace/punctuation", "codegemma"),
            MicroOperation("extract_semantic_fingerprint", "Get core keywords or vector hash", "codegemma"),
            MicroOperation("generate_namespace_prefix", "Create readable header (e.g., DOC-FINANCE-2023)", "qwen3"),
            MicroOperation("compute_content_hash", "SHA-256 or similar hash of normalized content", "codegemma"),
            MicroOperation("check_id_collision", "Verify ID does not already exist in registry", "codegemma"),
            MicroOperation("register_id_mapping", "Store ID -> Metadata link", "codegemma"),
        ],
        mesos=[
            MesoOperation("prepare_content", "Normalize and extract semantic fingerprint", ["normalize_input_content", "extract_semantic_fingerprint"]),
            MesoOperation("generate_id", "Generate namespace prefix and compute hash", ["generate_namespace_prefix", "compute_content_hash"]),
            MesoOperation("register_id", "Check collision and register mapping", ["check_id_collision", "register_id_mapping"]),
        ],
        macros=[
            MacroOperation("construct_semantic_id", "Complete ID generation pipeline", ["prepare_content", "generate_id", "register_id"]),
        ],
    ),

    # 10. SAFETY: CONSTRAINED DECODING
    "safety/constrained-decoding": SkillDecompositionStrategy(
        skill_id="safety/constrained-decoding",
        name="Constrained Decoding",
        concept="Forcing LLM to output exactly what is needed (e.g., valid JSON) by manipulating logit probabilities",
        micros=[
            MicroOperation("load_grammar_schema", "Ingest JSON Schema or BNF grammar", "codegemma"),
            MicroOperation("calculate_token_mask", "Determine which tokens are valid next-steps", "codegemma"),
            MicroOperation("suppress_invalid_logits", "Set probability of invalid tokens to -infinity", "codegemma"),
            MicroOperation("enforce_stop_sequence", "Hard stop generation at specific delimiters", "codegemma"),
            MicroOperation("validate_partial_json", "Check if incomplete stream is still valid JSON", "codegemma"),
            MicroOperation("apply_repetition_penalty", "Reduce probability of looping phrases", "codegemma"),
        ],
        mesos=[
            MesoOperation("prepare_constraints", "Load grammar and calculate token mask", ["load_grammar_schema", "calculate_token_mask"]),
            MesoOperation("apply_constraints", "Suppress invalid logits and enforce stop sequence", ["suppress_invalid_logits", "enforce_stop_sequence"]),
            MesoOperation("validate_output", "Validate partial JSON and apply repetition penalty", ["validate_partial_json", "apply_repetition_penalty"]),
        ],
        macros=[
            MacroOperation("constrained_generation", "Complete constrained decoding pipeline", ["prepare_constraints", "apply_constraints", "validate_output"]),
        ],
    ),

    # 11. SYSTEM: SKILL INDEXER
    "system/skill-indexer": SkillDecompositionStrategy(
        skill_id="system/skill-indexer",
        name="Skill Indexer",
        concept="Registry system that allows Orchestrator to know what tools are available",
        micros=[
            MicroOperation("parse_skill_manifest", "Read SKILL.md YAML/Frontmatter", "codegemma"),
            MicroOperation("validate_skill_schema", "Ensure required fields (inputs, outputs) exist", "codegemma"),
            MicroOperation("generate_skill_description_embedding", "Vectorize the 'What does this do?' text", "codegemma"),
            MicroOperation("register_skill_endpoint", "Map function name to execution path/API", "codegemma"),
            MicroOperation("update_skill_metadata", "Refresh version numbers or parameters", "codegemma"),
            MicroOperation("optimize_retrieval_index", "Rebalance vector tree for faster search", "codegemma"),
        ],
        mesos=[
            MesoOperation("parse_and_validate", "Parse manifest and validate schema", ["parse_skill_manifest", "validate_skill_schema"]),
            MesoOperation("index_skill", "Generate embedding and register endpoint", ["generate_skill_description_embedding", "register_skill_endpoint"]),
            MesoOperation("maintain_index", "Update metadata and optimize retrieval", ["update_skill_metadata", "optimize_retrieval_index"]),
        ],
        macros=[
            MacroOperation("index_skill_catalog", "Complete skill indexing pipeline", ["parse_and_validate", "index_skill", "maintain_index"]),
        ],
    ),
}


def generate_s2_decomposition(strategy: SkillDecompositionStrategy) -> Dict[str, Any]:
    """
    Generate S2 decomposition from a strategy.

    Returns the full structure needed for a decomposed skill file.
    """
    # Build scale structure
    scale_structure = {
        "L0": [f"{m.name}: {m.description}" for m in strategy.micros],
        "L1": [f"{m.name}: {m.description}" for m in strategy.mesos],
        "L2": [f"{m.name}: {m.description}" for m in strategy.macros],
        "L3": [f"{strategy.skill_id.replace('/', '_')}_orchestrator"],
    }

    # Build skill tree
    prefix = strategy.skill_id.replace("-", "_")
    skill_tree = {
        f"{prefix}/orchestrator": [f"{prefix}/{m.name}" for m in strategy.macros],
    }

    for macro in strategy.macros:
        skill_tree[f"{prefix}/{macro.name}"] = [f"{prefix}/{m}" for m in macro.mesos]

    for meso in strategy.mesos:
        skill_tree[f"{prefix}/{meso.name}"] = [f"{prefix}/{m}" for m in meso.micros]

    # Build model routing (5 LLM partners)
    model_routing = {
        "L0": {
            "text": "codegemma",
            "visual": "llava" if strategy.visual_potential else "codegemma",
            "reasoning": "codegemma",
            "synthesis": "qwen3"
        },
        "L1": {
            "text": "qwen3",
            "visual": "llava" if strategy.visual_potential else "qwen3",
            "reasoning": "deepseek_r1",
            "synthesis": "qwen3"
        },
        "L2": {
            "text": "qwen3",
            "visual": "llava" if strategy.visual_potential else "qwen3",
            "reasoning": "deepseek_r1",
            "synthesis": "gpt_oss_20b"
        },
        "L3": {
            "text": "deepseek_r1",
            "visual": "llava" if strategy.visual_potential else "deepseek_r1",
            "reasoning": "deepseek_r1",
            "synthesis": "gpt_oss_20b"
        },
    }

    return {
        "skill_id": strategy.skill_id,
        "original_name": strategy.name,
        "concept": strategy.concept,
        "scale_structure": scale_structure,
        "skill_tree": skill_tree,
        "model_routing": model_routing,
    }


def save_decomposed_skill(decomposition: Dict[str, Any]) -> Path:
    """Save a decomposed skill to file."""
    DECOMPOSED_DIR.mkdir(parents=True, exist_ok=True)

    skill_id = decomposition["skill_id"]
    safe_name = skill_id.replace("/", "_").replace("-", "_")
    output_file = DECOMPOSED_DIR / f"{safe_name}_s2.py"

    content = f'''"""
S2 Decomposed: {decomposition["original_name"]}
==========================================

Auto-generated from Complex Decomposition Strategy.

Original skill: {skill_id}
Concept: {decomposition["concept"]}

Scale structure:
  L0 (Micro): {len(decomposition["scale_structure"]["L0"])} operations
  L1 (Meso): {len(decomposition["scale_structure"]["L1"])} operations
  L2 (Macro): {len(decomposition["scale_structure"]["L2"])} operations
  L3 (Meta): 1 orchestrator

Model routing (5 LLM Partners: codegemma, qwen3, deepseek_r1, llava, gpt_oss_20b):
  L0 -> text:{decomposition["model_routing"]["L0"]["text"]} | reasoning:{decomposition["model_routing"]["L0"]["reasoning"]}
  L1 -> text:{decomposition["model_routing"]["L1"]["text"]} | reasoning:{decomposition["model_routing"]["L1"]["reasoning"]}
  L2 -> text:{decomposition["model_routing"]["L2"]["text"]} | synthesis:{decomposition["model_routing"]["L2"]["synthesis"]}
  L3 -> text:{decomposition["model_routing"]["L3"]["text"]} | synthesis:{decomposition["model_routing"]["L3"]["synthesis"]}
"""


# Skill metadata
SKILL_METADATA = {{
    "original_id": "{skill_id}",
    "original_name": "{decomposition["original_name"]}",
    "concept": "{decomposition["concept"]}",
    "scale_structure": {json.dumps(decomposition["scale_structure"], indent=4)},
    "skill_tree": {json.dumps(decomposition["skill_tree"], indent=4)},
    "model_routing": {json.dumps(decomposition["model_routing"], indent=4)},
}}
'''

    output_file.write_text(content, encoding='utf-8')
    return output_file


def decompose_all_complex_skills() -> Dict[str, Any]:
    """
    Decompose all 11 complex skills using the provided strategies.

    This is the main entry point for GPIA to execute the decomposition.
    """
    results = {
        "total": len(DECOMPOSITION_STRATEGIES),
        "successful": [],
        "failed": [],
    }

    print(f"\\nDecomposing {len(DECOMPOSITION_STRATEGIES)} complex skills...")
    print("=" * 60)

    for skill_id, strategy in DECOMPOSITION_STRATEGIES.items():
        print(f"\\n[{len(results['successful']) + 1}/{len(DECOMPOSITION_STRATEGIES)}] {skill_id}")

        try:
            decomposition = generate_s2_decomposition(strategy)
            output_path = save_decomposed_skill(decomposition)

            results["successful"].append({
                "skill_id": skill_id,
                "path": str(output_path),
                "micros": len(strategy.micros),
                "mesos": len(strategy.mesos),
                "macros": len(strategy.macros),
            })

            print(f"  -> SUCCESS: {len(strategy.micros)} micros, {len(strategy.mesos)} mesos, {len(strategy.macros)} macros")

        except Exception as e:
            results["failed"].append({
                "skill_id": skill_id,
                "error": str(e),
            })
            print(f"  -> FAILED: {e}")

    print("\\n" + "=" * 60)
    print(f"Complete: {len(results['successful'])} successful, {len(results['failed'])} failed")

    return results


if __name__ == "__main__":
    decompose_all_complex_skills()

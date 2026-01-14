"""
S2 Memory Skill - Multi-Scale Decomposition
============================================

Demonstrates S2 decomposition of the conscience/memory skill.

Original: conscience/memory (single L2 macro skill with multiple capabilities)
S2 Decomposed:
  L3 (Meta):  memory-orchestrator   - Coordinates memory operations
  L2 (Macro): experience            - Store new memory with context
              recall                - Search and retrieve memories
              reflect               - Analyze patterns in memory
  L1 (Meso):  recall-by-type        - Type-specific retrieval
              consolidate           - Merge related memories
              link-memories         - Create associative links
  L0 (Micro): generate-embedding    - Create vector from text
              store-record          - Atomic SQLite insert
              fetch-record          - Atomic SQLite query
              compute-similarity    - Vector cosine similarity
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import logging
import time
import numpy as np

from ..context_stack import S2ContextStack, ScaleLevel, create_s2_context
from ..composer import S2Composer, CompositionPlan

logger = logging.getLogger(__name__)


# ==============================================================================
# L0 MICRO SKILLS (Atomic operations, <=10 tokens each)
# ==============================================================================

def micro_generate_embedding(text: str, dimension: int = 384, **kwargs) -> Dict[str, Any]:
    """L0: Generate embedding vector for text (simulated for demo)."""
    # In production, would use NPU/GPU embedder
    # For demo, generate deterministic pseudo-embedding from text hash
    hash_bytes = hashlib.sha256(text.encode()).digest()
    # Expand hash to embedding dimension
    np.random.seed(int.from_bytes(hash_bytes[:4], 'little'))
    embedding = np.random.randn(dimension).astype(np.float32)
    # Normalize
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return {
        "embedding": embedding.tolist(),
        "dimension": dimension,
        "text_length": len(text)
    }


def micro_store_record(
    record_id: str,
    content: str,
    memory_type: str = "episodic",
    importance: float = 0.5,
    embedding: Optional[List[float]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L0: Store a single memory record (simulated SQLite insert)."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # In production, would do actual SQLite insert
    return {
        "stored": True,
        "id": record_id,
        "memory_type": memory_type,
        "importance": importance,
        "timestamp": timestamp,
        "has_embedding": embedding is not None
    }


def micro_fetch_record(
    record_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """L0: Fetch memory records (simulated SQLite query)."""
    # In production, would do actual SQLite query
    # For demo, return simulated results
    records = []
    if record_id:
        records = [{
            "id": record_id,
            "content": f"Memory content for {record_id}",
            "memory_type": memory_type or "episodic",
            "importance": 0.5,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }]
    else:
        # Return demo records
        for i in range(min(limit, 3)):
            records.append({
                "id": f"mem_{i}",
                "content": f"Sample memory {i}",
                "memory_type": memory_type or "episodic",
                "importance": 0.5 + i * 0.1,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
    return {"records": records, "count": len(records)}


def micro_compute_similarity(
    embedding_a: List[float],
    embedding_b: List[float],
    **kwargs
) -> Dict[str, Any]:
    """L0: Compute cosine similarity between two embeddings."""
    a = np.array(embedding_a)
    b = np.array(embedding_b)
    similarity = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    return {
        "similarity": similarity,
        "is_similar": similarity > 0.7,
        "dimension": len(embedding_a)
    }


# ==============================================================================
# L1 MESO SKILLS (Composed operations, 30-50 tokens each)
# ==============================================================================

def meso_recall_by_type(
    query: str,
    memory_type: str = "episodic",
    limit: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """L1: Retrieve memories of specific type with ranking."""
    # Generate query embedding
    query_emb = micro_generate_embedding(query)

    # Fetch records of type
    records = micro_fetch_record(memory_type=memory_type, limit=limit * 2)

    # Score and rank (simulated - in production would use actual embeddings)
    scored = []
    for record in records["records"]:
        # Generate record embedding
        rec_emb = micro_generate_embedding(record["content"])
        sim = micro_compute_similarity(query_emb["embedding"], rec_emb["embedding"])
        scored.append({
            "record": record,
            "similarity": sim["similarity"],
            "relevance": sim["similarity"] * record["importance"]
        })

    # Sort by relevance
    scored.sort(key=lambda x: x["relevance"], reverse=True)

    return {
        "memories": scored[:limit],
        "count": len(scored[:limit]),
        "memory_type": memory_type,
        "query": query
    }


def meso_consolidate_memories(
    memories: List[Dict[str, Any]],
    threshold: float = 0.8,
    **kwargs
) -> Dict[str, Any]:
    """L1: Consolidate similar memories into summaries."""
    if not memories:
        return {"consolidated": [], "original_count": 0, "final_count": 0}

    # Find clusters of similar memories
    clusters = []
    used = set()

    for i, mem_i in enumerate(memories):
        if i in used:
            continue
        cluster = [mem_i]
        used.add(i)

        emb_i = micro_generate_embedding(mem_i.get("content", ""))

        for j, mem_j in enumerate(memories[i+1:], i+1):
            if j in used:
                continue
            emb_j = micro_generate_embedding(mem_j.get("content", ""))
            sim = micro_compute_similarity(emb_i["embedding"], emb_j["embedding"])
            if sim["similarity"] >= threshold:
                cluster.append(mem_j)
                used.add(j)

        clusters.append(cluster)

    # Create consolidated entries
    consolidated = []
    for cluster in clusters:
        if len(cluster) == 1:
            consolidated.append(cluster[0])
        else:
            # Merge cluster into summary
            contents = [m.get("content", "") for m in cluster]
            consolidated.append({
                "content": f"[Consolidated {len(cluster)} memories]: {contents[0]}...",
                "memory_type": cluster[0].get("memory_type", "episodic"),
                "importance": max(m.get("importance", 0.5) for m in cluster),
                "source_count": len(cluster)
            })

    return {
        "consolidated": consolidated,
        "original_count": len(memories),
        "final_count": len(consolidated),
        "clusters": len(clusters)
    }


def meso_link_memories(
    memory_a: Dict[str, Any],
    memory_b: Dict[str, Any],
    relation: str = "related",
    **kwargs
) -> Dict[str, Any]:
    """L1: Create associative link between memories."""
    # Compute similarity
    emb_a = micro_generate_embedding(memory_a.get("content", ""))
    emb_b = micro_generate_embedding(memory_b.get("content", ""))
    sim = micro_compute_similarity(emb_a["embedding"], emb_b["embedding"])

    return {
        "linked": True,
        "from_id": memory_a.get("id", "unknown_a"),
        "to_id": memory_b.get("id", "unknown_b"),
        "relation": relation,
        "strength": sim["similarity"],
        "bidirectional": True
    }


# ==============================================================================
# L2 MACRO SKILLS (Bundled workflows, 80-120 tokens)
# ==============================================================================

def macro_experience(
    content: str,
    memory_type: str = "episodic",
    importance: float = 0.5,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L2: Store a new experience as memory."""
    # Generate embedding
    embedding = micro_generate_embedding(content)

    # Generate ID
    record_id = hashlib.sha256(f"{content}:{time.time()}".encode()).hexdigest()[:16]

    # Store record
    stored = micro_store_record(
        record_id=record_id,
        content=content,
        memory_type=memory_type,
        importance=importance,
        embedding=embedding["embedding"]
    )

    return {
        "stored": stored["stored"],
        "memory_id": record_id,
        "memory_type": memory_type,
        "importance": importance,
        "embedding_dim": embedding["dimension"],
        "context_provided": context is not None
    }


def macro_recall(
    query: str,
    memory_types: Optional[List[str]] = None,
    limit: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """L2: Search and retrieve relevant memories."""
    memory_types = memory_types or ["episodic", "semantic"]

    all_results = []
    for mtype in memory_types:
        type_results = meso_recall_by_type(query, memory_type=mtype, limit=limit)
        all_results.extend(type_results["memories"])

    # Re-rank all results by relevance
    all_results.sort(key=lambda x: x["relevance"], reverse=True)

    return {
        "memories": all_results[:limit],
        "total_found": len(all_results),
        "returned": min(limit, len(all_results)),
        "query": query,
        "types_searched": memory_types
    }


def macro_reflect(
    topic: str,
    depth: str = "shallow",
    **kwargs
) -> Dict[str, Any]:
    """L2: Analyze patterns in memory related to topic."""
    # Recall memories related to topic
    memories = macro_recall(topic, memory_types=["episodic", "semantic", "identity"])

    # Consolidate similar memories
    memory_list = [m["record"] for m in memories["memories"]]
    consolidated = meso_consolidate_memories(memory_list, threshold=0.7)

    # Generate reflection
    patterns = []
    if consolidated["final_count"] < consolidated["original_count"]:
        patterns.append(f"Found {consolidated['clusters']} distinct memory clusters")

    if memories["total_found"] > 0:
        avg_relevance = sum(m["relevance"] for m in memories["memories"]) / len(memories["memories"])
        patterns.append(f"Average relevance to '{topic}': {avg_relevance:.2f}")

    reflection = {
        "topic": topic,
        "depth": depth,
        "memories_analyzed": memories["total_found"],
        "consolidated_to": consolidated["final_count"],
        "patterns": patterns,
        "insight": f"Analysis of {topic} revealed {len(patterns)} patterns across {memories['total_found']} memories"
    }

    return reflection


# ==============================================================================
# L3 META SKILL (Orchestrator)
# ==============================================================================

def meta_memory_orchestrator(
    capability: str,
    params: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """L3: Orchestrate memory operations across all scales."""
    params = params or {}
    context = context or {}

    # Route to appropriate macro skill
    if capability == "experience":
        result = macro_experience(
            content=params.get("content", context.get("content", "")),
            memory_type=params.get("memory_type", "episodic"),
            importance=params.get("importance", 0.5),
            context=context
        )
    elif capability == "recall":
        result = macro_recall(
            query=params.get("query", context.get("query", "")),
            memory_types=params.get("memory_types"),
            limit=params.get("limit", 5)
        )
    elif capability == "reflect":
        result = macro_reflect(
            topic=params.get("topic", context.get("topic", "")),
            depth=params.get("depth", "shallow")
        )
    else:
        result = {"error": f"Unknown capability: {capability}"}

    # Add orchestration metadata
    result["orchestrated"] = True
    result["capability"] = capability
    result["workflow"] = "S2_memory"

    return result


# ==============================================================================
# S2 COMPOSITION SETUP
# ==============================================================================

def create_memory_composer() -> S2Composer:
    """Create an S2Composer configured for memory operations."""
    composer = S2Composer()

    # L0 Micros
    composer.register_skill("memory/generate-embedding", micro_generate_embedding, ScaleLevel.L0)
    composer.register_skill("memory/store-record", micro_store_record, ScaleLevel.L0)
    composer.register_skill("memory/fetch-record", micro_fetch_record, ScaleLevel.L0)
    composer.register_skill("memory/compute-similarity", micro_compute_similarity, ScaleLevel.L0)

    # L1 Mesos
    composer.register_skill("memory/recall-by-type", meso_recall_by_type, ScaleLevel.L1)
    composer.register_skill("memory/consolidate", meso_consolidate_memories, ScaleLevel.L1)
    composer.register_skill("memory/link-memories", meso_link_memories, ScaleLevel.L1)

    # L2 Macros
    composer.register_skill("memory/experience", macro_experience, ScaleLevel.L2)
    composer.register_skill("memory/recall", macro_recall, ScaleLevel.L2)
    composer.register_skill("memory/reflect", macro_reflect, ScaleLevel.L2)

    # L3 Meta
    composer.register_skill("memory/orchestrator", meta_memory_orchestrator, ScaleLevel.L3)

    return composer


def get_memory_skill_tree() -> Dict[str, List[str]]:
    """Get the skill tree for memory decomposition."""
    return {
        "memory/orchestrator": ["memory/experience", "memory/recall", "memory/reflect"],
        "memory/experience": ["memory/generate-embedding", "memory/store-record"],
        "memory/recall": ["memory/recall-by-type"],
        "memory/reflect": ["memory/recall", "memory/consolidate"],
        "memory/recall-by-type": ["memory/fetch-record", "memory/generate-embedding", "memory/compute-similarity"],
        "memory/consolidate": ["memory/generate-embedding", "memory/compute-similarity"],
        "memory/link-memories": ["memory/generate-embedding", "memory/compute-similarity"],
    }


# ==============================================================================
# EXAMPLE EXECUTION
# ==============================================================================

def run_example():
    """Run an example S2 memory workflow."""
    print("=" * 60)
    print("S2 MEMORY SKILL EXAMPLE")
    print("=" * 60)

    # Create composer for planning
    composer = create_memory_composer()
    skill_tree = get_memory_skill_tree()

    # Create execution plan
    plan = composer.create_plan(
        goal="Demonstrate memory operations",
        meta_skill_id="memory/orchestrator",
        skill_tree=skill_tree
    )

    print(f"\nExecution Plan:")
    print(f"  Goal: {plan.goal}")
    print(f"  Skills: {len([s for _, s in plan.flatten()])} skills in tree")
    print(f"  Estimated tokens: {plan.estimated_tokens}")

    # Create context
    context = create_s2_context(
        goal="Memory operations demo",
        initial_data={
            "content": "Today I learned about S2 multi-scale architecture.",
            "query": "What did I learn about architecture?",
            "topic": "architecture"
        }
    )

    print("\n--- EXPERIENCE (Store Memory) ---")
    exp_result = meta_memory_orchestrator(
        capability="experience",
        params={"content": "Today I learned about S2 multi-scale architecture.", "importance": 0.8},
        context=context.get_context()
    )
    print(f"  Stored: {exp_result['stored']}")
    print(f"  Memory ID: {exp_result['memory_id']}")
    print(f"  Type: {exp_result['memory_type']}")

    print("\n--- RECALL (Search Memories) ---")
    recall_result = meta_memory_orchestrator(
        capability="recall",
        params={"query": "architecture", "limit": 3},
        context=context.get_context()
    )
    print(f"  Found: {recall_result['total_found']} memories")
    print(f"  Returned: {recall_result['returned']}")
    for mem in recall_result.get("memories", [])[:2]:
        print(f"    - {mem['record']['content'][:50]}... (relevance: {mem['relevance']:.2f})")

    print("\n--- REFLECT (Analyze Patterns) ---")
    reflect_result = meta_memory_orchestrator(
        capability="reflect",
        params={"topic": "architecture", "depth": "shallow"},
        context=context.get_context()
    )
    print(f"  Memories analyzed: {reflect_result['memories_analyzed']}")
    print(f"  Insight: {reflect_result['insight']}")
    for pattern in reflect_result.get("patterns", []):
        print(f"    - {pattern}")

    print("\n" + "=" * 60)
    print("S2 Memory workflow complete!")

    return {
        "experience": exp_result,
        "recall": recall_result,
        "reflect": reflect_result
    }


if __name__ == "__main__":
    run_example()

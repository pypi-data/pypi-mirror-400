"""
Multi-Space Hierarchical Retrieval (MSHR)
=========================================

Cognitive memory retrieval with separate embedding spaces
per memory type and type-specific retrieval strategies.

Architecture:
- Episodic Index: Time-weighted, contextual events
- Semantic Index: Concept clusters, fact graphs
- Procedural Index: Goal-action chains, step sequences
- Identity Index: High-confidence beliefs, stable values

Each index uses optimized strategies for its memory type,
then results are fused with learned weights.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Supported memory types with retrieval characteristics."""
    EPISODIC = "episodic"      # Events: when/where/who
    SEMANTIC = "semantic"      # Facts: what/why
    PROCEDURAL = "procedural"  # Actions: how
    IDENTITY = "identity"      # Beliefs: who am I


@dataclass
class RetrievalConfig:
    """Type-specific retrieval configuration."""
    memory_type: MemoryType
    similarity_threshold: float
    recency_weight: float       # How much to weight recent memories
    frequency_weight: float     # How much to weight access count
    importance_weight: float    # How much to weight importance score
    cross_type_boost: float     # Boost for linked memories from other types


# Default configurations per memory type
DEFAULT_CONFIGS = {
    MemoryType.EPISODIC: RetrievalConfig(
        memory_type=MemoryType.EPISODIC,
        similarity_threshold=0.3,
        recency_weight=0.4,      # Recent events more relevant
        frequency_weight=0.1,    # Don't over-weight frequent access
        importance_weight=0.3,   # Importance matters for events
        cross_type_boost=0.2,    # Some cross-type linking
    ),
    MemoryType.SEMANTIC: RetrievalConfig(
        memory_type=MemoryType.SEMANTIC,
        similarity_threshold=0.4,
        recency_weight=0.1,      # Facts don't decay much
        frequency_weight=0.2,    # Frequently used facts = useful
        importance_weight=0.4,   # High-importance facts prioritized
        cross_type_boost=0.3,    # Strong cross-type for facts
    ),
    MemoryType.PROCEDURAL: RetrievalConfig(
        memory_type=MemoryType.PROCEDURAL,
        similarity_threshold=0.5,
        recency_weight=0.2,      # Recent procedures may be updates
        frequency_weight=0.3,    # Frequently used procedures = proven
        importance_weight=0.3,   # Important procedures prioritized
        cross_type_boost=0.1,    # Procedures self-contained
    ),
    MemoryType.IDENTITY: RetrievalConfig(
        memory_type=MemoryType.IDENTITY,
        similarity_threshold=0.6,  # High threshold for identity
        recency_weight=0.05,       # Identity is stable
        frequency_weight=0.1,      # Core values not about frequency
        importance_weight=0.6,     # Only high-importance identity
        cross_type_boost=0.1,      # Identity is foundational
    ),
}


class TypedIndex:
    """
    Vector index for a single memory type.

    Uses numpy for now, can swap to FAISS for scale.
    """

    def __init__(self, memory_type: MemoryType, embedding_dim: Optional[int] = None):
        self.memory_type = memory_type
        # Enforce 384-dim (MiniLM-L6-v2) to prevent dimension mismatches
        self.embedding_dim = 384 if embedding_dim is None or embedding_dim != 384 else 384
        self.config = DEFAULT_CONFIGS[memory_type]

        # In-memory index (numpy arrays)
        self.ids: List[str] = []
        self.embeddings: Optional[np.ndarray] = None  # Shape: (n, embedding_dim)
        self.metadata: List[Dict] = []  # Parallel metadata list

    def add(self, memory_id: str, embedding: np.ndarray, metadata: Dict):
        """Add a memory to the index."""
        if self.embedding_dim is None:
            self.embedding_dim = int(embedding.shape[0])
        if embedding.shape[0] != self.embedding_dim:
            raise ValueError(f"Expected embedding dim {self.embedding_dim}, got {embedding.shape[0]}")

        self.ids.append(memory_id)
        self.metadata.append(metadata)

        if self.embeddings is None:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding.reshape(1, -1)])

    def remove(self, memory_id: str) -> bool:
        """Remove a memory from the index."""
        if memory_id not in self.ids:
            return False

        idx = self.ids.index(memory_id)
        self.ids.pop(idx)
        self.metadata.pop(idx)

        if self.embeddings is not None:
            self.embeddings = np.delete(self.embeddings, idx, axis=0)
            if len(self.embeddings) == 0:
                self.embeddings = None

        return True

    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        min_similarity: Optional[float] = None,
    ) -> List[Tuple[str, float, Dict]]:
        """
        Search index with type-specific scoring.

        Returns: List of (memory_id, final_score, metadata)
        """
        if self.embeddings is None or len(self.ids) == 0:
            return []
        if self.embedding_dim is None or query_embedding.shape[0] != self.embedding_dim:
            logger.warning(
                "Query embedding dim mismatch (expected %s, got %s)",
                self.embedding_dim,
                query_embedding.shape[0],
            )
            return []

        threshold = min_similarity or self.config.similarity_threshold

        # Compute cosine similarities
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        emb_norms = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8)
        similarities = emb_norms @ query_norm

        # Build scored results
        results = []
        for i, (mem_id, sim, meta) in enumerate(zip(self.ids, similarities, self.metadata)):
            if sim < threshold:
                continue

            # Type-specific scoring
            final_score = self._compute_score(sim, meta)
            results.append((mem_id, final_score, meta))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _compute_score(self, similarity: float, metadata: Dict) -> float:
        """Compute final score using type-specific weights."""
        config = self.config

        # Base similarity score
        score = similarity

        # Recency factor (decay over time)
        recency = metadata.get("recency_factor", 0.5)
        score += config.recency_weight * recency

        # Frequency factor (normalized access count)
        frequency = min(metadata.get("access_count", 0) / 10.0, 1.0)
        score += config.frequency_weight * frequency

        # Importance factor
        importance = metadata.get("importance", 0.5)
        score += config.importance_weight * importance

        return score

    def size(self) -> int:
        """Return number of memories in index."""
        return len(self.ids)

    def clear(self):
        """Clear the index."""
        self.ids = []
        self.embeddings = None
        self.metadata = []


class MSHRetriever:
    """
    Multi-Space Hierarchical Retriever.

    Maintains separate indexes per memory type and fuses
    results using learned strategies.
    """

    def __init__(self, embedding_dim: Optional[int] = None):
        # Enforce 384-dim (MiniLM-L6-v2) to prevent dimension mismatches
        self.embedding_dim = embedding_dim if embedding_dim == 384 else 384

        # Create typed indexes
        self.indexes: Dict[MemoryType, TypedIndex] = {
            mt: TypedIndex(mt, embedding_dim) for mt in MemoryType
        }

        # Cross-type link weights (learned over time)
        self.cross_type_weights: Dict[Tuple[MemoryType, MemoryType], float] = {}

        # Fusion weights per type (can be learned)
        self.fusion_weights: Dict[MemoryType, float] = {
            MemoryType.EPISODIC: 1.0,
            MemoryType.SEMANTIC: 1.0,
            MemoryType.PROCEDURAL: 1.0,
            MemoryType.IDENTITY: 1.2,  # Slight boost for identity
        }

        logger.info("MSHR initialized with typed indexes")

    def index_memory(
        self,
        memory_id: str,
        embedding: np.ndarray,
        memory_type: str,
        metadata: Dict,
    ):
        """Add memory to appropriate typed index."""
        if self.embedding_dim is None:
            self.embedding_dim = int(embedding.shape[0])
            for idx in self.indexes.values():
                if idx.embedding_dim is None:
                    idx.embedding_dim = self.embedding_dim
        elif embedding.shape[0] != self.embedding_dim:
            raise ValueError(f"Expected embedding dim {self.embedding_dim}, got {embedding.shape[0]}")
        try:
            mt = MemoryType(memory_type)
        except ValueError:
            mt = MemoryType.EPISODIC  # Default to episodic

        self.indexes[mt].add(memory_id, embedding, metadata)

    def remove_memory(self, memory_id: str, memory_type: str) -> bool:
        """Remove memory from index."""
        try:
            mt = MemoryType(memory_type)
        except ValueError:
            mt = MemoryType.EPISODIC

        return self.indexes[mt].remove(memory_id)

    def retrieve(
        self,
        query_embedding: np.ndarray,
        target_types: Optional[List[str]] = None,
        limit: int = 10,
        include_cross_type: bool = True,
    ) -> List[Dict]:
        """
        Retrieve memories using multi-space search.

        Args:
            query_embedding: Query vector
            target_types: Memory types to search (None = all)
            limit: Max results total
            include_cross_type: Whether to boost cross-type linked memories

        Returns:
            List of memory results with scores
        """
        if self.embedding_dim is not None and query_embedding.shape[0] != self.embedding_dim:
            logger.warning(
                "Query embedding dim mismatch (expected %s, got %s)",
                self.embedding_dim,
                query_embedding.shape[0],
            )
            return []

        # Determine which types to search
        if target_types:
            search_types = []
            for t in target_types:
                try:
                    search_types.append(MemoryType(t))
                except ValueError:
                    pass
        else:
            search_types = list(MemoryType)

        # Search each typed index
        all_results = []
        for mt in search_types:
            index = self.indexes[mt]
            type_results = index.search(query_embedding, limit=limit)

            for mem_id, score, meta in type_results:
                fusion_weight = self.fusion_weights.get(mt, 1.0)
                all_results.append({
                    "memory_id": mem_id,
                    "memory_type": mt.value,
                    "score": score * fusion_weight,
                    "raw_score": score,
                    "metadata": meta,
                })

        # Sort by fused score
        all_results.sort(key=lambda x: x["score"], reverse=True)

        # Cross-type boosting (if linked memories exist)
        if include_cross_type and len(all_results) > 0:
            all_results = self._apply_cross_type_boost(all_results)

        return all_results[:limit]

    def retrieve_by_type(
        self,
        query_embedding: np.ndarray,
        memory_type: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Retrieve from a single memory type."""
        return self.retrieve(
            query_embedding,
            target_types=[memory_type],
            limit=limit,
            include_cross_type=False,
        )

    def _apply_cross_type_boost(self, results: List[Dict]) -> List[Dict]:
        """Apply cross-type linking boost based on memory links."""
        # For now, simple implementation - can be enhanced with actual link data
        # This would use the memory_links table in SQLite
        return results

    def update_fusion_weights(self, feedback: Dict[str, float]):
        """
        Update fusion weights based on retrieval feedback.

        Args:
            feedback: Dict mapping memory_type to relevance score (0-1)
        """
        learning_rate = 0.1

        for type_str, relevance in feedback.items():
            try:
                mt = MemoryType(type_str)
                current = self.fusion_weights.get(mt, 1.0)
                # Simple exponential moving average
                self.fusion_weights[mt] = current * (1 - learning_rate) + relevance * learning_rate
            except ValueError:
                pass

        logger.debug(f"Updated fusion weights: {self.fusion_weights}")

    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "indexes": {
                mt.value: {
                    "size": self.indexes[mt].size(),
                    "config": {
                        "similarity_threshold": self.indexes[mt].config.similarity_threshold,
                        "recency_weight": self.indexes[mt].config.recency_weight,
                        "importance_weight": self.indexes[mt].config.importance_weight,
                    }
                }
                for mt in MemoryType
            },
            "fusion_weights": {mt.value: w for mt, w in self.fusion_weights.items()},
            "total_memories": sum(idx.size() for idx in self.indexes.values()),
        }

    def rebuild_from_store(self, memory_store, embedder):
        """
        Rebuild indexes from existing MemoryStore.

        This allows migration from flat storage to MSHR.
        Auto-fixes embeddings with wrong dimensions.
        """
        EXPECTED_DIM = 384  # MiniLM-L6-v2 dimension

        conn = memory_store._get_conn()
        rows = conn.execute("SELECT * FROM memories WHERE embedding IS NOT NULL").fetchall()

        count = 0
        fixed = 0
        for row in rows:
            try:
                embedding = np.frombuffer(row["embedding"], dtype=np.float32)

                # Auto-fix wrong dimension embeddings
                if embedding.shape[0] != EXPECTED_DIM:
                    if embedder:
                        try:
                            # Ensure embedder is loaded
                            if hasattr(embedder, '_model') and not embedder._model:
                                embedder.load_model()
                            elif hasattr(embedder, '_backend') and not embedder._backend:
                                embedder.load_model()

                            # Re-embed with correct model
                            new_embedding = embedder.embed([row["content"]])[0]
                            if isinstance(new_embedding, np.ndarray):
                                embedding = new_embedding.astype(np.float32)
                            else:
                                embedding = np.array(new_embedding, dtype=np.float32)

                            # Update database with correct embedding
                            conn.execute(
                                "UPDATE memories SET embedding = ? WHERE id = ?",
                                (embedding.tobytes(), row["id"])
                            )
                            conn.commit()
                            fixed += 1
                            logger.info(f"Auto-fixed embedding for {row['id']}: {row['embedding'].__len__()//4}d -> {EXPECTED_DIM}d")
                        except Exception as fix_err:
                            logger.warning(f"Could not fix embedding for {row['id']}: {fix_err}")
                            continue
                    else:
                        logger.warning(f"Skipping {row['id']}: wrong dim {embedding.shape[0]}, no embedder")
                        continue

                # Compute recency factor (0-1, higher = more recent)
                from datetime import datetime
                timestamp = datetime.fromisoformat(row["timestamp"])
                age_days = (datetime.now() - timestamp).days
                recency_factor = max(0.0, 1.0 - (age_days / 365.0))  # Decay over year

                metadata = {
                    "content": row["content"],
                    "importance": row["importance"],
                    "access_count": row["access_count"],
                    "timestamp": row["timestamp"],
                    "recency_factor": recency_factor,
                }

                self.index_memory(
                    memory_id=row["id"],
                    embedding=embedding,
                    memory_type=row["memory_type"],
                    metadata=metadata,
                )
                count += 1

            except Exception as e:
                logger.warning(f"Failed to index memory {row['id']}: {e}")

        if fixed > 0:
            logger.info(f"MSHR auto-fixed {fixed} embeddings with wrong dimensions")
        logger.info(f"MSHR rebuilt: indexed {count} memories")
        return count


def compute_recency_factor(timestamp_str: str) -> float:
    """Compute recency factor (0-1) from ISO timestamp."""
    from datetime import datetime
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        age_days = (datetime.now() - timestamp).days
        return max(0.0, 1.0 - (age_days / 365.0))
    except (ValueError, TypeError):
        return 0.5  # Default mid-range


def resolve_embedding_dim(embedder) -> Optional[int]:
    """Probe embedding dimension from a loaded embedder."""
    if not embedder:
        return None
    try:
        model_loaded = getattr(embedder, "_backend", None) or getattr(embedder, "_model", None)
        if not model_loaded:
            embedder.load_model()
        vecs = embedder.embed(["dimension probe"])
        if isinstance(vecs, np.ndarray) and vecs.ndim == 2:
            return int(vecs.shape[1])
        if vecs and hasattr(vecs[0], "__len__"):
            return int(len(vecs[0]))
    except Exception as exc:
        logger.warning(f"Embedding dim probe failed: {exc}")
    return None


class MSHRSkillMixin:
    """
    Mixin to add MSHR retrieval to MemorySkill.

    Usage:
        class EnhancedMemorySkill(MemorySkill, MSHRSkillMixin):
            def __init__(self):
                super().__init__()
                self.init_mshr()
    """

    def init_mshr(self):
        """Initialize MSHR retriever."""
        embedding_dim = resolve_embedding_dim(self.store.embedder)
        self._mshr = MSHRetriever(embedding_dim=embedding_dim)

        # Rebuild from existing store
        if hasattr(self, 'store') and self.store.embedder:
            try:
                if self.store.embedder._backend is None:
                    self.store.embedder.load_model()
                self._mshr.rebuild_from_store(self.store, self.store.embedder)
            except Exception as e:
                logger.warning(f"MSHR rebuild failed: {e}")

    def mshr_recall(
        self,
        query: str,
        target_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """MSHR-based recall with multi-space search."""
        if not hasattr(self, '_mshr'):
            self.init_mshr()

        # Generate query embedding
        if not self.store.embedder:
            return []  # Fall back to basic recall
        if self.store.embedder._backend is None:
            try:
                self.store.embedder.load_model()
            except Exception:
                return []  # Fall back to basic recall

        query_vec = self.store.embedder.embed([query])[0]

        return self._mshr.retrieve(
            query_embedding=query_vec,
            target_types=target_types,
            limit=limit,
        )

    def mshr_index_new(self, memory_id: str, content: str, memory_type: str, metadata: Dict):
        """Index a new memory in MSHR."""
        if not hasattr(self, '_mshr'):
            self.init_mshr()

        if not self.store.embedder:
            return
        if self.store.embedder._backend is None:
            try:
                self.store.embedder.load_model()
            except Exception:
                return

        embedding = self.store.embedder.embed([content])[0]

        metadata["recency_factor"] = 1.0  # New memory = max recency

        self._mshr.index_memory(
            memory_id=memory_id,
            embedding=embedding,
            memory_type=memory_type,
            metadata=metadata,
        )

    def mshr_stats(self) -> Dict:
        """Get MSHR statistics."""
        if not hasattr(self, '_mshr'):
            self.init_mshr()
        return self._mshr.get_stats()

"""
S² Scale Transforms
===================

Linear projections between skill scales, based on the S² paper insight that
multi-scale smaller models approximate large model capacity via linear transform.

The key finding: Features from larger models can be well approximated by
multi-scale smaller models through a simple linear transform.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Default embedding dimension (matches MSHR)
EMBEDDING_DIM = 384


class ScaleLevel(str, Enum):
    """Scale levels for S² architecture."""
    L0 = "L0"  # Micro
    L1 = "L1"  # Meso
    L2 = "L2"  # Macro
    L3 = "L3"  # Meta


@dataclass
class ScaleTransform:
    """
    Linear transform between adjacent skill scales.

    Implements the S² paper's key insight: multi-scale features
    can approximate large model capacity through linear projection.
    """
    source_scale: ScaleLevel
    target_scale: ScaleLevel
    dimension: int = EMBEDDING_DIM

    # Learned projection matrix (dim x dim)
    # Initialized to identity for stable start
    weights: np.ndarray = field(default=None)
    bias: np.ndarray = field(default=None)

    def __post_init__(self):
        if self.weights is None:
            # Initialize to identity + small noise
            self.weights = np.eye(self.dimension, dtype=np.float32)
            self.weights += np.random.randn(self.dimension, self.dimension).astype(np.float32) * 0.01
        if self.bias is None:
            self.bias = np.zeros(self.dimension, dtype=np.float32)

    def forward(self, embeddings: np.ndarray) -> np.ndarray:
        """Project embeddings from source to target scale."""
        # embeddings: (batch, dim) or (dim,)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        projected = embeddings @ self.weights + self.bias
        return projected.squeeze()

    def compose(self, embeddings_list: List[np.ndarray]) -> np.ndarray:
        """
        Compose multiple embeddings via attention-weighted pooling.
        Used for L0 -> L1 composition (multiple micros -> one meso).
        """
        if not embeddings_list:
            return np.zeros(self.dimension, dtype=np.float32)

        stacked = np.stack(embeddings_list)  # (n, dim)

        # Simple attention: softmax over norms
        norms = np.linalg.norm(stacked, axis=1, keepdims=True)
        weights = np.exp(norms) / np.sum(np.exp(norms))

        pooled = np.sum(stacked * weights, axis=0)
        return self.forward(pooled)


class S2Projector:
    """
    Complete S² projection system with transforms between all scale pairs.

    Enables:
    - Upward composition: L0 -> L1 -> L2 -> L3 (aggregation)
    - Downward decomposition: L3 -> L2 -> L1 -> L0 (delegation)
    - Cross-scale retrieval: Query at any scale, retrieve from any scale
    """

    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension

        # Create transforms for adjacent scales
        self.transforms: Dict[Tuple[str, str], ScaleTransform] = {
            ("L0", "L1"): ScaleTransform(ScaleLevel.L0, ScaleLevel.L1, dimension),
            ("L1", "L2"): ScaleTransform(ScaleLevel.L1, ScaleLevel.L2, dimension),
            ("L2", "L3"): ScaleTransform(ScaleLevel.L2, ScaleLevel.L3, dimension),
            # Reverse transforms for downward flow
            ("L1", "L0"): ScaleTransform(ScaleLevel.L1, ScaleLevel.L0, dimension),
            ("L2", "L1"): ScaleTransform(ScaleLevel.L2, ScaleLevel.L1, dimension),
            ("L3", "L2"): ScaleTransform(ScaleLevel.L3, ScaleLevel.L2, dimension),
        }

        logger.info(f"S2Projector initialized with dimension={dimension}")

    def project(
        self,
        embedding: np.ndarray,
        source_scale: str,
        target_scale: str,
    ) -> np.ndarray:
        """
        Project embedding from source scale to target scale.

        For non-adjacent scales, chains through intermediate transforms.
        """
        if source_scale == target_scale:
            return embedding

        # Determine path
        scale_order = ["L0", "L1", "L2", "L3"]
        src_idx = scale_order.index(source_scale)
        tgt_idx = scale_order.index(target_scale)

        current = embedding
        step = 1 if tgt_idx > src_idx else -1

        for i in range(src_idx, tgt_idx, step):
            src = scale_order[i]
            dst = scale_order[i + step]
            transform = self.transforms.get((src, dst))
            if transform:
                current = transform.forward(current)
            else:
                logger.warning(f"No transform for {src} -> {dst}")

        return current

    def compose_micros(self, micro_embeddings: List[np.ndarray]) -> np.ndarray:
        """Compose multiple L0 micro embeddings into L1 meso embedding."""
        if not micro_embeddings:
            return np.zeros(self.dimension, dtype=np.float32)

        transform = self.transforms[("L0", "L1")]
        return transform.compose(micro_embeddings)

    def compose_mesos(self, meso_embeddings: List[np.ndarray]) -> np.ndarray:
        """Compose multiple L1 meso embeddings into L2 macro embedding."""
        if not meso_embeddings:
            return np.zeros(self.dimension, dtype=np.float32)

        transform = self.transforms[("L1", "L2")]
        return transform.compose(meso_embeddings)

    def compose_macros(self, macro_embeddings: List[np.ndarray]) -> np.ndarray:
        """Compose multiple L2 macro embeddings into L3 meta embedding."""
        if not macro_embeddings:
            return np.zeros(self.dimension, dtype=np.float32)

        transform = self.transforms[("L2", "L3")]
        return transform.compose(macro_embeddings)

    def multi_scale_embedding(
        self,
        base_embedding: np.ndarray,
        base_scale: str = "L0",
    ) -> Dict[str, np.ndarray]:
        """
        Generate embeddings at all scales from a base embedding.

        This is the core S² operation: represent content at multiple scales
        via linear transforms, enabling scale-aware retrieval.
        """
        result = {base_scale: base_embedding}

        scale_order = ["L0", "L1", "L2", "L3"]
        base_idx = scale_order.index(base_scale)

        # Project upward
        current = base_embedding
        for i in range(base_idx, 3):
            src = scale_order[i]
            dst = scale_order[i + 1]
            current = self.project(current, src, dst)
            result[dst] = current

        # Project downward
        current = base_embedding
        for i in range(base_idx, 0, -1):
            src = scale_order[i]
            dst = scale_order[i - 1]
            current = self.project(current, src, dst)
            result[dst] = current

        return result

    def fused_retrieval(
        self,
        query_embedding: np.ndarray,
        candidates: Dict[str, List[Tuple[str, np.ndarray]]],  # scale -> [(id, embedding)]
        top_k: int = 10,
        scale_weights: Optional[Dict[str, float]] = None,
    ) -> List[Tuple[str, float]]:
        """
        Multi-scale fused retrieval.

        Queries at all scales with configurable weighting,
        returning top-k results across all scales.
        """
        if scale_weights is None:
            # Default: higher scales get slightly more weight
            scale_weights = {"L0": 0.2, "L1": 0.25, "L2": 0.3, "L3": 0.25}

        # Project query to all scales
        query_at_scales = self.multi_scale_embedding(query_embedding, "L1")

        scores = []
        for scale, items in candidates.items():
            if scale not in query_at_scales:
                continue

            query_vec = query_at_scales[scale]
            weight = scale_weights.get(scale, 0.25)

            for item_id, item_embedding in items:
                # Cosine similarity
                sim = np.dot(query_vec, item_embedding) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(item_embedding) + 1e-8
                )
                weighted_score = sim * weight
                scores.append((item_id, weighted_score, scale))

        # Sort by weighted score and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(item_id, score) for item_id, score, _ in scores[:top_k]]

    def save(self, path: str) -> None:
        """Save projector weights to file."""
        import json
        data = {
            "dimension": self.dimension,
            "transforms": {}
        }
        for key, transform in self.transforms.items():
            data["transforms"][f"{key[0]}_{key[1]}"] = {
                "weights": transform.weights.tolist(),
                "bias": transform.bias.tolist(),
            }
        with open(path, 'w') as f:
            json.dump(data, f)
        logger.info(f"S2Projector saved to {path}")

    def load(self, path: str) -> None:
        """Load projector weights from file."""
        import json
        with open(path, 'r') as f:
            data = json.load(f)

        self.dimension = data["dimension"]
        for key_str, transform_data in data["transforms"].items():
            src, tgt = key_str.split("_")
            key = (src, tgt)
            if key in self.transforms:
                self.transforms[key].weights = np.array(transform_data["weights"], dtype=np.float32)
                self.transforms[key].bias = np.array(transform_data["bias"], dtype=np.float32)
        logger.info(f"S2Projector loaded from {path}")

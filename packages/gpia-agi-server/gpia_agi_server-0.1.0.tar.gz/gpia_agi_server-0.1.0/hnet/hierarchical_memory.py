from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, TypeAlias, TYPE_CHECKING

try:  # optional dependency
    import faiss

    _FAISS_AVAILABLE = True
except ImportError:  # pragma: no cover - runtime fallback
    faiss = None
    _FAISS_AVAILABLE = False

if TYPE_CHECKING:
    from faiss import Index as FaissIndex
else:
    FaissIndex = Any

import numpy as np

from hnet.dynamic_chunker import DynamicChunker

logger = logging.getLogger(__name__)
if not _FAISS_AVAILABLE:
    logger.warning("faiss not installed, using NumPy-based nearest neighbor search.")


class NumpyIndex:
    """Minimal FAISS-like index using NumPy for L2 search."""

    def __init__(self, dim: int) -> None:
        self.vectors = np.empty((0, dim), dtype="float32")

    @property
    def ntotal(self) -> int:
        return self.vectors.shape[0]

    def add(self, arr: np.ndarray) -> None:
        self.vectors = np.vstack([self.vectors, arr]) if self.ntotal else arr

    def search(self, vec: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        if self.ntotal == 0:
            dists = np.full((1, top_k), np.inf, dtype="float32")
            idxs = np.full((1, top_k), -1, dtype=int)
            return dists, idxs
        dists = np.sum((self.vectors - vec) ** 2, axis=1)
        order = np.argsort(dists)[:top_k]
        sel_dists = dists[order]
        if len(order) < top_k:
            pad = top_k - len(order)
            order = np.concatenate([order, -1 * np.ones(pad, dtype=int)])
            sel_dists = np.concatenate([sel_dists, np.full(pad, np.inf)])
        return sel_dists.reshape(1, -1).astype("float32"), order.reshape(1, -1)


IndexType: TypeAlias = FaissIndex | NumpyIndex


class HierarchicalMemory:
    """Persist conversation chunks with FAISS or NumPy fallback indexing."""

    def __init__(
        self,
        *,
        storage_dir: str | Path = Path("data/hier_mem"),
        embedding_fn: Callable[[str], List[float]] | None = None,
        max_tokens: int = 800,
        overlap_tokens: int = 80,
    ) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.embedding_fn = embedding_fn or self._default_embedder
        self._lock = threading.RLock()
        self.index, self.metadata, self.version = self._load_latest()

    # ------------------------------------------------------------------ utils
    def _default_embedder(self, text: str) -> List[float]:  # pragma: no cover - heavy
        from integrations.openvino_embedder import get_embeddings

        return get_embeddings(text)

    def _align_index_and_metadata(self) -> None:
        """Ensure ``self.index`` and ``self.metadata`` have matching lengths."""
        if self.index is None:
            return
        if len(self.metadata) > self.index.ntotal:
            logger.warning(
                "metadata longer than index; truncating to %d entries", self.index.ntotal
            )
            self.metadata = self.metadata[: self.index.ntotal]
        elif len(self.metadata) < self.index.ntotal:
            logger.warning("metadata shorter than index; rebuilding index from metadata")
            if not self.metadata:
                self.index = None
                return
            vecs = [self.embedding_fn(m["text"]) for m in self.metadata]
            dim = len(vecs[0])
            rebuilt = faiss.IndexFlatL2(dim) if _FAISS_AVAILABLE else NumpyIndex(dim)
            arr = np.array(vecs, dtype="float32")
            if arr.size:
                rebuilt.add(arr)
            self.index = rebuilt

    def _load_latest(self) -> tuple[IndexType | None, List[Dict[str, Any]], int]:
        ext = "faiss" if _FAISS_AVAILABLE else "npy"
        idx_files = sorted(self.storage_dir.glob(f"index_v*.{ext}"))
        if not idx_files:
            return None, [], 0
        latest = idx_files[-1]
        version = int(latest.stem.split("v")[-1])
        if _FAISS_AVAILABLE:
            index = faiss.read_index(str(latest))
        else:
            arr = np.load(latest)
            index = NumpyIndex(arr.shape[1])
            index.add(arr)
        meta_path = self.storage_dir / f"meta_v{version}.json"
        metadata = json.loads(meta_path.read_text()) if meta_path.exists() else []
        # ensure index/metadata alignment
        self.index, self.metadata = index, metadata
        self._align_index_and_metadata()
        assert self.index is None or len(self.metadata) == self.index.ntotal
        return self.index, self.metadata, version

    def _save(self) -> None:
        self._align_index_and_metadata()
        if self.index is not None and len(self.metadata) != self.index.ntotal:
            raise RuntimeError("Index and metadata misaligned")
        self.version += 1
        ext = "faiss" if _FAISS_AVAILABLE else "npy"
        idx_path = self.storage_dir / f"index_v{self.version}.{ext}"
        meta_path = self.storage_dir / f"meta_v{self.version}.json"
        if _FAISS_AVAILABLE:
            assert self.index is not None
            faiss.write_index(self.index, str(idx_path))
        else:
            assert isinstance(self.index, NumpyIndex)
            np.save(str(idx_path), self.index.vectors)
        meta_path.write_text(json.dumps(self.metadata))

    # ------------------------------------------------------------------ public
    def add_segment(self, conversation_id: str, text: str) -> None:
        """Chunk *text*, embed, and persist in the vector index."""

        ch = DynamicChunker(self.max_tokens, self.overlap_tokens)
        chunks = ch.chunk(text)
        vecs = [self.embedding_fn(c) for c in chunks]
        arr = np.array(vecs, dtype="float32")
        with self._lock:
            if self.index is None:
                self.index = (
                    faiss.IndexFlatL2(arr.shape[1])
                    if _FAISS_AVAILABLE
                    else NumpyIndex(arr.shape[1])
                )
            assert self.index is not None
            self.index.add(arr)
            for chunk in chunks:
                self.metadata.append(
                    {
                        "conversation_id": conversation_id,
                        "text": chunk,
                        "version": self.version + 1,
                    }
                )
            self._save()

    def search(self, conversation_id: str, query: str, top_k: int = 5) -> List[str]:
        """Return up to ``top_k`` matching chunks for ``query``."""

        if self.index is None or self.index.ntotal == 0:
            return []
        vec = np.array([self.embedding_fn(query)], dtype="float32")
        with self._lock:
            assert self.index is not None
            dists, idxs = self.index.search(vec, min(top_k * 2, self.index.ntotal))
        out: List[str] = []
        for idx in idxs[0]:
            if idx == -1:
                continue
            meta = self.metadata[idx]
            if meta.get("conversation_id") == conversation_id:
                out.append(meta["text"])
            if len(out) >= top_k:
                break
        return out

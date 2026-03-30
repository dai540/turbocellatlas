from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tca.quantization import exact_topk


@dataclass(slots=True)
class BenchmarkResult:
    indices: np.ndarray
    scores: np.ndarray
    backend: str


class ExactBackend:
    def __init__(self, embeddings: np.ndarray) -> None:
        self.embeddings = np.asarray(embeddings, dtype=np.float32)

    def search(self, query: np.ndarray, top_k: int) -> BenchmarkResult:
        indices, scores = exact_topk(query=query, bank=self.embeddings, top_k=top_k)
        return BenchmarkResult(indices=indices, scores=scores, backend="exact")


class HNSWBackend:
    def __init__(self, embeddings: np.ndarray, space: str = "cosine") -> None:
        try:
            import hnswlib
        except ImportError as exc:
            raise ImportError("hnswlib is required for HNSWBackend. Install with `.[bench]`.") from exc

        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.space = space
        self.index = hnswlib.Index(space=space, dim=self.embeddings.shape[1])
        self.index.init_index(max_elements=self.embeddings.shape[0], ef_construction=200, M=16)
        self.index.add_items(self.embeddings, np.arange(self.embeddings.shape[0]))
        self.index.set_ef(200)

    def search(self, query: np.ndarray, top_k: int) -> BenchmarkResult:
        labels, distances = self.index.knn_query(np.asarray(query, dtype=np.float32), k=top_k)
        scores = (1.0 - distances[0]).astype(np.float32) if self.space == "cosine" else -distances[0].astype(np.float32)
        return BenchmarkResult(indices=labels[0].astype(np.int32), scores=scores, backend="hnswlib")


class FaissPQBackend:
    def __init__(self, embeddings: np.ndarray, n_subquantizers: int = 8, n_bits: int = 8) -> None:
        try:
            import faiss
        except ImportError as exc:
            raise ImportError("faiss-cpu is required for FaissPQBackend. Install with `.[bench]`.") from exc

        self.faiss = faiss
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexPQ(dimension, n_subquantizers, n_bits, faiss.METRIC_INNER_PRODUCT)
        self.index.train(self.embeddings)
        self.index.add(self.embeddings)

    def search(self, query: np.ndarray, top_k: int) -> BenchmarkResult:
        scores, indices = self.index.search(np.asarray(query, dtype=np.float32)[None, :], top_k)
        return BenchmarkResult(
            indices=indices[0].astype(np.int32),
            scores=scores[0].astype(np.float32),
            backend="faiss-pq",
        )

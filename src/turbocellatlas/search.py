from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .config import SearchConfig

Metadata = dict[str, Any]


@dataclass(slots=True)
class SearchResult:
    rank: int
    item_id: str
    score: float
    metadata: Metadata


class SearchIndex:
    """Minimal exact search index over a dense embedding matrix."""

    def __init__(
        self,
        embeddings: np.ndarray,
        metadata: list[Metadata] | None = None,
        config: SearchConfig | None = None,
    ) -> None:
        matrix = np.asarray(embeddings, dtype=np.float32)
        if matrix.ndim != 2:
            raise ValueError("embeddings must be a 2D array")

        self.config = config or SearchConfig()
        self.config.validate()
        self.embeddings = matrix
        self.metadata = metadata or [{"cell_id": str(i)} for i in range(matrix.shape[0])]
        if len(self.metadata) != matrix.shape[0]:
            raise ValueError("metadata length must match embeddings rows")

        self.ids = np.asarray(
            [str(record.get("cell_id", i)) for i, record in enumerate(self.metadata)],
            dtype=object,
        )
        self._search_bank = self._normalize_rows(matrix) if self.config.normalize else matrix

    @staticmethod
    def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        safe_norms = np.where(norms == 0.0, 1.0, norms)
        return matrix / safe_norms

    @staticmethod
    def _normalize_vector(vector: np.ndarray) -> np.ndarray:
        norm = float(np.linalg.norm(vector))
        return vector if norm == 0.0 else vector / norm

    def _mask(self, filters: dict[str, Any] | None) -> np.ndarray:
        mask = np.ones(len(self.metadata), dtype=bool)
        if not filters:
            return mask

        for key, value in filters.items():
            allowed = value if isinstance(value, (list, tuple, set)) else [value]
            mask &= np.array(
                [record.get(key) in allowed for record in self.metadata],
                dtype=bool,
            )
        return mask

    def search(
        self,
        query: np.ndarray,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int | None = None,
    ) -> list[SearchResult]:
        vector = np.asarray(query, dtype=np.float32)
        if vector.ndim != 1 or vector.shape[0] != self.embeddings.shape[1]:
            raise ValueError("query must be a 1D vector matching the embedding dimension")

        active = np.flatnonzero(self._mask(filters))
        if active.size == 0:
            return []

        search_vector = self._normalize_vector(vector) if self.config.normalize else vector
        scores = self._search_bank[active] @ search_vector
        k = min(top_k or self.config.top_k, active.size)
        order = np.argsort(-scores)[:k]

        results: list[SearchResult] = []
        for rank, local_idx in enumerate(order, start=1):
            idx = int(active[local_idx])
            results.append(
                SearchResult(
                    rank=rank,
                    item_id=str(self.ids[idx]),
                    score=float(scores[local_idx]),
                    metadata=self.metadata[idx],
                )
            )
        return results

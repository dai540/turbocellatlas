from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from tca.config import TurboQuantConfig
from tca.planning import plan_query
from tca.quantization import EncodedProd, TurboQuantMSE, TurboQuantProd, exact_topk
from tca.types import MetadataRecord, SearchItem, SearchResults


class SearchIndex:
    def __init__(
        self,
        embeddings: np.ndarray,
        metadata: list[MetadataRecord],
        config: TurboQuantConfig,
    ) -> None:
        config.validate()
        if embeddings.ndim != 2:
            raise ValueError("embeddings must be a 2D array")
        if len(metadata) != embeddings.shape[0]:
            raise ValueError("metadata length must match number of embeddings")

        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.metadata = metadata
        self.config = config
        self.dimension = embeddings.shape[1]
        self.ids = np.array(
            [str(record.get("cell_id", idx)) for idx, record in enumerate(metadata)],
            dtype=object,
        )

        if config.quantizer_kind == "mse":
            self.quantizer = TurboQuantMSE(
                dimension=self.dimension,
                bit_width=config.bit_width,
                seed=config.seed,
                monte_carlo_samples=config.monte_carlo_samples,
                lloyd_max_iter=config.lloyd_max_iter,
                lloyd_tol=config.lloyd_tol,
            )
            self.encoded = self.quantizer.encode(self.embeddings)
        else:
            self.quantizer = TurboQuantProd(
                dimension=self.dimension,
                bit_width=config.bit_width,
                seed=config.seed,
                monte_carlo_samples=config.monte_carlo_samples,
                lloyd_max_iter=config.lloyd_max_iter,
                lloyd_tol=config.lloyd_tol,
            )
            self.encoded = self.quantizer.encode(self.embeddings)
        self.embedding_norms = np.linalg.norm(self.embeddings, axis=1).astype(np.float32)
        self.metadata_columns: dict[str, np.ndarray] = {}
        if metadata:
            keys = set().union(*(record.keys() for record in metadata))
            for key in keys:
                self.metadata_columns[key] = np.asarray([record.get(key) for record in metadata], dtype=object)

    @classmethod
    def from_embeddings(
        cls,
        embeddings: np.ndarray,
        metadata: list[MetadataRecord],
        config: TurboQuantConfig | None = None,
    ) -> "SearchIndex":
        return cls(embeddings=embeddings, metadata=metadata, config=config or TurboQuantConfig())

    def _mask_for_filters(self, filters: dict[str, Any] | None) -> np.ndarray:
        mask = np.ones(len(self.metadata), dtype=bool)
        if not filters:
            return mask
        for key, value in filters.items():
            allowed = value if isinstance(value, (list, tuple, set)) else [value]
            column = self.metadata_columns.get(key)
            if column is None:
                return np.zeros(len(self.metadata), dtype=bool)
            mask &= np.isin(column, list(allowed))
        return mask

    def _candidate_scores(self, query: np.ndarray, active_indices: np.ndarray) -> np.ndarray:
        if isinstance(self.quantizer, TurboQuantProd):
            subset = EncodedProd(
                indices=self.encoded.indices[active_indices],
                signs=self.encoded.signs[active_indices],
                residual_norms=self.encoded.residual_norms[active_indices],
            )
            return self.quantizer.approximate_inner_products(query, subset)
        return self.quantizer.approximate_inner_products(query, self.encoded.indices[active_indices])

    def search(
        self,
        query: np.ndarray,
        filters: dict[str, Any] | None = None,
        *,
        query_mode: str = "auto",
    ) -> SearchResults:
        query_arr = np.asarray(query, dtype=np.float32)
        if query_arr.ndim != 1 or query_arr.shape[0] != self.dimension:
            raise ValueError("query must be a 1D vector with the same dimensionality as the index")

        mask = self._mask_for_filters(filters)
        active_indices = np.flatnonzero(mask)
        if active_indices.size == 0:
            return SearchResults(items=[], backend="turboquant", candidate_count=0, filtered_count=0, diagnostics={"query_mode": query_mode})

        approx_scores = self._candidate_scores(query_arr, active_indices)
        query_plan = plan_query(approx_scores=approx_scores, config=self.config, query_mode=query_mode)
        candidate_count = min(active_indices.size, query_plan.candidate_k * query_plan.oversample)
        approx_order = np.argpartition(-approx_scores, kth=candidate_count - 1)[:candidate_count]
        candidate_indices = active_indices[approx_order]

        final_ids, final_scores = exact_topk(
            query=query_arr,
            bank=self.embeddings[candidate_indices],
            top_k=min(self.config.rerank_k, candidate_indices.size),
            ids=candidate_indices.tolist(),
        )

        items = [
            SearchItem(
                rank=rank + 1,
                item_id=str(self.ids[idx]),
                score=float(score),
                metadata=self.metadata[int(idx)],
            )
            for rank, (idx, score) in enumerate(zip(final_ids.tolist(), final_scores.tolist(), strict=True))
        ]
        return SearchResults(
            items=items,
            backend="turboquant",
            candidate_count=int(candidate_indices.size),
            filtered_count=int(active_indices.size),
            diagnostics={
                "query_mode": query_plan.mode,
                "planned_candidate_k": query_plan.candidate_k,
                "planned_oversample": query_plan.oversample,
                "probe_count": query_plan.probe_count,
                "score_gap": query_plan.score_gap,
                "score_spread": query_plan.score_spread,
            },
        )

    def search_exact(self, query: np.ndarray, filters: dict[str, Any] | None = None) -> SearchResults:
        query_arr = np.asarray(query, dtype=np.float32)
        mask = self._mask_for_filters(filters)
        active_indices = np.flatnonzero(mask)
        if active_indices.size == 0:
            return SearchResults(items=[], backend="exact", candidate_count=0, filtered_count=0, diagnostics={})

        final_ids, final_scores = exact_topk(
            query=query_arr,
            bank=self.embeddings[active_indices],
            top_k=min(self.config.rerank_k, active_indices.size),
            ids=active_indices.tolist(),
        )
        items = [
            SearchItem(
                rank=rank + 1,
                item_id=str(self.ids[idx]),
                score=float(score),
                metadata=self.metadata[int(idx)],
            )
            for rank, (idx, score) in enumerate(zip(final_ids.tolist(), final_scores.tolist(), strict=True))
        ]
        return SearchResults(
            items=items,
            backend="exact",
            candidate_count=int(active_indices.size),
            filtered_count=int(active_indices.size),
            diagnostics={},
        )

    def to_manifest(self) -> dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "n_cells": int(self.embeddings.shape[0]),
            "dimension": int(self.dimension),
            "quantizer_kind": self.config.quantizer_kind,
        }

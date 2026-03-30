from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tca.config import TurboQuantConfig


@dataclass(slots=True)
class QueryPlan:
    mode: str
    candidate_k: int
    oversample: int
    probe_count: int
    score_gap: float
    score_spread: float


def _sample_probe_scores(
    approx_scores: np.ndarray,
    max_probe: int = 4096,
) -> np.ndarray:
    if approx_scores.size <= max_probe:
        return np.sort(approx_scores)[::-1]
    step = max(1, approx_scores.size // max_probe)
    sampled = approx_scores[::step][:max_probe]
    return np.sort(sampled)[::-1]


def plan_query(
    approx_scores: np.ndarray,
    config: TurboQuantConfig,
    query_mode: str = "auto",
) -> QueryPlan:
    if query_mode in {"single_cell", "focused"}:
        return QueryPlan(
            mode=query_mode,
            candidate_k=config.candidate_k,
            oversample=config.oversample,
            probe_count=min(approx_scores.size, 4096),
            score_gap=0.0,
            score_spread=0.0,
        )
    probe = _sample_probe_scores(approx_scores)
    if probe.size < 32:
        return QueryPlan(
            mode="small",
            candidate_k=min(config.candidate_k, approx_scores.size),
            oversample=config.oversample,
            probe_count=probe.size,
            score_gap=0.0,
            score_spread=0.0,
        )

    top_band = probe[: min(32, probe.size)]
    mid_idx = min(probe.size - 1, max(31, probe.size // 4))
    score_gap = float(top_band[0] - probe[mid_idx])
    score_spread = float(np.std(top_band))

    broad = score_gap < config.auto_score_gap_threshold or score_spread < config.auto_score_spread_threshold
    if query_mode == "broad" or (query_mode == "auto" and broad):
        candidate_k = min(config.max_candidate_k, max(config.candidate_k, config.candidate_k * 2))
        oversample = min(config.max_oversample, max(config.oversample, config.oversample * 2))
        mode = "broad"
    else:
        candidate_k = config.candidate_k
        oversample = config.oversample
        mode = "focused" if query_mode == "auto" else query_mode

    return QueryPlan(
        mode=mode,
        candidate_k=candidate_k,
        oversample=oversample,
        probe_count=probe.size,
        score_gap=score_gap,
        score_spread=score_spread,
    )

import numpy as np

from tca.config import TurboQuantConfig
from tca.planning import plan_query


def test_plan_query_keeps_focused_defaults():
    scores = np.linspace(1.0, 0.2, 512, dtype=np.float32)
    plan = plan_query(scores, TurboQuantConfig(candidate_k=128, oversample=2), query_mode="focused")
    assert plan.mode == "focused"
    assert plan.candidate_k == 128
    assert plan.oversample == 2


def test_plan_query_expands_broad_candidates():
    scores = np.linspace(0.95, 0.85, 4096, dtype=np.float32)
    plan = plan_query(scores, TurboQuantConfig(candidate_k=128, oversample=2), query_mode="auto")
    assert plan.mode == "broad"
    assert plan.candidate_k >= 256
    assert plan.oversample >= 4

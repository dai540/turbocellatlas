from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TurboQuantConfig:
    bit_width: int = 3
    candidate_k: int = 128
    rerank_k: int = 20
    oversample: int = 2
    seed: int = 0
    quantizer_kind: str = "prod"
    lloyd_max_iter: int = 100
    lloyd_tol: float = 1e-6
    monte_carlo_samples: int = 20000
    store_original_embeddings: bool = True
    auto_score_gap_threshold: float = 0.06
    auto_score_spread_threshold: float = 0.015
    max_candidate_k: int = 2048
    max_oversample: int = 8

    def validate(self) -> "TurboQuantConfig":
        if self.bit_width < 1:
            raise ValueError("bit_width must be >= 1")
        if self.candidate_k < 1:
            raise ValueError("candidate_k must be >= 1")
        if self.rerank_k < 1:
            raise ValueError("rerank_k must be >= 1")
        if self.oversample < 1:
            raise ValueError("oversample must be >= 1")
        if self.max_candidate_k < self.candidate_k:
            raise ValueError("max_candidate_k must be >= candidate_k")
        if self.max_oversample < self.oversample:
            raise ValueError("max_oversample must be >= oversample")
        if self.quantizer_kind not in {"mse", "prod"}:
            raise ValueError("quantizer_kind must be either 'mse' or 'prod'")
        if self.quantizer_kind == "prod" and self.bit_width < 2:
            raise ValueError("TurboQuant 'prod' requires bit_width >= 2")
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: str | Path) -> "TurboQuantConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**payload).validate()

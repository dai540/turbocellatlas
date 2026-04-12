from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SearchConfig:
    """Configuration for exact cosine search."""

    top_k: int = 5
    normalize: bool = True

    def validate(self) -> None:
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")

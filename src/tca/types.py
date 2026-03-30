from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MetadataRecord = dict[str, Any]


@dataclass(slots=True)
class SearchItem:
    rank: int
    item_id: str
    score: float
    metadata: MetadataRecord = field(default_factory=dict)


@dataclass(slots=True)
class SearchResults:
    items: list[SearchItem]
    backend: str
    candidate_count: int
    filtered_count: int
    diagnostics: MetadataRecord = field(default_factory=dict)

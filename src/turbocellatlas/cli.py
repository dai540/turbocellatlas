from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from .config import SearchConfig
from .search import SearchIndex


def _load_metadata(path: Path | None, rows: int) -> list[dict[str, Any]]:
    if path is None:
        return [{"cell_id": str(i)} for i in range(rows)]

    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tca", description="Minimal exact search for embedding matrices.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Run exact cosine search.")
    search.add_argument("--embeddings", required=True, type=Path)
    search.add_argument("--query", required=True, type=Path)
    search.add_argument("--metadata", type=Path, default=None)
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "search":
        parser.error("unknown command")

    embeddings = np.load(args.embeddings)
    query = np.load(args.query)
    metadata = _load_metadata(args.metadata, int(embeddings.shape[0]))
    index = SearchIndex(embeddings, metadata=metadata, config=SearchConfig(top_k=args.top_k))
    results = [
        {
            "rank": item.rank,
            "item_id": item.item_id,
            "score": item.score,
            "metadata": item.metadata,
        }
        for item in index.search(query)
    ]

    payload = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 0

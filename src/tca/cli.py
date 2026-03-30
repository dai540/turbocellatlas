from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import numpy as np

from tca.config import TurboQuantConfig
from tca.io import load_embeddings, load_metadata, save_json
from tca.pipeline import SearchIndex


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tca", description="TurboCell Atlas CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Run TurboQuant candidate search + exact rerank")
    search.add_argument("--embeddings", required=True, help="Reference embeddings (.npy or .npz)")
    search.add_argument("--metadata", required=True, help="Metadata (.jsonl, .json, .csv)")
    search.add_argument("--query", required=True, help="Query embedding (.npy)")
    search.add_argument("--output", required=True, help="Output JSON path")
    search.add_argument("--bit-width", type=int, default=3)
    search.add_argument("--candidate-k", type=int, default=128)
    search.add_argument("--rerank-k", type=int, default=20)
    search.add_argument("--oversample", type=int, default=2)
    search.add_argument("--seed", type=int, default=0)
    search.add_argument("--quantizer-kind", choices=["mse", "prod"], default="prod")
    search.add_argument("--filter", action="append", default=[], help="Metadata filter in key=value form")

    return parser


def _parse_filters(entries: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Invalid filter: {entry}. Expected key=value")
        key, value = entry.split("=", 1)
        parsed[key] = value
    return parsed


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "search":
        config = TurboQuantConfig(
            bit_width=args.bit_width,
            candidate_k=args.candidate_k,
            rerank_k=args.rerank_k,
            oversample=args.oversample,
            seed=args.seed,
            quantizer_kind=args.quantizer_kind,
        ).validate()
        embeddings = load_embeddings(args.embeddings)
        metadata = load_metadata(args.metadata)
        query = load_embeddings(args.query)
        if query.ndim == 2:
            query = query[0]

        index = SearchIndex.from_embeddings(embeddings=embeddings, metadata=metadata, config=config)
        results = index.search(query=query, filters=_parse_filters(args.filter))
        payload = {
            "manifest": index.to_manifest(),
            "results": [asdict(item) for item in results.items],
            "backend": results.backend,
            "candidate_count": results.candidate_count,
            "filtered_count": results.filtered_count,
        }
        save_json(args.output, payload)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import time

import faiss
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tca import SearchIndex, TurboQuantConfig, __version__
from tca.benchmarks import FaissPQBackend, HNSWBackend
from tca.scimilarity_support import embed_h5ad_with_scimilarity


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT.parent / "artifacts" / "data" / "GSE136831_subsample.h5ad"
MODEL_PATH = ROOT.parent / "artifacts" / "data" / "scimilarity_py" / "scimilarity"
OUT_DIR = ROOT / "artifacts" / "real_data_case_study"
DOC_ASSETS_DIR = ROOT / "docs" / "assets"
NOTEBOOKS_DIR = ROOT / "notebooks"


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def candidate_memory_bytes(n_cells: int, dimension: int, bit_width: int) -> int:
    code_bytes = math.ceil(n_cells * dimension * bit_width / 8)
    norm_bytes = n_cells * 4
    return code_bytes + norm_bytes


def hnsw_index_size_bytes(index: HNSWBackend) -> int:
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as handle:
        tmp = Path(handle.name)
    index.index.save_index(str(tmp))
    size = tmp.stat().st_size
    tmp.unlink(missing_ok=True)
    return size


def faiss_index_size_bytes(index: FaissPQBackend) -> int:
    with tempfile.NamedTemporaryFile(suffix=".faiss", delete=False) as handle:
        tmp = Path(handle.name)
    faiss.write_index(index.index, str(tmp))
    size = tmp.stat().st_size
    tmp.unlink(missing_ok=True)
    return size


def build_embeddings() -> tuple[np.ndarray, pd.DataFrame]:
    embeddings, adata = embed_h5ad_with_scimilarity(DATA_PATH, MODEL_PATH, buffer_size=2048)
    embeddings = embeddings.astype(np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.maximum(norms, 1e-12)
    obs = adata.obs.reset_index(drop=True).copy()
    obs["cell_id"] = [f"cell-{i}" for i in range(obs.shape[0])]
    obs["query_group"] = obs["Disease"].astype(str) + "::" + obs["celltype_name"].astype(str)
    return embeddings, obs


def make_query_specs() -> list[dict[str, str]]:
    return [
        {"name": "IPF myofibroblast centroid", "celltype": "myofibroblast cell", "disease": "IPF", "query_mode": "focused"},
        {"name": "IPF alveolar macrophage centroid", "celltype": "alveolar macrophage", "disease": "IPF", "query_mode": "broad"},
    ]


def timed_call(fn, repeats: int = 5):
    result = None
    timings: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        timings.append(time.perf_counter() - start)
    return result, float(np.mean(timings))


def summarize_hits(hit_ids: list[str], obs: pd.DataFrame, target_celltype: str, target_disease: str) -> dict[str, float]:
    hit_table = obs.set_index("cell_id").loc[hit_ids]
    return {
        "target_celltype_fraction_top20": float((hit_table["celltype_name"] == target_celltype).mean()),
        "target_disease_fraction_top20": float((hit_table["Disease"] == target_disease).mean()),
    }


def topk_metrics(exact_ids: list[str], other_ids: list[str], k: int = 100) -> dict[str, float]:
    exact_set = set(exact_ids[:k])
    other_set = set(other_ids[:k])
    overlap20 = len(set(exact_ids[:20]) & set(other_ids[:20])) / 20.0
    return {
        "recall_at_100_vs_exact": len(exact_set & other_set) / float(k),
        "top20_overlap_vs_exact": overlap20,
    }


def save_plot(summary_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0))

    plot_df = summary_df[summary_df["method"] != "exact"].copy()
    methods = plot_df["method"].unique().tolist()
    queries = plot_df["query"].unique().tolist()
    x = np.arange(len(methods))
    width = 0.35
    palette = ["#0e6b5c", "#9a3412"]
    for i, query_name in enumerate(queries):
        subset = plot_df[plot_df["query"] == query_name].set_index("method").loc[methods]
        axes[0].bar(x + (i - 0.5) * width, subset["recall_at_100_vs_exact"], width=width, label=query_name, color=palette[i])
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(methods, rotation=20, ha="right")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Recall@100 vs exact")
    axes[0].legend(frameon=False)

    latency_df = summary_df.groupby("method", as_index=False)["avg_latency_ms"].mean()
    axes[1].bar(latency_df["method"], latency_df["avg_latency_ms"], color="#2563eb")
    axes[1].set_title("Average query latency (ms)")
    axes[1].tick_params(axis="x", rotation=20)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "benchmark_summary.png", dpi=180)
    fig.savefig(DOC_ASSETS_DIR / "real-data-benchmark-summary.png", dpi=180)
    plt.close(fig)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_data_dictionary(obs: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column in obs.columns:
        series = obs[column]
        rows.append(
            {
                "field": column,
                "table": "obs",
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "n_unique": int(series.nunique(dropna=True)),
                "example": str(series.dropna().iloc[0]) if series.dropna().shape[0] else "",
                "role": {
                    "celltype_name": "query definition and hit interpretation",
                    "Disease": "query definition and enrichment summary",
                    "study": "metadata context",
                    "sample": "metadata context",
                    "cell_id": "stable output identifier",
                    "query_group": "derived query grouping field",
                }.get(column, "metadata context"),
            }
        )
    rows.extend(
        [
            {
                "field": "X",
                "table": "adata",
                "dtype": "float32 sparse/dense after preprocessing",
                "non_null": int(obs.shape[0] * embeddings.shape[1]),
                "n_unique": None,
                "example": "SCimilarity log-normalized aligned expression matrix",
                "role": "embedding input matrix",
            },
            {
                "field": "embedding",
                "table": "derived",
                "dtype": "float32",
                "non_null": int(obs.shape[0] * embeddings.shape[1]),
                "n_unique": None,
                "example": f"{embeddings.shape[1]}-dimensional SCimilarity vector",
                "role": "retrieval representation",
            },
        ]
    )
    return pd.DataFrame(rows)


def write_pipeline_stages(obs: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "stage": 1,
                "name": "load_input_h5ad",
                "input_object": "GSE136831_subsample.h5ad",
                "output_object": "AnnData with counts layer and obs metadata",
                "shape_or_count": f"{obs.shape[0]} cells x 44942 genes",
                "display": "input dataset summary table",
            },
            {
                "stage": 2,
                "name": "align_to_scimilarity_gene_order",
                "input_object": "raw AnnData",
                "output_object": "aligned AnnData",
                "shape_or_count": "gene order matched to SCimilarity model",
                "display": "pipeline stage table",
            },
            {
                "stage": 3,
                "name": "scimilarity_preprocess",
                "input_object": "aligned counts",
                "output_object": "per-10k log1p expression matrix",
                "shape_or_count": f"{obs.shape[0]} cells",
                "display": "methods section + notebook cell",
            },
            {
                "stage": 4,
                "name": "embed_cells",
                "input_object": "preprocessed expression matrix",
                "output_object": "SCimilarity embedding matrix",
                "shape_or_count": f"{embeddings.shape[0]} x {embeddings.shape[1]}",
                "display": "embedding summary table",
            },
            {
                "stage": 5,
                "name": "construct_queries",
                "input_object": "embedding matrix + obs labels",
                "output_object": "centroid queries",
                "shape_or_count": "2 query vectors",
                "display": "query definition table",
            },
            {
                "stage": 6,
                "name": "candidate_generation",
                "input_object": "query vector + index",
                "output_object": "candidate set",
                "shape_or_count": "method-specific candidate pool",
                "display": "candidate vs rerank comparison table",
            },
            {
                "stage": 7,
                "name": "exact_rerank_or_baseline_return",
                "input_object": "candidate set or baseline index",
                "output_object": "ranked top hits",
                "shape_or_count": "top 100 per query and method",
                "display": "top hits table",
            },
            {
                "stage": 8,
                "name": "reporting",
                "input_object": "ranked outputs and metrics",
                "output_object": "csv/json/jsonl/png/md/ipynb artifacts",
                "shape_or_count": "artifact bundle",
                "display": "artifact index",
            },
        ]
    )


def write_artifact_index() -> pd.DataFrame:
    rows = [
        ("benchmark_summary.csv", "table", "per-query benchmark metrics", "reporting and comparison"),
        ("benchmark_summary.json", "json", "benchmark manifest and metrics", "machine-readable report"),
        ("benchmark_log.jsonl", "jsonl", "structured TurboQuant diagnostics", "audit and tuning"),
        ("top_hits.csv", "table", "top-ranked hits per method", "inspection and article examples"),
        ("candidate_rerank_comparison.csv", "table", "candidate vs rerank overlap summaries", "method traceability"),
        ("query_definitions.csv", "table", "query construction details", "query provenance"),
        ("input_data_dictionary.csv", "table", "field-level input dictionary", "input traceability"),
        ("pipeline_stages.csv", "table", "stage-by-stage process summary", "process traceability"),
        ("artifact_index.csv", "table", "artifact catalog", "navigation"),
        ("benchmark_summary.png", "figure", "recall and latency summary plot", "article figure"),
        ("benchmark_report.md", "markdown", "compact benchmark report", "human-readable summary"),
    ]
    return pd.DataFrame(rows, columns=["artifact", "type", "contents", "purpose"])


def write_markdown_report(summary_df: pd.DataFrame, manifest: dict[str, object]) -> None:
    grouped = summary_df.groupby("query")
    lines = [
        "# TurboCell Atlas v0.2.0 Benchmark Report",
        "",
        f"- Dataset: `{manifest['dataset']['path']}`",
        f"- Model: `{manifest['dataset']['model_path']}`",
        f"- Embedding: {manifest['dataset']['embedding_method']}",
        "",
    ]
    for query_name, frame in grouped:
        lines.append(f"## {query_name}")
        lines.append("")
        lines.append("| Method | Recall@100 | Top20 overlap | Avg latency ms | Candidate memory MB | Query mode |")
        lines.append("| --- | ---: | ---: | ---: | ---: | --- |")
        for _, row in frame.iterrows():
            lines.append(
                f"| {row['method']} | {row['recall_at_100_vs_exact']:.2f} | {row['top20_overlap_vs_exact']:.2f} | "
                f"{row['avg_latency_ms']:.2f} | {row['candidate_memory_mb']:.2f} | {row.get('query_mode','n/a')} |"
            )
        lines.append("")
    (OUT_DIR / "benchmark_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_notebooks(summary_csv: Path) -> None:
    benchmark_nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# TurboCell Atlas End-to-End Benchmark Walkthrough\n",
                    "This notebook follows the full chain from input dataset description through process stages, query definition, benchmark results, and artifacts."
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    f"summary = pd.read_csv(r'{summary_csv}')\n",
                    f"data_dict = pd.read_csv(r'{OUT_DIR / 'input_data_dictionary.csv'}')\n",
                    f"stages = pd.read_csv(r'{OUT_DIR / 'pipeline_stages.csv'}')\n",
                    f"queries = pd.read_csv(r'{OUT_DIR / 'query_definitions.csv'}')\n",
                    "data_dict\n",
                    "stages\n",
                    "queries\n",
                    "summary\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "summary.pivot(index='method', columns='query', values='recall_at_100_vs_exact')\n",
                ],
            },
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    retrieval_nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# TurboCell Atlas Retrieval Trace Notebook\n",
                    "This notebook shows query provenance, candidate-vs-rerank comparison, and final hit tables."
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    f"hits = pd.read_csv(r'{OUT_DIR / 'top_hits.csv'}')\n",
                    f"cmp = pd.read_csv(r'{OUT_DIR / 'candidate_rerank_comparison.csv'}')\n",
                    f"queries = pd.read_csv(r'{OUT_DIR / 'query_definitions.csv'}')\n",
                    "queries\n",
                    "cmp\n",
                    "hits.head(20)\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "hits.groupby(['query','method']).head(10)\n",
                ],
            },
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (NOTEBOOKS_DIR / "benchmark_walkthrough.ipynb").write_text(json.dumps(benchmark_nb, indent=2), encoding="utf-8")
    (NOTEBOOKS_DIR / "retrieval_demo.ipynb").write_text(json.dumps(retrieval_nb, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    embeddings, obs = build_embeddings()
    metadata = obs.to_dict(orient="records")
    exact_bank_bytes = int(embeddings.nbytes)

    query_specs = make_query_specs()
    obs_indexed = obs.set_index("cell_id")

    exact_index = SearchIndex.from_embeddings(
        embeddings=embeddings,
        metadata=metadata,
        config=TurboQuantConfig(bit_width=2, candidate_k=512, rerank_k=100, seed=7, quantizer_kind="mse"),
    )
    turbo_indices = {
        bit_width: SearchIndex.from_embeddings(
            embeddings=embeddings,
            metadata=metadata,
            config=TurboQuantConfig(bit_width=bit_width, candidate_k=512, rerank_k=100, oversample=4, seed=7, quantizer_kind="prod"),
        )
        for bit_width in (2, 3, 4)
    }
    faiss_index = FaissPQBackend(embeddings, n_subquantizers=8, n_bits=8)
    hnsw_index = HNSWBackend(embeddings, space="cosine")

    faiss_memory = faiss_index_size_bytes(faiss_index)
    hnsw_memory = hnsw_index_size_bytes(hnsw_index)

    summary_rows: list[dict[str, object]] = []
    top_hit_rows: list[dict[str, object]] = []
    log_rows: list[dict[str, object]] = []
    query_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []

    for spec in query_specs:
        mask = (obs["celltype_name"] == spec["celltype"]) & (obs["Disease"] == spec["disease"])
        query = embeddings[mask.to_numpy()].mean(axis=0).astype(np.float32)
        query = query / np.linalg.norm(query)
        query_rows.append(
            {
                "query": spec["name"],
                "query_mode": spec["query_mode"],
                "disease": spec["disease"],
                "celltype": spec["celltype"],
                "n_source_cells": int(mask.sum()),
                "embedding_dim": int(query.shape[0]),
                "query_norm": float(np.linalg.norm(query)),
            }
        )

        exact_results, exact_latency = timed_call(lambda: exact_index.search_exact(query))
        exact_ids = [item.item_id for item in exact_results.items]
        exact_summary = summarize_hits(exact_ids[:20], obs, spec["celltype"], spec["disease"])
        summary_rows.append(
            {
                "query": spec["name"],
                "method": "exact",
                "recall_at_100_vs_exact": 1.0,
                "top20_overlap_vs_exact": 1.0,
                "avg_latency_ms": exact_latency * 1000.0,
                "candidate_memory_mb": exact_bank_bytes / 1024**2,
                "query_mode": spec["query_mode"],
                **exact_summary,
            }
        )
        for item in exact_results.items[:10]:
            row = obs_indexed.loc[item.item_id].to_dict()
            row.update({"query": spec["name"], "method": "exact", "rank": item.rank, "score": item.score, "item_id": item.item_id})
            top_hit_rows.append(row)

        for bit_width, turbo_index in turbo_indices.items():
            turbo_results, turbo_latency = timed_call(lambda idx=turbo_index, mode=spec["query_mode"]: idx.search(query, query_mode=mode))
            turbo_ids = [item.item_id for item in turbo_results.items]
            metrics = topk_metrics(exact_ids, turbo_ids, k=100)
            enrich = summarize_hits(turbo_ids[:20], obs, spec["celltype"], spec["disease"])
            summary_row = {
                "query": spec["name"],
                "method": f"turboquant-prod-b{bit_width}",
                "avg_latency_ms": turbo_latency * 1000.0,
                "candidate_memory_mb": candidate_memory_bytes(obs.shape[0], embeddings.shape[1], bit_width) / 1024**2,
                "query_mode": turbo_results.diagnostics.get("query_mode", spec["query_mode"]),
                **metrics,
                **enrich,
            }
            summary_rows.append(summary_row)
            log_rows.append(
                {
                    "event": "turboquant_search",
                    "query": spec["name"],
                    "method": summary_row["method"],
                    "timestamp": time.time(),
                    "diagnostics": turbo_results.diagnostics,
                    "metrics": {k: summary_row[k] for k in ["recall_at_100_vs_exact", "top20_overlap_vs_exact", "avg_latency_ms", "candidate_memory_mb"]},
                }
            )
            candidate_rows.append(
                {
                    "query": spec["name"],
                    "method": summary_row["method"],
                    "query_mode": summary_row["query_mode"],
                    "candidate_count": turbo_results.candidate_count,
                    "filtered_count": turbo_results.filtered_count,
                    "top20_overlap_vs_exact": summary_row["top20_overlap_vs_exact"],
                    "recall_at_100_vs_exact": summary_row["recall_at_100_vs_exact"],
                    "planned_candidate_k": turbo_results.diagnostics.get("planned_candidate_k"),
                    "planned_oversample": turbo_results.diagnostics.get("planned_oversample"),
                    "score_gap": turbo_results.diagnostics.get("score_gap"),
                    "score_spread": turbo_results.diagnostics.get("score_spread"),
                }
            )
            for item in turbo_results.items[:10]:
                row = obs_indexed.loc[item.item_id].to_dict()
                row.update({"query": spec["name"], "method": f"turboquant-prod-b{bit_width}", "rank": item.rank, "score": item.score, "item_id": item.item_id})
                top_hit_rows.append(row)

        faiss_result, faiss_latency = timed_call(lambda: faiss_index.search(query, 100))
        faiss_hit_ids = [metadata[int(idx)]["cell_id"] for idx in faiss_result.indices.tolist()]
        metrics = topk_metrics(exact_ids, faiss_hit_ids, k=100)
        enrich = summarize_hits(faiss_hit_ids[:20], obs, spec["celltype"], spec["disease"])
        summary_rows.append(
            {
                "query": spec["name"],
                "method": "faiss-pq-m8-nbits8",
                "avg_latency_ms": faiss_latency * 1000.0,
                "candidate_memory_mb": faiss_memory / 1024**2,
                "query_mode": spec["query_mode"],
                **metrics,
                **enrich,
            }
        )
        for rank, (item_id, score) in enumerate(zip(faiss_hit_ids[:10], faiss_result.scores.tolist()[:10], strict=True), start=1):
            row = obs_indexed.loc[item_id].to_dict()
            row.update({"query": spec["name"], "method": "faiss-pq-m8-nbits8", "rank": rank, "score": float(score), "item_id": item_id})
            top_hit_rows.append(row)

        hnsw_result, hnsw_latency = timed_call(lambda: hnsw_index.search(query, 100))
        hnsw_hit_ids = [metadata[int(idx)]["cell_id"] for idx in hnsw_result.indices.tolist()]
        metrics = topk_metrics(exact_ids, hnsw_hit_ids, k=100)
        enrich = summarize_hits(hnsw_hit_ids[:20], obs, spec["celltype"], spec["disease"])
        summary_rows.append(
            {
                "query": spec["name"],
                "method": "hnswlib-cosine",
                "avg_latency_ms": hnsw_latency * 1000.0,
                "candidate_memory_mb": hnsw_memory / 1024**2,
                "query_mode": spec["query_mode"],
                **metrics,
                **enrich,
            }
        )
        for rank, (item_id, score) in enumerate(zip(hnsw_hit_ids[:10], hnsw_result.scores.tolist()[:10], strict=True), start=1):
            row = obs_indexed.loc[item_id].to_dict()
            row.update({"query": spec["name"], "method": "hnswlib-cosine", "rank": rank, "score": float(score), "item_id": item_id})
            top_hit_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    top_hits_df = pd.DataFrame(top_hit_rows)
    query_df = pd.DataFrame(query_rows)
    candidate_df = pd.DataFrame(candidate_rows)
    data_dictionary_df = write_data_dictionary(obs, embeddings)
    pipeline_df = write_pipeline_stages(obs, embeddings)
    artifact_index_df = write_artifact_index()
    summary_df.to_csv(OUT_DIR / "benchmark_summary.csv", index=False)
    top_hits_df.to_csv(OUT_DIR / "top_hits.csv", index=False)
    query_df.to_csv(OUT_DIR / "query_definitions.csv", index=False)
    candidate_df.to_csv(OUT_DIR / "candidate_rerank_comparison.csv", index=False)
    data_dictionary_df.to_csv(OUT_DIR / "input_data_dictionary.csv", index=False)
    pipeline_df.to_csv(OUT_DIR / "pipeline_stages.csv", index=False)
    artifact_index_df.to_csv(OUT_DIR / "artifact_index.csv", index=False)
    save_plot(summary_df)

    payload = {
        "package_version": __version__,
        "dataset": {
            "path": str(DATA_PATH),
            "model_path": str(MODEL_PATH),
            "embedding_method": "SCimilarity encoder v1 embedding + l2 normalization",
            "n_cells": int(obs.shape[0]),
            "n_genes": 44942,
            "disease_counts": obs["Disease"].value_counts().to_dict(),
            "top_celltypes": obs["celltype_name"].value_counts().head(10).to_dict(),
        },
        "queries": query_specs,
        "results": summary_rows,
    }
    (OUT_DIR / "benchmark_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_jsonl(OUT_DIR / "benchmark_log.jsonl", log_rows)
    write_markdown_report(summary_df, payload)
    write_notebooks(OUT_DIR / "benchmark_summary.csv")


if __name__ == "__main__":
    main()

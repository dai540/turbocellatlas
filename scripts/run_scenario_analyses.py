from __future__ import annotations

import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tca import SearchIndex, TurboQuantConfig
from tca.benchmarks import FaissPQBackend, HNSWBackend
from tca.quantization import exact_topk
from tca.types import SearchResults

from run_real_data_case_study import build_embeddings, candidate_memory_bytes


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "artifacts" / "scenario_articles"
DOC_ASSETS_DIR = ROOT / "docs" / "assets"


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def timed_call(fn, repeats: int = 5):
    result = None
    timings: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        timings.append(time.perf_counter() - start)
    return result, float(np.mean(timings)) * 1000.0


def make_query(embeddings: np.ndarray, obs: pd.DataFrame, celltype: str, disease: str) -> np.ndarray:
    mask = (obs["celltype_name"] == celltype) & (obs["Disease"] == disease)
    query = embeddings[mask.to_numpy()].mean(axis=0).astype(np.float32)
    return query / np.maximum(np.linalg.norm(query), 1e-12)


def result_to_ids(results: SearchResults) -> list[str]:
    return [item.item_id for item in results.items]


def topk_overlap(reference_ids: list[str], other_ids: list[str], k: int = 20) -> float:
    return len(set(reference_ids[:k]) & set(other_ids[:k])) / float(k)


def recall_at_k(reference_ids: list[str], other_ids: list[str], k: int = 100) -> float:
    return len(set(reference_ids[:k]) & set(other_ids[:k])) / float(k)


def top_disease_counts(hit_ids: list[str], obs_indexed: pd.DataFrame, top_k: int = 20) -> dict[str, int]:
    hit_table = obs_indexed.loc[hit_ids[:top_k]]
    counts = hit_table["Disease"].value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def top_celltype_fraction(hit_ids: list[str], obs_indexed: pd.DataFrame, target_celltype: str, top_k: int = 20) -> float:
    hit_table = obs_indexed.loc[hit_ids[:top_k]]
    return float((hit_table["celltype_name"] == target_celltype).mean())


def top_disease_fraction(hit_ids: list[str], obs_indexed: pd.DataFrame, target_disease: str, top_k: int = 20) -> float:
    hit_table = obs_indexed.loc[hit_ids[:top_k]]
    return float((hit_table["Disease"] == target_disease).mean())


def search_faiss_subset(index: FaissPQBackend, query: np.ndarray, active_indices: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
    subset = index.embeddings[active_indices]
    ids, scores = exact_topk(query=query, bank=subset, top_k=min(top_k, subset.shape[0]), ids=active_indices.tolist())
    return ids, scores


def search_hnsw_subset(index: HNSWBackend, query: np.ndarray, active_indices: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
    labels, distances = index.index.knn_query(np.asarray(query, dtype=np.float32), k=min(index.embeddings.shape[0], max(top_k * 5, 512)))
    ordered = [int(idx) for idx in labels[0].tolist() if int(idx) in set(active_indices.tolist())]
    chosen = ordered[:top_k]
    scores = np.dot(index.embeddings[np.asarray(chosen, dtype=np.int32)], np.asarray(query, dtype=np.float32))
    return np.asarray(chosen, dtype=np.int32), np.asarray(scores, dtype=np.float32)


def save_rare_state_plot(df: pd.DataFrame) -> None:
    order = ["exact", "turboquant-prod-b2", "turboquant-prod-b3", "turboquant-prod-b4", "faiss-pq-m8-nbits8", "hnswlib-cosine"]
    plot_df = df.set_index("method").loc[order].reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

    axes[0].bar(plot_df["method"], plot_df["recall_at_100_vs_exact"], color=["#d7dfe2", "#0f6c63", "#1f8a70", "#4aa382", "#b65a2a", "#355c7d"])
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Rare-state recall@100")
    axes[0].tick_params(axis="x", rotation=24)

    axes[1].bar(plot_df["method"], plot_df["candidate_memory_mb"], color=["#d7dfe2", "#0f6c63", "#1f8a70", "#4aa382", "#b65a2a", "#355c7d"])
    axes[1].set_title("Candidate-layer memory (MB)")
    axes[1].tick_params(axis="x", rotation=24)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "rare_state_thumbnail.png", dpi=180)
    fig.savefig(DOC_ASSETS_DIR / "scenario-rare-state.png", dpi=180)
    plt.close(fig)


def save_cohort_triage_plot(composition_df: pd.DataFrame) -> None:
    disease_order = ["IPF", "healthy", "COPD"]
    methods = composition_df["scope_method"].tolist()
    bottom = np.zeros(len(methods), dtype=np.float32)
    colors = {"IPF": "#0f6c63", "healthy": "#d8c7a0", "COPD": "#b65a2a"}

    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    for disease in disease_order:
        values = composition_df[disease].to_numpy(dtype=np.float32)
        ax.bar(methods, values, bottom=bottom, label=disease, color=colors[disease])
        bottom += values
    ax.set_ylim(0, 20)
    ax.set_title("Top-20 disease composition by cohort scope")
    ax.legend(frameon=False)
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "cohort_triage_thumbnail.png", dpi=180)
    fig.savefig(DOC_ASSETS_DIR / "scenario-cohort-triage.png", dpi=180)
    plt.close(fig)


def save_broad_state_plot(df: pd.DataFrame) -> None:
    order = ["turboquant-prod-b2", "turboquant-prod-b3", "turboquant-prod-b4"]
    focused = df[df["query_mode"] == "focused"].set_index("method").loc[order]
    broad = df[df["query_mode"] == "broad"].set_index("method").loc[order]

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    x = np.arange(len(order))
    width = 0.36

    axes[0].bar(x - width / 2, focused["recall_at_100_vs_exact"], width=width, color="#b65a2a", label="focused")
    axes[0].bar(x + width / 2, broad["recall_at_100_vs_exact"], width=width, color="#0f6c63", label="broad")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(order, rotation=20)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Broad-state recall@100")
    axes[0].legend(frameon=False)

    axes[1].bar(x - width / 2, focused["candidate_count"], width=width, color="#b65a2a", label="focused")
    axes[1].bar(x + width / 2, broad["candidate_count"], width=width, color="#0f6c63", label="broad")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(order, rotation=20)
    axes[1].set_title("Candidate pool size")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "broad_state_thumbnail.png", dpi=180)
    fig.savefig(DOC_ASSETS_DIR / "scenario-broad-state.png", dpi=180)
    plt.close(fig)


def save_single_cell_plot(df: pd.DataFrame) -> None:
    order = ["exact", "turboquant-prod-b3", "hnswlib-cosine"]
    plot_df = df.set_index("method").loc[order].reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))

    axes[0].bar(plot_df["method"], plot_df["target_celltype_fraction_top20"], color=["#d7dfe2", "#0f6c63", "#355c7d"])
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Top-20 same cell type fraction")
    axes[0].tick_params(axis="x", rotation=20)

    axes[1].bar(plot_df["method"], plot_df["top20_overlap_vs_exact"], color=["#d7dfe2", "#0f6c63", "#355c7d"])
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Top-20 overlap vs exact")
    axes[1].tick_params(axis="x", rotation=20)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "single_cell_thumbnail.png", dpi=180)
    fig.savefig(DOC_ASSETS_DIR / "scenario-single-cell.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    embeddings, obs = build_embeddings()
    metadata = obs.to_dict(orient="records")
    obs_indexed = obs.set_index("cell_id")

    exact_index = SearchIndex.from_embeddings(
        embeddings=embeddings,
        metadata=metadata,
        config=TurboQuantConfig(bit_width=2, candidate_k=512, rerank_k=100, oversample=4, seed=7, quantizer_kind="mse"),
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

    scenario_manifest: dict[str, object] = {"dataset_cells": int(obs.shape[0]), "scenarios": {}}

    rare_query = make_query(embeddings, obs, celltype="myofibroblast cell", disease="IPF")
    exact_res, exact_ms = timed_call(lambda: exact_index.search_exact(rare_query))
    exact_ids = result_to_ids(exact_res)
    rare_rows: list[dict[str, object]] = [
        {
            "method": "exact",
            "query": "IPF myofibroblast centroid",
            "recall_at_100_vs_exact": 1.0,
            "top20_overlap_vs_exact": 1.0,
            "avg_latency_ms": exact_ms,
            "candidate_memory_mb": embeddings.nbytes / (1024 * 1024),
            "target_celltype_fraction_top20": top_celltype_fraction(exact_ids, obs_indexed, "myofibroblast cell"),
            "target_disease_fraction_top20": top_disease_fraction(exact_ids, obs_indexed, "IPF"),
        }
    ]
    for bit_width, index in turbo_indices.items():
        res, latency_ms = timed_call(lambda idx=index: idx.search(rare_query, query_mode="focused"))
        ids = result_to_ids(res)
        rare_rows.append(
            {
                "method": f"turboquant-prod-b{bit_width}",
                "query": "IPF myofibroblast centroid",
                "recall_at_100_vs_exact": recall_at_k(exact_ids, ids, k=100),
                "top20_overlap_vs_exact": topk_overlap(exact_ids, ids, k=20),
                "avg_latency_ms": latency_ms,
                "candidate_memory_mb": candidate_memory_bytes(obs.shape[0], embeddings.shape[1], bit_width) / (1024 * 1024),
                "target_celltype_fraction_top20": top_celltype_fraction(ids, obs_indexed, "myofibroblast cell"),
                "target_disease_fraction_top20": top_disease_fraction(ids, obs_indexed, "IPF"),
            }
        )
    faiss_ids, faiss_ms = timed_call(lambda: faiss_index.search(rare_query, top_k=100))
    faiss_hit_ids = obs.iloc[faiss_ids.indices]["cell_id"].tolist()
    rare_rows.append(
        {
            "method": "faiss-pq-m8-nbits8",
            "query": "IPF myofibroblast centroid",
            "recall_at_100_vs_exact": recall_at_k(exact_ids, faiss_hit_ids, k=100),
            "top20_overlap_vs_exact": topk_overlap(exact_ids, faiss_hit_ids, k=20),
            "avg_latency_ms": faiss_ms,
            "candidate_memory_mb": 0.5065517425537109,
            "target_celltype_fraction_top20": top_celltype_fraction(faiss_hit_ids, obs_indexed, "myofibroblast cell"),
            "target_disease_fraction_top20": top_disease_fraction(faiss_hit_ids, obs_indexed, "IPF"),
        }
    )
    hnsw_ids, hnsw_ms = timed_call(lambda: hnsw_index.search(rare_query, top_k=100))
    hnsw_hit_ids = obs.iloc[hnsw_ids.indices]["cell_id"].tolist()
    rare_rows.append(
        {
            "method": "hnswlib-cosine",
            "query": "IPF myofibroblast centroid",
            "recall_at_100_vs_exact": recall_at_k(exact_ids, hnsw_hit_ids, k=100),
            "top20_overlap_vs_exact": topk_overlap(exact_ids, hnsw_hit_ids, k=20),
            "avg_latency_ms": hnsw_ms,
            "candidate_memory_mb": 31.68560791015625,
            "target_celltype_fraction_top20": top_celltype_fraction(hnsw_hit_ids, obs_indexed, "myofibroblast cell"),
            "target_disease_fraction_top20": top_disease_fraction(hnsw_hit_ids, obs_indexed, "IPF"),
        }
    )
    rare_df = pd.DataFrame(rare_rows)
    rare_df.to_csv(OUT_DIR / "rare_state_summary.csv", index=False)
    save_rare_state_plot(rare_df)
    scenario_manifest["scenarios"]["rare_state"] = {"summary": "rare_state_summary.csv"}

    triage_query = make_query(embeddings, obs, celltype="alveolar macrophage", disease="IPF")
    triage_rows: list[dict[str, object]] = []
    triage_comp_rows: list[dict[str, object]] = []
    for scope_name, filters in [("all_cells", None), ("ipf_only", {"Disease": "IPF"})]:
        exact_scope_res, exact_scope_ms = timed_call(lambda flt=filters: exact_index.search_exact(triage_query, filters=flt))
        exact_scope_ids = result_to_ids(exact_scope_res)
        exact_counts = top_disease_counts(exact_scope_ids, obs_indexed)
        triage_rows.append(
            {
                "scope": scope_name,
                "method": "exact",
                "active_cells": exact_scope_res.filtered_count,
                "avg_latency_ms": exact_scope_ms,
                "target_celltype_fraction_top20": top_celltype_fraction(exact_scope_ids, obs_indexed, "alveolar macrophage"),
                "target_disease_fraction_top20": top_disease_fraction(exact_scope_ids, obs_indexed, "IPF"),
                "top20_overlap_vs_exact_in_scope": 1.0,
            }
        )
        triage_comp_rows.append(
            {
                "scope_method": f"{scope_name}: exact",
                "IPF": exact_counts.get("IPF", 0),
                "healthy": exact_counts.get("healthy", 0),
                "COPD": exact_counts.get("COPD", 0),
            }
        )

        turbo_scope_res, turbo_scope_ms = timed_call(lambda flt=filters: turbo_indices[3].search(triage_query, filters=flt, query_mode="focused"))
        turbo_scope_ids = result_to_ids(turbo_scope_res)
        turbo_counts = top_disease_counts(turbo_scope_ids, obs_indexed)
        triage_rows.append(
            {
                "scope": scope_name,
                "method": "turboquant-prod-b3",
                "active_cells": turbo_scope_res.filtered_count,
                "avg_latency_ms": turbo_scope_ms,
                "target_celltype_fraction_top20": top_celltype_fraction(turbo_scope_ids, obs_indexed, "alveolar macrophage"),
                "target_disease_fraction_top20": top_disease_fraction(turbo_scope_ids, obs_indexed, "IPF"),
                "top20_overlap_vs_exact_in_scope": topk_overlap(exact_scope_ids, turbo_scope_ids, k=20),
            }
        )
        triage_comp_rows.append(
            {
                "scope_method": f"{scope_name}: turbo",
                "IPF": turbo_counts.get("IPF", 0),
                "healthy": turbo_counts.get("healthy", 0),
                "COPD": turbo_counts.get("COPD", 0),
            }
        )
    triage_df = pd.DataFrame(triage_rows)
    triage_comp_df = pd.DataFrame(triage_comp_rows)
    triage_df.to_csv(OUT_DIR / "cohort_triage_summary.csv", index=False)
    triage_comp_df.to_csv(OUT_DIR / "cohort_triage_disease_composition.csv", index=False)
    save_cohort_triage_plot(triage_comp_df)
    scenario_manifest["scenarios"]["cohort_triage"] = {
        "summary": "cohort_triage_summary.csv",
        "composition": "cohort_triage_disease_composition.csv",
    }

    broad_query = triage_query
    exact_broad_res, _ = timed_call(lambda: exact_index.search_exact(broad_query))
    exact_broad_ids = result_to_ids(exact_broad_res)
    broad_rows: list[dict[str, object]] = []
    for mode in ("focused", "broad"):
        for bit_width, index in turbo_indices.items():
            res, latency_ms = timed_call(lambda idx=index, qmode=mode: idx.search(broad_query, query_mode=qmode))
            ids = result_to_ids(res)
            broad_rows.append(
                {
                    "query": "IPF alveolar macrophage centroid",
                    "method": f"turboquant-prod-b{bit_width}",
                    "query_mode": mode,
                    "candidate_count": res.candidate_count,
                    "planned_candidate_k": res.diagnostics.get("planned_candidate_k", index.config.candidate_k),
                    "planned_oversample": res.diagnostics.get("planned_oversample", index.config.oversample),
                    "recall_at_100_vs_exact": recall_at_k(exact_broad_ids, ids, k=100),
                    "top20_overlap_vs_exact": topk_overlap(exact_broad_ids, ids, k=20),
                    "avg_latency_ms": latency_ms,
                    "target_disease_fraction_top20": top_disease_fraction(ids, obs_indexed, "IPF"),
                }
            )
    broad_df = pd.DataFrame(broad_rows)
    broad_df.to_csv(OUT_DIR / "broad_state_tuning_summary.csv", index=False)
    save_broad_state_plot(broad_df)
    scenario_manifest["scenarios"]["broad_state"] = {"summary": "broad_state_tuning_summary.csv"}

    single_mask = (obs["celltype_name"] == "myofibroblast cell") & (obs["Disease"] == "IPF")
    single_idx = int(np.flatnonzero(single_mask.to_numpy())[0])
    single_query = embeddings[single_idx]
    single_meta = obs.iloc[single_idx]
    exact_single_res, exact_single_ms = timed_call(lambda: exact_index.search_exact(single_query))
    exact_single_ids = result_to_ids(exact_single_res)
    turbo_single_res, turbo_single_ms = timed_call(lambda: turbo_indices[3].search(single_query, query_mode="single_cell"))
    turbo_single_ids = result_to_ids(turbo_single_res)
    hnsw_single_res, hnsw_single_ms = timed_call(lambda: hnsw_index.search(single_query, top_k=100))
    hnsw_single_ids = obs.iloc[hnsw_single_res.indices]["cell_id"].tolist()

    single_rows = [
        {
            "method": "exact",
            "query": "single IPF myofibroblast cell",
            "query_sample": str(single_meta["sample"]),
            "target_celltype_fraction_top20": top_celltype_fraction(exact_single_ids, obs_indexed, "myofibroblast cell"),
            "target_disease_fraction_top20": top_disease_fraction(exact_single_ids, obs_indexed, "IPF"),
            "top20_overlap_vs_exact": 1.0,
            "recall_at_100_vs_exact": 1.0,
            "avg_latency_ms": exact_single_ms,
        },
        {
            "method": "turboquant-prod-b3",
            "query": "single IPF myofibroblast cell",
            "query_sample": str(single_meta["sample"]),
            "target_celltype_fraction_top20": top_celltype_fraction(turbo_single_ids, obs_indexed, "myofibroblast cell"),
            "target_disease_fraction_top20": top_disease_fraction(turbo_single_ids, obs_indexed, "IPF"),
            "top20_overlap_vs_exact": topk_overlap(exact_single_ids, turbo_single_ids, k=20),
            "recall_at_100_vs_exact": recall_at_k(exact_single_ids, turbo_single_ids, k=100),
            "avg_latency_ms": turbo_single_ms,
        },
        {
            "method": "hnswlib-cosine",
            "query": "single IPF myofibroblast cell",
            "query_sample": str(single_meta["sample"]),
            "target_celltype_fraction_top20": top_celltype_fraction(hnsw_single_ids, obs_indexed, "myofibroblast cell"),
            "target_disease_fraction_top20": top_disease_fraction(hnsw_single_ids, obs_indexed, "IPF"),
            "top20_overlap_vs_exact": topk_overlap(exact_single_ids, hnsw_single_ids, k=20),
            "recall_at_100_vs_exact": recall_at_k(exact_single_ids, hnsw_single_ids, k=100),
            "avg_latency_ms": hnsw_single_ms,
        },
    ]
    single_df = pd.DataFrame(single_rows)
    single_df.to_csv(OUT_DIR / "single_cell_query_summary.csv", index=False)
    save_single_cell_plot(single_df)
    scenario_manifest["scenarios"]["single_cell_query"] = {"summary": "single_cell_query_summary.csv"}

    (OUT_DIR / "scenario_manifest.json").write_text(json.dumps(scenario_manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

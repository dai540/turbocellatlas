from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = ROOT / "artifacts" / "scenario_articles"
REAL_DIR = ROOT / "artifacts" / "real_data_case_study"
OUT_DIR = ROOT / "artifacts" / "wetlab_examples"
DOC_ASSETS_DIR = ROOT / "docs" / "assets"


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def save_plot(rare_df: pd.DataFrame, cohort_df: pd.DataFrame, broad_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6))

    rare_plot = rare_df.set_index("method").loc[["exact", "turboquant-prod-b3", "faiss-pq-m8-nbits8", "hnswlib-cosine"]]
    axes[0].bar(
        rare_plot.index,
        rare_plot["target_celltype_fraction_top20"],
        color=["#d7dfe2", "#0f6c63", "#b65a2a", "#355c7d"],
    )
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Do we get the same cell type back?")
    axes[0].tick_params(axis="x", rotation=24)

    cohort_plot = cohort_df.set_index("scope_method").loc[["all_cells: exact", "ipf_only: exact"]]
    axes[1].bar(cohort_plot.index, cohort_plot["IPF"], color=["#b65a2a", "#0f6c63"])
    axes[1].set_ylim(0, 20.5)
    axes[1].set_title("How many of the top-20 are IPF?")
    axes[1].tick_params(axis="x", rotation=20)

    broad_plot = broad_df.set_index(["method", "query_mode"]).sort_index()
    axes[2].bar(
        ["focused", "broad"],
        [
            broad_plot.loc[("turboquant-prod-b3", "focused"), "recall_at_100_vs_exact"],
            broad_plot.loc[("turboquant-prod-b3", "broad"), "recall_at_100_vs_exact"],
        ],
        color=["#b65a2a", "#0f6c63"],
    )
    axes[2].set_ylim(0, 1.05)
    axes[2].set_title("Does a broader search help?")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "wetlab-use-cases.png", dpi=180)
    fig.savefig(DOC_ASSETS_DIR / "wetlab-use-cases.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()

    rare_df = pd.read_csv(SCENARIO_DIR / "rare_state_summary.csv")
    cohort_df = pd.read_csv(SCENARIO_DIR / "cohort_triage_disease_composition.csv")
    broad_df = pd.read_csv(SCENARIO_DIR / "broad_state_tuning_summary.csv")
    top_hits_df = pd.read_csv(REAL_DIR / "top_hits.csv")

    use_cases = pd.DataFrame(
        [
            {
                "use_case": "rare_state_lookup",
                "plain_question": "If I search with a disease-like fibroblast state, do I get back the same kind of cells?",
                "main_takeaway": "Yes. TurboQuant and exact returned the same top-100 neighborhood for the myofibroblast centroid.",
                "where_to_look": "rare_state_summary.csv and tutorial-rare-state.*",
            },
            {
                "use_case": "cohort_triage",
                "plain_question": "If I only care about IPF, should I search inside the whole atlas or only inside IPF cells?",
                "main_takeaway": "The story changes. IPF-only filtering turns the top-20 from mixed disease to all-IPF.",
                "where_to_look": "cohort_triage_summary.csv and tutorial-cohort-triage.*",
            },
            {
                "use_case": "broad_state_search",
                "plain_question": "What if my query is broad and the first result looks weak?",
                "main_takeaway": "Use broad planning. It raised recall from about 0.15 to about 0.63 for the alveolar macrophage query.",
                "where_to_look": "broad_state_tuning_summary.csv and tutorial-broad-state.*",
            },
        ]
    )
    use_cases.to_csv(OUT_DIR / "wetlab_use_cases.csv", index=False)

    easy_top_hits = top_hits_df[
        (top_hits_df["query"] == "IPF myofibroblast centroid")
        & (top_hits_df["method"].isin(["exact", "turboquant-prod-b3"]))
        & (top_hits_df["rank"] <= 10)
    ][["query", "method", "rank", "celltype_name", "Disease", "sample", "score", "item_id"]].copy()
    easy_top_hits.to_csv(OUT_DIR / "myofibroblast_top10.csv", index=False)

    cohort_summary = pd.read_csv(SCENARIO_DIR / "cohort_triage_summary.csv")
    cohort_summary.to_csv(OUT_DIR / "cohort_triage_readout.csv", index=False)

    broad_summary = pd.read_csv(SCENARIO_DIR / "broad_state_tuning_summary.csv")
    broad_summary.to_csv(OUT_DIR / "broad_state_readout.csv", index=False)

    how_to_read = pd.DataFrame(
        [
            {"thing": "top hit table", "plain_meaning": "which cells came back first", "file": "myofibroblast_top10.csv"},
            {"thing": "top-20 IPF fraction", "plain_meaning": "how disease-specific the results look", "file": "cohort_triage_readout.csv"},
            {"thing": "recall@100 vs exact", "plain_meaning": "how similar the method is to exact search", "file": "rare_state_summary.csv / broad_state_readout.csv"},
            {"thing": "candidate memory", "plain_meaning": "how much memory the compressed search layer needs", "file": "rare_state_summary.csv"},
        ]
    )
    how_to_read.to_csv(OUT_DIR / "how_to_read_outputs.csv", index=False)

    save_plot(rare_df, cohort_df, broad_df)


if __name__ == "__main__":
    main()

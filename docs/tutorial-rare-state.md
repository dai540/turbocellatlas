# Tutorial Article: Rare-State Retrieval

This article reports an executed rare-state retrieval analysis on the public SCimilarity tutorial dataset. The scenario is the `IPF myofibroblast centroid`, which acts as a compact pathological-state query.

## Question

Can TurboQuant preserve the exact neighborhood of a rare and coherent disease-associated cell state while shrinking the candidate layer substantially?

## Data and query

- dataset: `GSE136831_subsample.h5ad`
- embedding space: official SCimilarity encoder
- query: centroid of all `IPF myofibroblast cell` embeddings
- source cells used for the centroid: `458`

## Result figure

![Rare-state retrieval thumbnail](assets/scenario-rare-state.png)

## Result table

The executed summary is written to `artifacts/scenario_articles/rare_state_summary.csv`.

| Method | Recall@100 vs exact | Top-20 overlap | Avg latency (ms) | Candidate memory (MB) |
| --- | ---: | ---: | ---: | ---: |
| `exact` | `1.00` | `1.00` | `15.72` | `24.41` |
| `turboquant-prod-b2` | `1.00` | `1.00` | `50.64` | `1.72` |
| `turboquant-prod-b3` | `1.00` | `1.00` | `47.45` | `2.48` |
| `turboquant-prod-b4` | `1.00` | `1.00` | `47.82` | `3.24` |
| `faiss-pq-m8-nbits8` | `0.30` | `0.05` | `0.52` | `0.51` |
| `hnswlib-cosine` | `1.00` | `1.00` | `0.13` | `31.69` |

## Interpretation

This is the cleanest success case for TurboCell Atlas so far.

- TurboQuant preserved the exact top-100 neighborhood at all tested bit widths.
- The candidate layer shrank from `24.41 MB` to `1.72-3.24 MB`.
- HNSW also preserved exact neighborhoods, but with a larger memory footprint.
- FAISS-PQ remained compact and fast, but lost too much neighborhood fidelity for this use case.

The scientific meaning is straightforward: for a compact and disease-coherent state, compressed candidate generation can still hand exact reranking the right cells.

## Output artifacts

- `artifacts/scenario_articles/rare_state_summary.csv`
- `artifacts/scenario_articles/rare_state_thumbnail.png`
- `docs/assets/scenario-rare-state.png`

## Why this scenario matters

Rare-state retrieval is where TurboQuant has the clearest product value. If this case failed, the method would have little practical justification. Because it succeeds, it gives the project a credible biological foothold.

# Real Data Case Study

This article is the executed end-to-end benchmark for TurboCell Atlas on the public SCimilarity tutorial dataset. Its purpose is not only to report recall and latency, but to show the full chain from input dataframe to final tables and figures.

## Background

Atlas-scale retrieval only matters if researchers can trust what the retrieved neighbors mean. TurboCell Atlas therefore separates two jobs:

1. keep biological meaning in a high-quality embedding space such as SCimilarity
2. compress only the candidate-generation layer, then rerank exactly in the original embedding space

The benchmark asks whether that design can preserve biologically meaningful neighborhoods while reducing candidate-layer memory.

## Objective

We evaluated two centroid queries with different difficulty profiles:

1. `IPF myofibroblast centroid`, a relatively compact and rare pathological-state query
2. `IPF alveolar macrophage centroid`, a broader and more heterogeneous query

The goal was to measure what TurboQuant preserves, where it fails, and how those results compare with exact search, HNSW, and FAISS-PQ.

## Input

### Dataset

- dataset: `GSE136831_subsample.h5ad`
- source: public SCimilarity tutorial materials
- shape: `50,000` cells x `44,942` genes
- diseases: `IPF`, `healthy`, `COPD`

### Input dataframe

The executed run writes a field-level dictionary to `artifacts/real_data_case_study/input_data_dictionary.csv`.

Key fields used by the method are:

| Field | Table | Role |
| --- | --- | --- |
| `celltype_name` | `obs` | query construction and hit interpretation |
| `Disease` | `obs` | query construction and disease enrichment summary |
| `sample` | `obs` | sample-level metadata context |
| `study` | `obs` | study provenance |
| `cell_id` | derived `obs` column | stable output identifier |
| `query_group` | derived `obs` column | group label for query provenance |
| `X` | AnnData matrix | SCimilarity-preprocessed expression matrix |
| `embedding` | derived matrix | `128`-dimensional retrieval representation |

The important point is that the method does not begin from a vague tensor. It begins from a concrete AnnData object with `obs` metadata and a counts-derived expression matrix that can be audited field by field.

## Process

### Workflow

```text
GSE136831_subsample.h5ad
  -> obs metadata summary + counts-derived matrix
  -> SCimilarity gene alignment
  -> per-10k normalization + log1p
  -> SCimilarity encoder embeddings
  -> L2 normalization
  -> centroid query construction
  -> exact / HNSW / FAISS-PQ / TurboQuant candidate search
  -> exact reranking for TurboQuant candidates
  -> benchmark tables, figures, logs, and notebooks
```

The executed stage summary is written to `artifacts/real_data_case_study/pipeline_stages.csv`.

### Stage-by-stage process

| Stage | Name | Output | Display artifact |
| --- | --- | --- | --- |
| 1 | `load_input_h5ad` | AnnData with counts-derived matrix and `obs` metadata | input dataset summary |
| 2 | `align_to_scimilarity_gene_order` | gene order aligned to SCimilarity | pipeline stage table |
| 3 | `scimilarity_preprocess` | per-10k `log1p` matrix | methods section and notebook |
| 4 | `embed_cells` | `50,000 x 128` embedding matrix | embedding summary table |
| 5 | `construct_queries` | centroid query vectors | query definition table |
| 6 | `candidate_generation` | method-specific candidate pool | candidate vs rerank table |
| 7 | `exact_rerank_or_baseline_return` | ranked top hits | top hits table |
| 8 | `reporting` | CSV, JSON, JSONL, PNG, Markdown, notebooks | artifact index |

### Query construction

The executed query provenance is written to `artifacts/real_data_case_study/query_definitions.csv`.

| Query | Disease | Cell type | Source cells | Query mode |
| --- | --- | --- | ---: | --- |
| `IPF myofibroblast centroid` | `IPF` | `myofibroblast cell` | `458` | `focused` |
| `IPF alveolar macrophage centroid` | `IPF` | `alveolar macrophage` | `4,389` | `broad` |

`focused` mode keeps the original TurboQuant search budget. `broad` mode increases `candidate_k` and `oversample` within configured caps because heterogeneous neighborhoods are harder to preserve.

### Candidate generation versus exact rerank

The executed comparison is written to `artifacts/real_data_case_study/candidate_rerank_comparison.csv`.

For TurboQuant, the workflow is:

1. approximate similarities in compressed space
2. keep a candidate pool
3. rerank those candidates exactly in the full SCimilarity embedding space

Observed candidate behavior:

| Query | Method | Query mode | Candidate count | Recall@100 vs exact | Top-20 overlap |
| --- | --- | --- | ---: | ---: | ---: |
| `IPF myofibroblast centroid` | `turboquant-prod-b2` | `focused` | `2048` | `1.00` | `1.00` |
| `IPF myofibroblast centroid` | `turboquant-prod-b3` | `focused` | `2048` | `1.00` | `1.00` |
| `IPF myofibroblast centroid` | `turboquant-prod-b4` | `focused` | `2048` | `1.00` | `1.00` |
| `IPF alveolar macrophage centroid` | `turboquant-prod-b2` | `broad` | `8192` | `0.62` | `0.70` |
| `IPF alveolar macrophage centroid` | `turboquant-prod-b3` | `broad` | `8192` | `0.63` | `0.60` |
| `IPF alveolar macrophage centroid` | `turboquant-prod-b4` | `broad` | `8192` | `0.58` | `0.65` |

This table is important because it shows that failure or success is not hidden inside one final score. We can see how large the candidate pool was, which query policy was used, and how much exact reranking was able to recover.

## Output

### Final benchmark figure

![Real-data benchmark summary](assets/real-data-benchmark-summary.png)

### Final benchmark table

The executed summary is written to `artifacts/real_data_case_study/benchmark_summary.csv`.

| Query | Method | Recall@100 vs exact | Avg latency (ms) | Candidate memory (MB) |
| --- | --- | ---: | ---: | ---: |
| `IPF myofibroblast centroid` | `exact` | `1.00` | `11.98` | `24.41` |
| `IPF myofibroblast centroid` | `turboquant-prod-b2` | `1.00` | `53.71` | `1.72` |
| `IPF myofibroblast centroid` | `turboquant-prod-b3` | `1.00` | `47.34` | `2.48` |
| `IPF myofibroblast centroid` | `turboquant-prod-b4` | `1.00` | `45.35` | `3.24` |
| `IPF myofibroblast centroid` | `faiss-pq-m8-nbits8` | `0.30` | `0.17` | `0.51` |
| `IPF myofibroblast centroid` | `hnswlib-cosine` | `1.00` | `0.12` | `31.69` |
| `IPF alveolar macrophage centroid` | `exact` | `1.00` | `10.46` | `24.41` |
| `IPF alveolar macrophage centroid` | `turboquant-prod-b2` | `0.62` | `47.51` | `1.72` |
| `IPF alveolar macrophage centroid` | `turboquant-prod-b3` | `0.63` | `59.07` | `2.48` |
| `IPF alveolar macrophage centroid` | `turboquant-prod-b4` | `0.58` | `55.03` | `3.24` |
| `IPF alveolar macrophage centroid` | `faiss-pq-m8-nbits8` | `0.03` | `0.27` | `0.51` |
| `IPF alveolar macrophage centroid` | `hnswlib-cosine` | `1.00` | `0.35` | `31.69` |

### Ranked output table

The ranked retrieval output is written to `artifacts/real_data_case_study/top_hits.csv`. That file is the concrete answer table for the method: for each query and retrieval backend, it records the returned cells, scores, rank positions, cell types, and diseases.

### Artifact index

The executed artifact catalog is written to `artifacts/real_data_case_study/artifact_index.csv`.

| Artifact | Type | Purpose |
| --- | --- | --- |
| `input_data_dictionary.csv` | table | input traceability |
| `pipeline_stages.csv` | table | process traceability |
| `query_definitions.csv` | table | query provenance |
| `candidate_rerank_comparison.csv` | table | candidate and rerank traceability |
| `benchmark_summary.csv` | table | final benchmark comparison |
| `top_hits.csv` | table | returned cells for inspection |
| `benchmark_summary.png` | figure | article figure |
| `benchmark_log.jsonl` | JSONL | structured diagnostics |
| `benchmark_report.md` | Markdown | compact textual report |
| `benchmark_walkthrough.ipynb` | notebook | end-to-end walkthrough |
| `retrieval_demo.ipynb` | notebook | retrieval-centric inspection |

## Results

### What the demo shows

For the compact `IPF myofibroblast` query, TurboQuant preserved the exact top-100 neighborhood across tested bit widths while shrinking the candidate layer from `24.41 MB` to `1.72-3.24 MB`. That is the clearest evidence that the method can work as intended in the real SCimilarity embedding space.

For the broader `IPF alveolar macrophage` query, adaptive planning helped but did not fully close the gap to exact or HNSW. This shows that the method is sensitive to neighborhood geometry and that broad biological states require more careful candidate coverage.

### What the demo does not show yet

The current implementation is still a Python prototype, so TurboQuant is not yet faster than exact search. The demo therefore proves candidate-layer compression and query-dependent behavior more strongly than it proves end-to-end speed advantage.

## Discussion

The most important change in this case study is not only the numbers. It is the fact that the analysis is now auditable from start to finish:

1. the input dataframe is described explicitly
2. the process stages are enumerated
3. the queries are defined from real labeled populations
4. the candidate pool and rerank behavior are visible
5. the final ranked outputs are available as tables and figures

That makes the benchmark useful for scientific review, engineering debugging, and future acceptance work.

## Reproducibility

Executed assets:

- dataset: `artifacts/data/GSE136831_subsample.h5ad`
- SCimilarity encoder files: `artifacts/data/scimilarity_py/scimilarity/`
- analysis script: `scripts/run_real_data_case_study.py`
- notebooks: `notebooks/benchmark_walkthrough.ipynb`, `notebooks/retrieval_demo.ipynb`

The benchmark can be rerun to regenerate every artifact listed above.

## Conclusion

TurboCell Atlas now demonstrates a complete retrieval story rather than only a score sheet. We can show what the input dataframe was, how it moved through the SCimilarity and TurboQuant pipeline, what tables and figures were emitted, and where the method currently succeeds or fails.

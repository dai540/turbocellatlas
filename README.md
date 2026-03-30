# TurboCell Atlas

TurboCell Atlas is a retrieval system for atlas-scale single-cell search. It is built around a simple separation of concerns:

- biological meaning lives in a high-quality embedding space such as SCimilarity
- retrieval efficiency lives in a compressed candidate-generation layer
- final search quality is restored by exact reranking in the original embedding space

That split is the central design decision of the project. Phase 1 is not about replacing the representation model. It is about making large-scale search practical without throwing away the semantics that make the embedding space useful.

## At a glance

- best current use case: rare or coherent disease-state retrieval
- easiest entry point for non-computational users: `docs/wet-lab-guide.*`
- current benchmark dataset: public SCimilarity tutorial lung dataset
- current limitation: TurboQuant is still slower than exact search in this Python prototype

## Quick start for GitHub readers

1. install the package:

```bash
pip install -e .[io,bench,dev]
```

2. download demo assets:

```bash
python scripts/setup_demo_assets.py
```

3. open the easiest documentation entry point:

- `docs/wet-lab-guide.html`
- `notebooks/wet_lab_walkthrough.ipynb`

4. if you want the full executed benchmark, inspect:

- `artifacts/real_data_case_study/`
- `artifacts/scenario_articles/`
- `https://dai540.github.io/turbocellatlas/`

## Why this project exists

Single-cell atlas retrieval becomes expensive quickly:

- storing a large float32 embedding bank is memory hungry
- exact nearest-neighbor search gets slower as the atlas grows
- future atlas updates should not force a full redesign of the search stack

TurboCell Atlas addresses that by inserting TurboQuant into the candidate-search stage and then reranking with full-precision embeddings. The intended result is a better recall-memory-latency tradeoff than exact search alone, while staying honest about quality by always comparing against exact baselines.

## Theory in one page

The package follows the TurboQuant framing at a high level:

1. apply a random orthogonal rotation so information is spread more evenly across coordinates
2. quantize the rotated representation with a scalar codebook
3. for the inner-product-oriented variant, add a residual sign-based correction term
4. use the compressed codes to propose a candidate set
5. rerank those candidates exactly in the original embedding space

The practical meaning is:

- `mse` prioritizes reconstruction quality
- `prod` is better aligned with approximate inner-product search
- reranking is mandatory for the project goal because it preserves biological ranking semantics better than approximate search alone

## Design principles

### 1. Representation and retrieval are separate modules

SCimilarity or another upstream embedding model should be replaceable without rewriting the compressed search layer.

### 2. Approximation is allowed only in candidate generation

The final answer should come from exact reranking on the source embedding bank whenever possible.

### 3. Metadata is part of retrieval

Real atlas search almost always needs filters such as tissue, disease, study, donor, or sample. The pipeline therefore treats filtering as a first-class operation.

### 4. Benchmarks are part of the product

This is not only a package for search. It is also a package for proving that the search is worth using. Exact, HNSW, FAISS-PQ, and TurboQuant+rerank should be comparable under matched conditions.

### 5. Reproducibility is a design requirement

Random seeds, configuration, codebook fitting strategy, and data manifests should be recordable and stable enough for repeated runs.

## Current architecture

The codebase is intentionally small but already split along future-proof boundaries:

- `tca.config`: runtime configuration
- `tca.quantization`: TurboQuant core and exact top-k utility
- `tca.pipeline`: end-to-end index construction, filtering, candidate generation, reranking
- `tca.io`: local embedding and metadata loading
- `tca.benchmarks`: exact, HNSW, and FAISS-PQ benchmark adapters
- `tca.cli`: command-line entry point

The main retrieval path is:

1. load embeddings and metadata
2. fit or initialize the TurboQuant encoder
3. encode the reference bank
4. apply metadata filters to the active subset
5. score compressed candidates
6. exact-rerank the shortlisted cells
7. return ranked items plus machine-readable run metadata

## What is already implemented

- paper-based TurboQuant `mse` and `prod` variants
- exact reranking in the original embedding space
- optional HNSW and FAISS-PQ adapters for comparison
- metadata-aware filtering
- Python API and CLI
- Markdown and static HTML docs
- deterministic smoke tests

## What is not fully implemented yet

- CELLxGENE Census ingestion helpers
- ILD / HLCA case studies beyond the SCimilarity tutorial dataset
- lower-latency TurboQuant execution beyond the current Python prototype

The repository now includes an executed real-data case study on the public SCimilarity tutorial dataset using the official SCimilarity encoder files. It is intentionally honest about the current prototype behavior: candidate-layer compression is already measurable, broad-query quality improved substantially after adaptive search planning, but TurboQuant latency is not yet better than exact search in this Python implementation.

## Input, process, output

The project now ships an explicit traceability bundle for the real-data benchmark. The intended reading order is:

1. inspect the input schema in `artifacts/real_data_case_study/input_data_dictionary.csv`
2. inspect the stage-by-stage process in `artifacts/real_data_case_study/pipeline_stages.csv`
3. inspect query provenance in `artifacts/real_data_case_study/query_definitions.csv`
4. inspect candidate generation versus reranking in `artifacts/real_data_case_study/candidate_rerank_comparison.csv`
5. inspect final ranked outputs and benchmark metrics in `top_hits.csv` and `benchmark_summary.csv`

The workflow is:

```text
AnnData (.h5ad)
  -> obs metadata summary and counts layer
  -> SCimilarity gene alignment
  -> per-10k normalization + log1p
  -> SCimilarity embedding matrix
  -> centroid query construction
  -> candidate generation by exact / HNSW / FAISS-PQ / TurboQuant
  -> exact reranking for TurboQuant candidates
  -> tables, figures, logs, and notebooks
```

That means the repository no longer only reports final benchmark numbers. It also records what the input dataframe contains, what each processing stage emits, and which artifact displays each step.

## Documentation

Longer-form documentation lives in `docs/` in both Markdown and static HTML form:

- `docs/index.md` / `docs/index.html`
- `docs/get-started.md` / `docs/get-started.html`
- `docs/wet-lab-guide.md` / `docs/wet-lab-guide.html`
- `docs/tutorial.md` / `docs/tutorial.html`
- `docs/tutorial-rare-state.md` / `docs/tutorial-rare-state.html`
- `docs/tutorial-single-cell.md` / `docs/tutorial-single-cell.html`
- `docs/tutorial-cohort-triage.md` / `docs/tutorial-cohort-triage.html`
- `docs/tutorial-broad-state.md` / `docs/tutorial-broad-state.html`
- `docs/tutorial-benchmark-review.md` / `docs/tutorial-benchmark-review.html`
- `docs/theory-and-design.md` / `docs/theory-and-design.html`
- `docs/real-data-case-study.md` / `docs/real-data-case-study.html`
- `docs/reference.md` / `docs/reference.html`

Wet-lab starter assets:

- `configs/wetlab_metadata_template.csv`
- `notebooks/wet_lab_walkthrough.ipynb`
- `artifacts/wetlab_examples/`

Project metadata for GitHub release:

- `LICENSE`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `CITATION.cff`
- `.github/workflows/ci.yml`

## Install

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e .[io,bench,dev]
```

Or create a local environment with:

```bash
conda env create -f environment.yml
```

## Quick start

```python
import numpy as np
from tca import SearchIndex, TurboQuantConfig

rng = np.random.default_rng(7)
embeddings = rng.normal(size=(200, 64)).astype(np.float32)
metadata = [{"cell_id": f"cell-{i}", "disease": "ild" if i % 3 == 0 else "control"} for i in range(200)]
query = embeddings[0]

index = SearchIndex.from_embeddings(
    embeddings=embeddings,
    metadata=metadata,
    config=TurboQuantConfig(bit_width=3, candidate_k=40, rerank_k=10, seed=7),
)

results = index.search(query, filters={"disease": "ild"})
print(results.items[0].item_id, results.items[0].score)
```

## CLI

```bash
tca search ^
  --embeddings data/reference.npy ^
  --metadata data/reference.jsonl ^
  --query data/query.npy ^
  --bit-width 3 ^
  --candidate-k 128 ^
  --rerank-k 20 ^
  --output artifacts/results.json
```

## Real-data benchmark snapshot

On the public SCimilarity tutorial dataset (`50,000` cells, `44,942` genes) using the official SCimilarity encoder:

- `TurboQuant prod b2/b3/b4` matched exact retrieval for the `IPF myofibroblast centroid` query at `recall@100 = 1.00`
- the compressed TurboQuant candidate layer shrank from about `24.41 MB` for the float32 bank to about `1.72-3.24 MB`
- adaptive broad-query planning raised `IPF alveolar macrophage centroid` recall from the earlier low range to about `0.58-0.63`
- `hnswlib` also matched exact on both evaluated queries and was very fast, but its index footprint grew to about `31.69 MB`
- `FAISS-PQ` remained extremely compact and fast, but agreed less well with exact on both queries
- for the broader `IPF alveolar macrophage centroid` query, TurboQuant still remained less faithful than HNSW or exact in the current prototype

See `docs/real-data-case-study.*` and `artifacts/real_data_case_study/` for the measured outputs.

## Traceability artifacts

The real-data benchmark now writes the following inspection files:

- `artifacts/real_data_case_study/input_data_dictionary.csv`: field-by-field description of the AnnData input and derived embedding table
- `artifacts/real_data_case_study/pipeline_stages.csv`: stage summary from raw `h5ad` through reporting outputs
- `artifacts/real_data_case_study/query_definitions.csv`: exact query populations used to construct centroid probes
- `artifacts/real_data_case_study/candidate_rerank_comparison.csv`: TurboQuant candidate pool size, rerank behavior, and overlap versus exact
- `artifacts/real_data_case_study/artifact_index.csv`: catalog of every output table, figure, log, and report
- `notebooks/benchmark_walkthrough.ipynb`: end-to-end walkthrough from input tables to final figure
- `notebooks/retrieval_demo.ipynb`: retrieval-focused notebook centered on ranked outputs

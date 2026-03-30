# Reference

This page is the compact API and file-format reference for TurboCell Atlas.

## Package modules

## `tca.config`

### `TurboQuantConfig`

Configuration object for index construction and search.

Key fields:

- `bit_width`: number of bits used by the quantizer
- `candidate_k`: target candidate pool size before reranking
- `rerank_k`: final number of returned hits
- `oversample`: extra approximate candidates before exact rerank
- `seed`: random seed for deterministic construction
- `quantizer_kind`: `"mse"` or `"prod"`
- `monte_carlo_samples`: sample size for scalar codebook fitting

## `tca.quantization`

### `TurboQuantMSE`

Implements the MSE-oriented TurboQuant variant.

Methods:

- `encode(x)`
- `decode(encoded)`

### `TurboQuantProd`

Implements the inner-product-oriented TurboQuant variant with residual sign correction.

Methods:

- `encode(x)`
- `decode(encoded)`
- `approximate_inner_products(query, encoded)`

### `exact_topk(query, bank, top_k, ids=None)`

Small exact baseline utility for reranking or direct evaluation.

## `tca.pipeline`

### `SearchIndex`

Main retrieval object.

Methods:

- `from_embeddings(embeddings, metadata, config=None)`
- `search(query, filters=None)`
- `search_exact(query, filters=None)`
- `to_manifest()`

### Filter semantics

`filters` is a dictionary such as:

```python
{"disease": "fibrosis", "study": ["study-1", "study-2"]}
```

Each key is matched against metadata records before candidate generation.

## `tca.io`

### `load_embeddings(path)`

Supported formats:

- `.npy`
- `.npz` with `embeddings`

### `load_metadata(path)`

Supported formats:

- `.jsonl`
- `.json`
- `.csv`

### `load_h5ad_embeddings(path, embedding_key="X")`

Optional helper for `.h5ad` loading. Requires the `io` extra.

## `tca.scimilarity_support`

### `embed_h5ad_with_scimilarity(h5ad_path, model_path, buffer_size=2048)`

Loads a public or local `.h5ad`, aligns genes to the SCimilarity model space, applies SCimilarity preprocessing, and returns embeddings plus the aligned `AnnData`.

## `tca.benchmarks`

### `ExactBackend`

Exact comparison backend.

### `HNSWBackend`

Optional `hnswlib` backend. Requires the `bench` extra.

### `FaissPQBackend`

Optional `faiss-cpu` product quantization backend. Requires the `bench` extra.

## Documentation pages

- `index`: project overview and rationale
- `get-started`: first-run instructions
- `tutorial`: synthetic mechanics walkthrough
- `theory-and-design`: system rationale and architecture
- `real-data-case-study`: executed SCimilarity tutorial benchmark article
- `reference`: API and file-format summary

## CLI reference

### `tca search`

Required arguments:

- `--embeddings`
- `--metadata`
- `--query`
- `--output`

Common optional arguments:

- `--bit-width`
- `--candidate-k`
- `--rerank-k`
- `--oversample`
- `--seed`
- `--quantizer-kind`
- `--filter key=value`

## Output JSON shape

```json
{
  "manifest": {
    "config": {},
    "n_cells": 200,
    "dimension": 64,
    "quantizer_kind": "prod"
  },
  "results": [
    {
      "rank": 1,
      "item_id": "cell-1",
      "score": 3.14,
      "metadata": {}
    }
  ],
  "backend": "turboquant",
  "candidate_count": 128,
  "filtered_count": 400
}
```

## Current assumptions and limits

- embeddings are treated as dense numeric arrays
- exact reranking assumes original embeddings are available in memory
- direct SCimilarity model execution is not wired yet
- Census ingestion and richer manifests are still future-facing extensions

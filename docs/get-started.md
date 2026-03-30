# Get Started

This page gets TurboCell Atlas running from local embedding files.

## 1. Install

Core install:

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e .[io,bench,dev]
```

- `io`: enables `.h5ad` loading via `anndata`
- `bench`: enables `hnswlib` and `faiss-cpu`
- `dev`: enables `pytest` and packaging tools

## 2. Project layout

Important files:

- `src/tca/quantization.py`: TurboQuant implementation
- `src/tca/pipeline.py`: retrieval pipeline and reranking
- `src/tca/benchmarks.py`: exact, HNSW, and FAISS-PQ adapters
- `src/tca/cli.py`: command-line entry point
- `configs/minimal.json`: example runtime config

## 3. Prepare input files

Minimal CLI input:

- reference embeddings: `.npy` or `.npz`
- reference metadata: `.jsonl`, `.json`, or `.csv`
- query embedding: `.npy`

Example metadata record:

```json
{"cell_id": "cell-0001", "study": "ILD-demo", "disease": "fibrosis", "tissue": "lung"}
```

If you want the easiest starting point for your own metadata table, use:

- `configs/wetlab_metadata_template.csv`

If you want the easiest notebook-style entry point, open:

- `notebooks/wet_lab_walkthrough.ipynb`

## 4. Run your first search

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

Filter to a subset:

```bash
tca search ^
  --embeddings data/reference.npy ^
  --metadata data/reference.jsonl ^
  --query data/query.npy ^
  --filter disease=fibrosis ^
  --filter tissue=lung ^
  --output artifacts/results.json
```

## 5. Use the Python API

```python
import numpy as np
from tca import SearchIndex, TurboQuantConfig

embeddings = np.load("data/reference.npy").astype(np.float32)
query = np.load("data/query.npy").astype(np.float32)[0]
metadata = [
    {"cell_id": "cell-0", "disease": "fibrosis"},
    {"cell_id": "cell-1", "disease": "control"},
]

index = SearchIndex.from_embeddings(
    embeddings=embeddings,
    metadata=metadata,
    config=TurboQuantConfig(
        bit_width=3,
        candidate_k=128,
        rerank_k=20,
        quantizer_kind="prod",
        seed=7,
    ),
)

results = index.search(query, filters={"disease": "fibrosis"})
for item in results.items[:5]:
    print(item.rank, item.item_id, item.score)
```

## 6. Read the output

The CLI writes JSON with:

- manifest
- selected backend
- candidate and filtered counts
- ranked results with metadata

That output is designed to be easy to feed into later reporting or notebook layers.

## 7. Wet-lab shortcut

If you are not primarily a computational user, the simplest route is:

1. read [Wet Lab Guide](wet-lab-guide.md)
2. copy the metadata shape from `configs/wetlab_metadata_template.csv`
3. open `notebooks/wet_lab_walkthrough.ipynb`
4. compare your first result against the example outputs in `artifacts/wetlab_examples/`

# TurboCell Atlas

<img src="docs/assets/tca-icon.svg" alt="TurboCell Atlas icon" width="80" />

[![Docs](https://img.shields.io/badge/docs-github.io-0f6c63)](https://dai540.github.io/turbocellatlas/)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)
![License](https://img.shields.io/badge/license-MIT-0f172a)

TurboCell Atlas is a minimal Python package for atlas-scale cell-state retrieval. This repository has been reduced to the smallest defensible form: a compact package, a small test suite, and a Sphinx site. Heavy benchmark artifacts, downloaded datasets, notebooks, and generated caches are intentionally excluded.

## Design goals

The repository is built around four constraints.

1. Keep the package small.
2. Keep the dependency set small.
3. Keep the documentation explicit and structured.
4. Avoid shipping large bundled data or generated outputs.

The current implementation therefore focuses on one core capability: exact cosine search over a dense embedding matrix with optional exact-match metadata filters.

## What is included

- a minimal installable package under `src/turbocellatlas`
- a small CLI for running exact search on `.npy` embeddings
- a compact test suite under `tests`
- a Sphinx site under `docs`
- GitHub Actions for tests and documentation deployment

## What is intentionally excluded

- large benchmark artifacts
- downloaded demo datasets
- notebooks
- one-off scripts used only during development
- approximate-search backends with heavy compiled dependencies
- temporary files, `.tar.gz` outputs, and generated caches

This is deliberate. The repository is meant to remain small enough to inspect and install quickly.

## Installation

Install the package:

```bash
pip install -e .
```

Install development and documentation dependencies:

```bash
pip install -r requirements-dev.txt
```

## Core usage

The package exposes one primary object: `SearchIndex`.

```python
import numpy as np

from turbocellatlas import SearchConfig, SearchIndex

embeddings = np.array(
    [
        [1.0, 0.0],
        [0.9, 0.1],
        [0.0, 1.0],
    ],
    dtype=np.float32,
)

metadata = [
    {"cell_id": "cell-a", "disease": "IPF"},
    {"cell_id": "cell-b", "disease": "IPF"},
    {"cell_id": "cell-c", "disease": "Control"},
]

index = SearchIndex(embeddings, metadata, SearchConfig(top_k=2))
results = index.search(np.array([1.0, 0.0], dtype=np.float32), filters={"disease": "IPF"})
```

Each result contains:

- `rank`
- `item_id`
- `score`
- `metadata`

## Command-line usage

The CLI accepts `.npy` embeddings and query vectors. Metadata is optional and can be supplied as JSONL.

```bash
tca search \
  --embeddings embeddings.npy \
  --query query.npy \
  --metadata metadata.jsonl \
  --top-k 5 \
  --output results.json
```

## Repository layout

```text
turbocellatlas/
├── .github/workflows/
├── docs/
├── src/turbocellatlas/
├── tests/
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements-dev.txt
```

## Documentation

The documentation is built with Sphinx and organized into four top-level sections.

- Getting Started
- Guides
- Tutorials
- Reference

The published site is available at [https://dai540.github.io/turbocellatlas/](https://dai540.github.io/turbocellatlas/).

Build the docs locally:

```bash
sphinx-build -b html docs docs/_build/html
```

## Scope and limitations

This package is now intentionally narrow.

- It performs exact search only.
- It does not bundle or download heavy datasets.
- It does not include benchmark pipelines or tutorial notebooks.
- It expects dense embedding matrices that already exist.

That tradeoff is intentional. The repository now prioritizes a small footprint, clarity, and maintainability over breadth.

## Development checks

Run tests:

```bash
pytest
```

Build docs:

```bash
sphinx-build -W -b html docs docs/_build/html
```

## Metadata

- Author: Dai
- License: MIT
- Repository: [https://github.com/dai540/turbocellatlas](https://github.com/dai540/turbocellatlas)
- Documentation: [https://dai540.github.io/turbocellatlas/](https://dai540.github.io/turbocellatlas/)

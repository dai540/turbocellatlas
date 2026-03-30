# TurboCell Atlas

<img src="docs/assets/tca-icon.svg" alt="TurboCell Atlas icon" width="92" />

[![Docs](https://img.shields.io/badge/docs-github.io-0f6c63)](https://dai540.github.io/turbocellatlas/)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)
![License](https://img.shields.io/badge/license-MIT-0f172a)
![Status](https://img.shields.io/badge/status-alpha-b65a2a)

TurboCell Atlas is a Python package for atlas-scale single-cell retrieval. It combines compressed candidate generation with exact reranking in the original embedding space, with an emphasis on reproducible benchmark artifacts and documentation that can be read by both computational and wet-lab collaborators.

- Read the docs: [https://dai540.github.io/turbocellatlas/](https://dai540.github.io/turbocellatlas/)
- Browse tutorials: [Tutorials](docs/tutorial.md)
- Start from the easiest path: [Wet Lab Guide](docs/wet-lab-guide.md)
- Inspect executed benchmarks: [Benchmarks](docs/benchmarks.md)

## Install

Install from a local clone:

```bash
pip install -e .[io,bench,dev]
```

Or create a local environment:

```bash
conda env create -f environment.yml
```

## Get started

Download the public demo assets used by the documentation:

```bash
python scripts/setup_demo_assets.py
```

Then inspect:

- `configs/wetlab_metadata_template.csv`
- `notebooks/wet_lab_walkthrough.ipynb`
- `artifacts/wetlab_examples/`

## What this package is for

TurboCell Atlas is designed for questions like these:

- given one cell state, what similar cells exist in a large atlas
- how much memory can be saved in candidate search without changing the final biological ranking too much
- when should retrieval be restricted by disease, tissue, study, or sample

## Public API

The intended public package surface is small:

- `tca.pipeline.SearchIndex`
- `tca.config.TurboQuantConfig`
- `tca.quantization.TurboQuantMSE`
- `tca.quantization.TurboQuantProd`
- `tca.cli`

The project does not promise stability for undocumented internal details.

## Current highlights

- `IPF myofibroblast centroid`: TurboQuant matched exact at `recall@100 = 1.00`
- `single IPF myofibroblast cell`: TurboQuant matched exact in the executed example
- `IPF alveolar macrophage centroid`: broader planning substantially improved recall, but did not reach exact

## Current limitation

TurboQuant remains slower than exact search in this Python prototype. The package is therefore best understood as a strong research and benchmarking prototype rather than a fully optimized production retrieval engine.

## Documentation map

- [Home](docs/index.md)
- [Tutorials](docs/tutorial.md)
- [Guides](docs/guides.md)
- [API](docs/api.md)
- [Benchmarks](docs/benchmarks.md)
- [Contributing](docs/contributing.md)
- [Release notes](docs/release-notes.md)
- [References](docs/references.md)

## Project metadata

- `LICENSE`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `.github/workflows/ci.yml`
- `.github/workflows/pages.yml`

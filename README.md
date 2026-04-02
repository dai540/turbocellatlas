# TurboCell Atlas

<img src="docs/assets/tca-icon.svg" alt="TurboCell Atlas icon" width="92" />

[![Docs](https://img.shields.io/badge/docs-github.io-0f6c63)](https://dai540.github.io/turbocellatlas/)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)
![License](https://img.shields.io/badge/license-MIT-0f172a)
![Status](https://img.shields.io/badge/status-alpha-b65a2a)

TurboCell Atlas is a Python package for atlas-scale single-cell retrieval. It combines compressed candidate generation with exact reranking in the original embedding space, with an emphasis on reproducible benchmark artifacts and Sphinx documentation that can be read by both computational and wet-lab collaborators.

- Read the docs: [https://dai540.github.io/turbocellatlas/](https://dai540.github.io/turbocellatlas/)
- Browse tutorials: [Tutorials](https://dai540.github.io/turbocellatlas/tutorials/index.html)
- Start with the simplest questions: [What TurboCell Atlas Can Do](https://dai540.github.io/turbocellatlas/guides/what-can-do.html)
- Check your prerequisites: [What You Need](https://dai540.github.io/turbocellatlas/guides/what-you-need.html)
- Start from the easiest path: [Wet-lab Guide](https://dai540.github.io/turbocellatlas/tutorials/wet-lab-guide.html)
- Inspect executed benchmarks: [Benchmarks](https://dai540.github.io/turbocellatlas/benchmarks.html)

## Install

Install from a local clone:

```bash
pip install -e .[io,bench,dev,docs]
```

Or create a local environment:

```bash
conda env create -f environment.yml
```

## Documentation structure

The Sphinx site is organized like a package documentation site:

- `Home`
- `Tutorials`
- `Guides`
- `API reference`
- `Benchmarks`
- `Contributing`
- `Release notes`
- `References`

If you want the plain-language explanation first, read:

- [What TurboCell Atlas Can Do](https://dai540.github.io/turbocellatlas/guides/what-can-do.html)
- [What You Need Before Using TurboCell Atlas](https://dai540.github.io/turbocellatlas/guides/what-you-need.html)

## Build the docs

Build the Sphinx site locally:

```bash
sphinx-build -b html docs docs/_build/html
```

## Get started with data

Download the public demo assets used by the tutorials:

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

- [Home](https://dai540.github.io/turbocellatlas/)
- [Tutorials](https://dai540.github.io/turbocellatlas/tutorials/index.html)
- [Guides](https://dai540.github.io/turbocellatlas/guides/index.html)
- [API](https://dai540.github.io/turbocellatlas/api/index.html)
- [Benchmarks](https://dai540.github.io/turbocellatlas/benchmarks.html)
- [Contributing](https://dai540.github.io/turbocellatlas/contributing.html)
- [Release notes](https://dai540.github.io/turbocellatlas/release-notes.html)
- [References](https://dai540.github.io/turbocellatlas/references.html)

## Project metadata

- `LICENSE`
- `CITATION.cff`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `.github/workflows/ci.yml`
- `.github/workflows/pages.yml`

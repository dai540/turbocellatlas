# Contributing

## Scope

TurboCell Atlas is currently an open research prototype with strong emphasis on:

- reproducible retrieval benchmarks
- understandable documentation for non-specialist users
- honest reporting of current limitations

## Development setup

1. Create an environment from `environment.yml`, or install the package with:
   - `pip install -e .[io,bench,dev]`
2. Run tests:
   - `pytest`
3. If you change docs or example analyses, rerun the relevant scripts in `scripts/`.

## Preferred contribution types

- bug fixes in retrieval logic or docs
- reproducibility improvements
- new benchmark scenarios with clear provenance
- wet-lab-friendly explanations and notebooks

## Ground rules

- do not replace exact reranking with approximate final ranking without explicit discussion
- keep benchmark claims tied to generated artifacts
- document any new dataset or model dependency clearly
- prefer small, reviewable pull requests

## Before opening a pull request

- run `pytest`
- update docs if behavior changed
- mention whether new data or large artifacts are required to reproduce the change

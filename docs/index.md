# TurboCell Atlas

TurboCell Atlas is a Python package for atlas-scale single-cell retrieval. It combines compressed candidate generation with exact reranking in the original embedding space.

## Site map

- [Tutorials](tutorial.md): practical entry points for first runs and worked examples
- [Guides](guides.md): how to think about data, queries, reports, and interpretation
- [API](api.md): package surface area, classes, and CLI
- [Benchmarks](benchmarks.md): executed case studies and measured scenario articles
- [Contributing](contributing.md): how to contribute safely to the project
- [Release Notes](release-notes.md): project change history
- [References](references.md): citations, dataset provenance, and external links

## Quick links

- [Get Started](get-started.md)
- [Wet Lab Guide](wet-lab-guide.md)
- [Rare-State Retrieval](tutorial-rare-state.md)
- [Single-Cell Query](tutorial-single-cell.md)
- [Real Data Case Study](real-data-case-study.md)

## What this package is for

TurboCell Atlas is designed for questions like these:

- given one cell state, what similar cells exist in a large atlas
- how much memory can be saved in candidate search without losing the final biological ranking
- when should retrieval be restricted by disease, tissue, study, or sample

## Current status

- best current success case: rare or coherent disease-state retrieval
- strongest executed benchmark: `IPF myofibroblast centroid` in the SCimilarity tutorial dataset
- main current limitation: TurboQuant is still slower than exact search in this Python prototype

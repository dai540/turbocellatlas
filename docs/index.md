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

- [What TurboCell Atlas Can Do](what-turbocellatlas-can-do.md)
- [What You Need](what-you-need.md)
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

## If you are new here

The best reading order is:

1. [What TurboCell Atlas Can Do](what-turbocellatlas-can-do.md)
2. [What You Need Before Using It](what-you-need.md)
3. [Wet Lab Guide](wet-lab-guide.md) or [Get Started](get-started.md)
4. one scenario article from [Tutorials](tutorial.md)

## Current status

- best current success case: rare or coherent disease-state retrieval
- strongest executed benchmark: `IPF myofibroblast centroid` in the SCimilarity tutorial dataset
- main current limitation: TurboQuant is still slower than exact search in this Python prototype

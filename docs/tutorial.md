# Tutorials

TurboCell Atlas is easier to understand when the documentation follows real usage patterns instead of one generic walkthrough. This page is now the hub for scenario-based tutorial articles, each backed by an executed analysis.

## Tutorial map

| Scenario | What it shows | Best next step |
| --- | --- | --- |
| [Rare-State Retrieval](tutorial-rare-state.md) | executed benchmark for `IPF myofibroblast centroid` showing perfect TurboQuant recall with compressed memory | compare with the real-data case study |
| [Single-Cell Query](tutorial-single-cell.md) | executed example showing that one `IPF myofibroblast cell` can already recover a coherent neighborhood | move from one cell to centroid refinement |
| [Cohort Triage with Metadata Filters](tutorial-cohort-triage.md) | executed cohort filter analysis showing how the top-20 disease mix changes under `IPF` restriction | move to cohort review workflows |
| [Broad-State Tuning](tutorial-broad-state.md) | executed tuning study comparing `focused` and `broad` planning on `IPF alveolar macrophage centroid` | tune broad centroids before reporting |
| [Acceptance-Style Benchmark Review](tutorial-benchmark-review.md) | how to read the benchmark artifacts as an engineering or scientific reviewer | convert outputs into a report or gate |

## How to use this section

The recommended order is:

1. start with [Wet Lab Guide](wet-lab-guide.md) if you want the easiest plain-language overview
2. or start with [Get Started](get-started.md) if you want to run the package immediately
3. read one scenario tutorial that matches your immediate question
4. move to [Real Data Case Study](real-data-case-study.md) once you need the full executed benchmark
5. use [Reference](reference.md) when you need CLI or API details

## Why multiple tutorials

TurboCell Atlas serves different jobs:

- finding rare pathological neighbors
- limiting retrieval to a biologically relevant cohort
- diagnosing why a broad query underperforms
- reviewing whether a benchmark artifact bundle is convincing

One tutorial cannot teach those equally well. Splitting them by scenario makes the intended workflows easier to understand and reuse.

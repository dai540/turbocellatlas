# TurboCell Atlas

TurboCell Atlas documentation is now organized by workflow rather than by one linear narrative. The goal is to help readers move quickly from first execution to scenario-specific usage and then to executed benchmark review.

## Start here

- [Get Started](get-started.md): install the package and run the first search
- [Wet Lab Guide](wet-lab-guide.md): the easiest explanation of inputs, outputs, and how to read the results
- [Tutorials](tutorial.md): scenario-based articles for different usage patterns
- [Theory and Design](theory-and-design.md): algorithmic rationale and architecture
- [Real Data Case Study](real-data-case-study.md): executed benchmark with explicit input, process, and output traceability
- [Reference](reference.md): module, CLI, and API details

## Tutorial scenarios

- [Rare-State Retrieval](tutorial-rare-state.md): compact pathological-state queries where TurboQuant is most likely to preserve exact neighborhoods
- [Cohort Triage with Metadata Filters](tutorial-cohort-triage.md): disease, tissue, study, or sample-restricted retrieval
- [Broad-State Tuning](tutorial-broad-state.md): tuning candidate coverage for heterogeneous neighborhoods
- [Acceptance-Style Benchmark Review](tutorial-benchmark-review.md): reading the artifact bundle as an engineering or scientific reviewer

## Core idea

The project is built on a stable contract:

1. keep biological meaning in a high-quality embedding space such as SCimilarity
2. compress only the candidate-generation layer with TurboQuant
3. recover final ranking quality with exact reranking in the original embedding space

That makes TurboCell Atlas a retrieval layer rather than a replacement for the embedding model.

## Input to output traceability

The executed benchmark now exposes the full chain:

- input schema: `artifacts/real_data_case_study/input_data_dictionary.csv`
- process stages: `artifacts/real_data_case_study/pipeline_stages.csv`
- query provenance: `artifacts/real_data_case_study/query_definitions.csv`
- candidate versus rerank behavior: `artifacts/real_data_case_study/candidate_rerank_comparison.csv`
- final outputs: `artifacts/real_data_case_study/top_hits.csv`, `benchmark_summary.csv`, `benchmark_summary.png`

This means the site now shows not only final numbers, but also what input dataframe was used, what transformations happened, and which artifacts display the outputs.

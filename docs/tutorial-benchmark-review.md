# Tutorial: Acceptance-Style Benchmark Review

## Scenario

You are not only running retrieval. You are reviewing whether the resulting artifact bundle is convincing enough for engineering acceptance, scientific communication, or milestone reporting.

## Review order

1. inspect `input_data_dictionary.csv`
2. inspect `pipeline_stages.csv`
3. inspect `query_definitions.csv`
4. inspect `candidate_rerank_comparison.csv`
5. inspect `benchmark_summary.csv`
6. inspect `top_hits.csv` and `benchmark_summary.png`

## What each artifact answers

| Artifact | Question it answers |
| --- | --- |
| `input_data_dictionary.csv` | what exactly was in the input dataframe |
| `pipeline_stages.csv` | what transformations were applied |
| `query_definitions.csv` | what biological populations defined the queries |
| `candidate_rerank_comparison.csv` | how candidate generation differed from final reranking |
| `benchmark_summary.csv` | what tradeoff each backend achieved |
| `top_hits.csv` | what cells were actually returned |
| `artifact_index.csv` | what else exists and why |

## What a convincing bundle looks like

- inputs are named and interpretable
- processing stages are explicit
- query provenance is reproducible
- candidate diagnostics are visible
- final outputs are tables and figures, not only prose

## What a weak bundle looks like

- only a final score table exists
- no one can tell what metadata drove query construction
- candidate generation and rerank behavior are hidden
- outputs cannot be traced back to a concrete input schema

## Next step

Use this review pattern whenever TurboCell Atlas outputs need to leave the development context and be read by other scientists, engineers, or stakeholders.

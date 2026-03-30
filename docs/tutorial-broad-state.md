# Tutorial Article: Broad-State Tuning

This article reports an executed broad-state tuning analysis on the public SCimilarity tutorial dataset. The scenario again uses the `IPF alveolar macrophage centroid`, but this time the focus is on how query planning changes TurboQuant behavior.

## Question

How much does `broad` query planning improve TurboQuant on a heterogeneous neighborhood compared with `focused` planning?

## Result figure

![Broad-state tuning thumbnail](assets/scenario-broad-state.png)

## Result table

The executed summary is written to `artifacts/scenario_articles/broad_state_tuning_summary.csv`.

| Method | Query mode | Candidate count | Recall@100 vs exact | Top-20 overlap | Avg latency (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| `turboquant-prod-b2` | `focused` | `2,048` | `0.14` | `0.20` | `53.70` |
| `turboquant-prod-b3` | `focused` | `2,048` | `0.15` | `0.10` | `61.78` |
| `turboquant-prod-b4` | `focused` | `2,048` | `0.15` | `0.10` | `59.73` |
| `turboquant-prod-b2` | `broad` | `8,192` | `0.62` | `0.70` | `53.44` |
| `turboquant-prod-b3` | `broad` | `8,192` | `0.63` | `0.60` | `52.72` |
| `turboquant-prod-b4` | `broad` | `8,192` | `0.58` | `0.65` | `47.61` |

## Interpretation

This scenario is important because it shows that broad-query failure is not binary. The method changes a lot once the candidate budget is allowed to grow.

- `focused` mode was clearly under-provisioned for this query.
- `broad` mode increased the candidate pool from `2,048` to `8,192`.
- That change lifted recall from roughly `0.14-0.15` to `0.58-0.63`.
- The best measured setting here was `turboquant-prod-b3` in `broad` mode.

The lesson is that heterogeneous neighborhoods should not be judged with the same candidate policy as compact rare states.

## Output artifacts

- `artifacts/scenario_articles/broad_state_tuning_summary.csv`
- `artifacts/scenario_articles/broad_state_thumbnail.png`
- `docs/assets/scenario-broad-state.png`

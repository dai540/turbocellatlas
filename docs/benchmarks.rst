Benchmarks
==========

TurboCell Atlas ships with executed benchmark artifacts because the central question is not only whether the code runs, but whether the retrieval behavior stays biologically interpretable after compression and filtering.

What the benchmark bundle contains
----------------------------------

The executed benchmark bundle under ``artifacts/real_data_case_study/`` includes:

* summary tables for recall, memory, and latency
* a machine-readable JSON summary
* a JSONL log for traceability
* top-hit tables
* plots that can be reused in articles or internal reviews

How to read the benchmark output
--------------------------------

There are three questions to ask in order.

1. Does the compressed method preserve the final neighborhood well enough for the biological question at hand?
2. How much memory is saved in the candidate layer?
3. Does the latency tradeoff justify the approximation in the current implementation?

In the current project state, the strongest positive result is still the rare-state IPF myofibroblast example. The broad-state examples are valuable because they show where compression becomes harder to trust without more careful planning and reranking.

Related reading
---------------

* :doc:`tutorials/benchmark-review`
* :doc:`guides/real-data-case-study`

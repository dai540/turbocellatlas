Theory and design
=================

Why the retrieval stack is split
--------------------------------

TurboCell Atlas separates the retrieval problem into two layers:

* an embedding layer that tries to preserve biologically meaningful neighborhood structure
* a candidate-generation layer that tries to reduce memory and search cost before exact reranking

This split is important because it keeps the final biological ranking anchored in the original embedding space even when a compressed method is used to narrow the candidate set.

Why exact reranking matters
---------------------------

If a compressed method were allowed to define the final biological answer by itself, interpretation would become much harder. Exact reranking keeps the final top-k result connected to the original representation, which makes the method easier to benchmark and easier to discuss with collaborators.

Why multiple scenarios matter
-----------------------------

The package is intentionally documented with multiple scenarios because retrieval quality is not uniform across all biological questions. Rare and coherent states behave differently from broad and heterogeneous states. A design that looks strong in one setting may still need caution in another.

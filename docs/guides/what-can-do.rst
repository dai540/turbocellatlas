What TurboCell Atlas can do
===========================

This page answers the simplest practical question: what is TurboCell Atlas actually useful for?

In plain language
-----------------

TurboCell Atlas helps you start from one cell state that you care about and retrieve similar cells from a large atlas. The result is not only a ranked list of cells. The result is a small set of artifacts that help you interpret whether the answer makes biological sense.

What it can already do well
---------------------------

Find cells similar to a rare or coherent disease state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the strongest current use case. In the executed ``IPF myofibroblast centroid`` example, TurboQuant preserved the exact top-100 neighborhood while using much less candidate-layer memory than the original float32 embedding bank.

Start from one interesting cell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You do not always need to begin with a curated centroid. In the executed single-cell example, one ``IPF myofibroblast`` cell was already enough to recover a coherent local neighborhood.

Restrict retrieval to a biologically relevant cohort
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many biological questions are not really "search the whole atlas" questions. They are "search the atlas, but only inside IPF, only inside lung, or only inside one study" questions. TurboCell Atlas can apply metadata filters before ranking cells.

Compare retrieval settings and methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project includes exact search, HNSW, FAISS-PQ, and TurboQuant-based retrieval paths, together with executed benchmark artifacts.

What it cannot yet do perfectly
-------------------------------

TurboCell Atlas is still a research prototype.

* TurboQuant is not yet faster than exact search in this Python implementation.
* Broad and heterogeneous queries are still harder than compact rare states.
* The strongest executed dataset is still the public SCimilarity tutorial dataset.

Good first use cases
--------------------

* retrieving neighbors for a rare pathological fibroblast-like state
* starting from one representative cell and inspecting its neighborhood
* comparing whole-atlas retrieval with disease-restricted retrieval
* generating a benchmark artifact bundle for discussion with collaborators

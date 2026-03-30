# What TurboCell Atlas Can Do

This page answers the simplest practical question: what is TurboCell Atlas actually useful for?

## In plain language

TurboCell Atlas helps you start from one cell state that you care about and retrieve similar cells from a large atlas. The result is not only a ranked list of cells. The result is a small set of artifacts that help you interpret whether the answer makes biological sense.

## What it can already do well

### 1. Find cells similar to a rare or coherent disease state

This is the strongest current use case. In the executed `IPF myofibroblast centroid` example, TurboQuant preserved the exact top-100 neighborhood while using much less candidate-layer memory than the original float32 embedding bank.

That means the package is already useful when:

- the target state is compact
- the biology is relatively coherent
- you want to compare compressed retrieval with exact retrieval

### 2. Start from one interesting cell

You do not always need to begin with a curated centroid. In the executed single-cell example, one `IPF myofibroblast cell` was already enough to recover a coherent local neighborhood.

This is useful when:

- you have a small pilot dataset
- you only trust a few cells
- you want to quickly inspect what state a cell appears close to

### 3. Restrict retrieval to a biologically relevant cohort

TurboCell Atlas can apply metadata filters before ranking cells. That matters because many biological questions are not really "search the whole atlas" questions. They are "search the atlas, but only inside `IPF`, only inside lung, or only inside one study" questions.

This is useful when:

- disease context matters
- tissue context matters
- you want to avoid mixing biologically incompatible cohorts

### 4. Compare retrieval settings and methods

The project includes exact search, HNSW, FAISS-PQ, and TurboQuant-based retrieval paths, with executed benchmark artifacts.

This is useful when:

- you want to know whether compression changes the biological answer
- you want to compare memory, latency, and ranking agreement
- you are preparing a report for collaborators

## What it cannot yet do perfectly

TurboCell Atlas is still a research prototype.

- TurboQuant is not yet faster than exact search in this Python implementation.
- Broad and heterogeneous queries are still harder than compact rare states.
- The strongest executed dataset is still the public SCimilarity tutorial dataset.

## Good first use cases

If you are wondering whether the package is relevant to your work, these are the best starting points:

1. retrieve neighbors for a rare pathological fibroblast-like state
2. start from one representative cell and inspect its neighborhood
3. compare whole-atlas retrieval with disease-restricted retrieval
4. generate a benchmark artifact bundle for discussion with collaborators

## Where to go next

- [What You Need Before Using TurboCell Atlas](what-you-need.md)
- [Wet Lab Guide](wet-lab-guide.md)
- [Tutorials](tutorial.md)

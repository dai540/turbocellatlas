# What You Need Before Using TurboCell Atlas

This page answers another simple question: what do you need before you can use the package successfully?

## Minimum technical ingredients

You need three things.

### 1. A reference atlas

This is the collection of cells you want to search against. In practice, TurboCell Atlas expects this atlas to be represented as embeddings plus metadata.

At minimum, the metadata should contain:

- `cell_id`
- whatever fields you may want to filter on, such as `Disease`, `tissue`, `study`, `sample`, or `celltype_name`

If you want a template, start from:

- `configs/wetlab_metadata_template.csv`

### 2. A query

The query is the cell state you want to search with. This can be:

- one single cell
- a centroid of several labeled cells
- a query vector saved in `.npy`

The important practical question is not only "how do I compute a vector?" but also "what biological state does this vector represent?" If that is unclear, the retrieved cells will also be hard to interpret.

### 3. A way to interpret the results

TurboCell Atlas returns ranked cells, but those ranks need biological context. You therefore need:

- metadata fields that mean something biologically
- a plan for checking whether the returned cells match your expectation
- a way to compare filtered and unfiltered retrieval when cohort effects matter

## Minimum files for the easiest start

If you want the shortest route, inspect these files first:

- `configs/wetlab_metadata_template.csv`
- `notebooks/wet_lab_walkthrough.ipynb`
- `artifacts/wetlab_examples/`

## Optional but strongly recommended

These are not strictly required, but they make the package much easier to use well.

### Meaningful metadata

The package becomes much more useful when the reference atlas has metadata like:

- disease
- tissue
- study
- sample
- cell type annotation

Without these, you can still retrieve neighbors, but you cannot interpret the answer nearly as well.

### A benchmark mindset

Even if you only care about one biological result, it helps to compare:

- exact search
- compressed search
- cohort-filtered search

This tells you whether the answer is stable or fragile.

### A realistic expectation

TurboCell Atlas is not a replacement for all biological judgment. It is a retrieval and comparison tool. The output helps you prioritize similar cells and inspect neighborhood structure, but you still need to decide whether the result makes scientific sense.

## Common misunderstandings

### "I only have raw counts, not embeddings"

That is still workable, but TurboCell Atlas itself mainly expects embeddings at retrieval time. In the current examples, SCimilarity is used as the embedding layer.

### "I only have one interesting cell"

That is fine. The single-cell tutorial article shows that one cell can still be a valid starting point.

### "I do not know which metadata fields matter"

Start with disease, tissue, study, sample, and cell type if you have them. Those are usually the most interpretable fields.

## Where to go next

- [What TurboCell Atlas Can Do](what-turbocellatlas-can-do.md)
- [Get Started](get-started.md)
- [Wet Lab Guide](wet-lab-guide.md)

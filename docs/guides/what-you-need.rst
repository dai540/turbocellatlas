What you need before using TurboCell Atlas
==========================================

This page answers another simple question: what do you need before you can use the package successfully?

Minimum technical ingredients
-----------------------------

You need three things.

A reference atlas
~~~~~~~~~~~~~~~~~

This is the collection of cells you want to search against. In practice, TurboCell Atlas expects this atlas to be represented as embeddings plus metadata.

At minimum, the metadata should contain:

* ``cell_id``
* whatever fields you may want to filter on, such as ``Disease``, ``tissue``, ``study``, ``sample``, or ``celltype_name``

A query
~~~~~~~

The query is the cell state you want to search with. This can be one single cell, a centroid of several labeled cells, or a query vector saved in ``.npy``.

The important practical question is not only how to compute a vector, but also what biological state that vector actually represents.

A way to interpret the results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TurboCell Atlas returns ranked cells, but those ranks need biological context. You therefore need metadata fields that mean something biologically and a plan for checking whether the returned cells match expectation.

Minimum files for the easiest start
-----------------------------------

Inspect these files first:

* ``configs/wetlab_metadata_template.csv``
* ``notebooks/wet_lab_walkthrough.ipynb``
* ``artifacts/wetlab_examples/``

Common misunderstandings
------------------------

I only have raw counts, not embeddings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

That is still workable, but TurboCell Atlas mainly expects embeddings at retrieval time. In the current examples, SCimilarity is used as the embedding layer.

I only have one interesting cell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

That is fine. The single-cell tutorial shows that one cell can still be a valid starting point.

I do not know which metadata fields matter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with disease, tissue, study, sample, and cell type if you have them. Those are usually the most interpretable fields.

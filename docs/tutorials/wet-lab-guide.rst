Wet-lab guide
=============

This guide is written for wet-lab researchers and collaborative users who may not want to start from API names or implementation details.

What goes in
------------

TurboCell Atlas needs three practical ingredients:

* a reference atlas represented as embeddings plus metadata
* a query that represents the cell state you care about
* metadata fields that let you judge whether the retrieved cells make biological sense

What comes out
--------------

The package does not return only one score. The useful output is a bundle:

* ranked cells or nearest-neighbor tables
* metadata columns that tell you what those cells are
* scenario or benchmark summaries that help you compare exact and compressed retrieval
* figures that make it easier to discuss the result with collaborators

How to read the output
----------------------

Read the output in this order:

#. Check whether the returned cells look biologically coherent.
#. Check whether metadata filters changed the answer in an expected way.
#. Compare compressed retrieval with exact retrieval if the workflow includes both.
#. Only then move to a stronger interpretation.

Why this matters
----------------

The package is most useful when a ranked result can be explained in ordinary biological language. If the retrieval table cannot be connected back to disease context, tissue, sample, or cell-type annotations, the result is much harder to trust.

Helpful follow-up pages
-----------------------

* :doc:`../guides/what-can-do`
* :doc:`../guides/what-you-need`
* :doc:`cohort-triage`

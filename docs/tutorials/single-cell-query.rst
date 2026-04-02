Single-cell query
=================

Why this scenario matters
-------------------------

Not every project begins with a curated cell-state centroid. Sometimes you only trust one interesting cell, especially in a pilot study or a small annotation exercise.

Objective
---------

This tutorial asks whether one representative cell can still anchor a meaningful local neighborhood.

Interpretation
--------------

The single-cell scenario is helpful because it lowers the barrier to entry. It shows that you do not need a perfect query design before the package becomes informative. You can begin with one cell, inspect the nearest neighbors, and use that result to decide whether a larger centroid-style query is worth building next.

What to look for
----------------

When reading a single-cell query result, focus on:

* whether the returned cells are consistent with the expected cell type or state
* whether disease and tissue context remain sensible
* whether the neighborhood is tight or noisy

Related artifacts
-----------------

.. image:: ../assets/scenario-single-cell.png
   :alt: Single-cell scenario figure

* ``artifacts/scenario_articles/single_cell_query_summary.csv``

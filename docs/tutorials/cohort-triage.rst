Cohort triage
=============

Why this scenario matters
-------------------------

Many biological questions are not really whole-atlas questions. They are questions like "show me the nearest neighbors, but only inside IPF" or "only inside one tissue context."

Objective
---------

This tutorial shows how metadata filters change the retrieved neighborhood and why those filters matter for interpretation.

What it demonstrates
--------------------

The cohort-triage scenario makes an important practical point: the meaning of a retrieval result depends on context. A result that looks convincing in the whole atlas may become more interpretable, or more suspicious, once disease or tissue filters are applied.

What to inspect
---------------

Pay attention to:

* changes in disease composition
* changes in top-hit identity
* whether the filtered result better matches the scientific question

Related artifacts
-----------------

.. image:: ../assets/scenario-cohort-triage.png
   :alt: Cohort triage scenario figure

* ``artifacts/scenario_articles/cohort_triage_summary.csv``
* ``artifacts/scenario_articles/cohort_triage_disease_composition.csv``

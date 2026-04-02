Tutorials
=========

Tutorials are the best place to learn TurboCell Atlas by following a complete story from question to output.

This section is intentionally prose-rich. A tutorial should explain not only what to run, but also why the workflow exists, what data shape is assumed, what output is returned, and how that output should be interpreted by collaborators who did not run the code themselves.

What tutorials are for
----------------------

TurboCell Atlas becomes understandable when it is tied to a concrete starting point. You may have one unusual fibroblast state in IPF, one suspicious cell in a pilot dataset, or one disease cohort that you want to compare against a larger atlas. Tutorials turn those situations into readable analysis stories.

Each tutorial should help you answer four questions:

#. What biological question am I asking?
#. What data do I need before I can ask it?
#. What output should I expect from the search?
#. How should I interpret the result without over-claiming?

Before you choose a workflow
----------------------------

If you are still deciding whether the package is relevant, start with these two short guides first.

* :doc:`../guides/what-can-do`
* :doc:`../guides/what-you-need`

Those pages answer the simplest questions before you commit to a longer workflow.

Entry points
------------

* :doc:`get-started` for the shortest route from installation to the first search
* :doc:`wet-lab-guide` for the easiest reading path if you mainly care about inputs, outputs, and biological interpretation

Worked examples
---------------

* :doc:`rare-state-retrieval`
* :doc:`single-cell-query`
* :doc:`cohort-triage`
* :doc:`broad-state-tuning`
* :doc:`benchmark-review`

.. toctree::
   :maxdepth: 1
   :hidden:

   get-started
   wet-lab-guide
   rare-state-retrieval
   single-cell-query
   cohort-triage
   broad-state-tuning
   benchmark-review

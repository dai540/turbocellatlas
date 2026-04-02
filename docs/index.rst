TurboCell Atlas
================

TurboCell Atlas is a Python package for atlas-scale single-cell retrieval. It combines compressed candidate generation with exact reranking in the original embedding space, and it is documented as a package-style site rather than a loose collection of pages.

The documentation is written for two kinds of readers at once:

* developers who want to understand the API, benchmark setup, and retrieval stack
* wet-lab and collaborative researchers who need a careful explanation of what the package can do, what inputs are required, and how to read the output tables and figures

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: What TurboCell Atlas can do
      :link: guides/what-can-do
      :link-type: doc

      Start with the plain-language explanation of where the package is already useful and what kind of biological questions it can answer.

   .. grid-item-card:: What you need before using it
      :link: guides/what-you-need
      :link-type: doc

      Read the simplest checklist of required data, metadata, and expectations before a first run.

   .. grid-item-card:: Tutorials
      :link: tutorials/index
      :link-type: doc

      Follow prose-rich walkthroughs that connect a biological question, a query, and an interpretable output.

   .. grid-item-card:: API reference
      :link: api/index
      :link-type: doc

      Inspect the package surface, configuration objects, and search entry points.

.. note::

   Best current success case: rare or coherent disease-state retrieval. Main current limitation: the current Python prototype still leaves TurboQuant slower than exact search in several scenarios.

Start reading here
------------------

If you are new to the package, this is the intended reading order.

#. :doc:`guides/what-can-do`
#. :doc:`guides/what-you-need`
#. :doc:`tutorials/get-started` or :doc:`tutorials/wet-lab-guide`
#. one scenario article from :doc:`tutorials/index`

Documentation map
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/index

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/index

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api/index
   benchmarks
   contributing
   release-notes
   references

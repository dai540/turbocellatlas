Get started
===========

This page is the shortest path from a fresh clone to a working local example.

Install
-------

Install the package in editable mode:

.. code-block:: bash

   pip install -e .[io,bench,dev,docs]

Or create an environment from the repository file:

.. code-block:: bash

   conda env create -f environment.yml

Download the public demo assets
-------------------------------

Run:

.. code-block:: bash

   python scripts/setup_demo_assets.py

This downloads the public SCimilarity tutorial dataset and the model assets used throughout the documentation.

First files to inspect
----------------------

Start with these files before you dive into the code:

* ``configs/wetlab_metadata_template.csv``
* ``notebooks/wet_lab_walkthrough.ipynb``
* ``artifacts/wetlab_examples/``

First search
------------

An example CLI invocation looks like this:

.. code-block:: bash

   tca search \
     --embeddings data/reference.npy \
     --metadata data/reference.jsonl \
     --query data/query.npy \
     --output artifacts/results.json

What to read next
-----------------

* :doc:`wet-lab-guide`
* :doc:`rare-state-retrieval`
* :doc:`../guides/what-you-need`

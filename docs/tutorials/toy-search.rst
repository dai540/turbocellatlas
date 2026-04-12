Toy search tutorial
===================

This tutorial shows the entire workflow with a minimal matrix.

Step 1: create a tiny embedding bank
------------------------------------

.. code-block:: python

   import numpy as np

   embeddings = np.array(
       [
           [1.0, 0.0],
           [0.9, 0.1],
           [0.0, 1.0],
       ],
       dtype=np.float32,
   )

Step 2: define metadata and a query
-----------------------------------

.. code-block:: python

   metadata = [
       {"cell_id": "cell-a", "disease": "IPF"},
       {"cell_id": "cell-b", "disease": "IPF"},
       {"cell_id": "cell-c", "disease": "Control"},
   ]
   query = np.array([1.0, 0.0], dtype=np.float32)

Step 3: search
--------------

.. code-block:: python

   from turbocellatlas import SearchConfig, SearchIndex

   index = SearchIndex(embeddings, metadata, SearchConfig(top_k=2))
   results = index.search(query, filters={"disease": "IPF"})

Step 4: inspect results
-----------------------

The output is a ranked list of result objects with ``rank``, ``item_id``, ``score``, and ``metadata``. This is enough to plug the package into a larger workflow without keeping large example files in the repository itself.

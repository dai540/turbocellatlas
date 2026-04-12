Installation
============

Install the package:

.. code-block:: bash

   pip install -e .

Install development and documentation dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt

Build the documentation:

.. code-block:: bash

   sphinx-build -b html docs docs/_build/html

Run the tests:

.. code-block:: bash

   pytest

What TurboCell Atlas does
=========================

TurboCell Atlas solves one narrow problem: given a dense embedding matrix and a query vector, it returns the top nearest rows by exact cosine similarity.

The current repository is intentionally minimal. It does not try to bundle:

* benchmark pipelines
* downloaded datasets
* notebooks
* approximate-search backends
* one-off analysis scripts

That scope reduction is deliberate. The package is now easier to inspect, easier to install, and cheaper to keep on GitHub.

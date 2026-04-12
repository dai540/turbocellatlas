from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "TurboCell Atlas"
author = "Dai"
copyright = "2026, Dai"
version = "0.3.0"
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_logo = "assets/tca-icon.svg"
html_favicon = "assets/tca-icon.svg"
html_static_path = ["assets"]

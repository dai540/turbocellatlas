from __future__ import annotations

import os
import sys
from datetime import datetime

ROOT = os.path.abspath("..")
SRC = os.path.abspath("../src")

sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)

project = "TurboCell Atlas"
author = "Daiki"
copyright = f"{datetime.now():%Y}, {author}"
release = "0.2.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "anndata": ("https://anndata.readthedocs.io/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

html_theme = "pydata_sphinx_theme"
html_title = "TurboCell Atlas"
html_logo = "assets/tca-icon.svg"
html_favicon = "assets/tca-icon.svg"
html_static_path = ["_static", "assets"]
html_css_files = ["custom.css"]
html_theme_options = {
    "logo": {
        "text": "TurboCell Atlas",
    },
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "secondary_sidebar_items": ["page-toc"],
    "show_nav_level": 2,
    "navigation_depth": 3,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/dai540/turbocellatlas",
            "icon": "fa-brands fa-github",
        }
    ],
    "announcement": "Sphinx rebuild in progress: the docs now ship as a package-style documentation site.",
}

html_context = {
    "default_mode": "light",
}


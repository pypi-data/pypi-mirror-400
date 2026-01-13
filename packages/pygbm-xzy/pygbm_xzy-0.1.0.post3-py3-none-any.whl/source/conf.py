# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Path setup --------------------------------------------------------------

# Add the project root directory to sys.path so Sphinx can find pygbm
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "pygbm"
author = "Ziyao Xiong"
copyright = "2026, Ziyao Xiong"
release = "0.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "nbsphinx",
]


templates_path = ["_templates"]
exclude_patterns = []

# -- Autodoc configuration --------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

autodoc_typehints = "description"

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

nbsphinx_execute = "never"

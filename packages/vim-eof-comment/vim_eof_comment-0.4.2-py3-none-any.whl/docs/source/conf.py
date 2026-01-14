# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
"""Runs configuration for building Sphinx documentation."""

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path('..', 'src').resolve()))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project: str = 'vim-eof-comment'
copyright: str = '2025, Guennadi Maximov C'
author: str = 'Guennadi Maximov C'
release: str = '0.1.33'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: List[str] = [
    'numpydoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.duration',
]

templates_path: List[str] = ['_templates']
exclude_patterns: List[str] = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme: str = 'sphinx_rtd_theme'
html_static_path: List[str] = ['_static']

# -- Options for numpydoc ----------------------------------------------------
numpydoc_xref_param_type = True
numpydoc_validation_checks = {
    "all",  # report on all checks, except the below
    "ES01",
    "EX01",
    "SA01",
}
numpydoc_xref_aliases = {
    'TextIO': 'typing.TextIO',
    'List': 'list',
    'Dict': 'dict',
    'Tuple': 'tuple',
}

# vim: set ts=4 sts=4 sw=4 et ai si sta:

# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'CloverAI'
copyright = '2024, CloverAI'
author = 'CloverAI Team'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'LVRA'
copyright = '2026, Heloise F. Stevance'
author = 'Heloise F. Stevance'
release = 'dev'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

extensions = ['sphinx_wagtail_theme', 
              'sphinxemoji.sphinxemoji',
    'sphinx.ext.autodoc',      # <-- pulls in docstrings
    'sphinx.ext.napoleon',     # <-- supports Google/NumPy docstring styles
    'sphinx.ext.viewcode',     # <-- adds links to source code
]


html_theme = 'sphinx_wagtail_theme'
#html_theme = 'sphinx_book_theme'  # or 'sphinx_rtd_theme' if installed
html_static_path = ['_static']
# include your custom CSS after the theme’s defaults
html_css_files = ["custom.css"]

# This is used by Sphinx in many places, such as page title tags.
project = "LVRA"

# These are options specifically for the Wagtail Theme.
html_theme_options = dict(
    project_name = "Lasair Virtual Research Assistants",
    #favicon = "img/logo.png",
    logo = "img/lvra.png",
    logo_alt = "LVRA",
    logo_height = 79,
    logo_url = "https://lasairvras.github.io/lvra-doc/index.html",
    logo_width = 75,
    github_url = "https://github.com/LasairVRAs/lvra-doc/docs/",
    header_links = "hfstevance.com | https://www.hfstevance.com/",
    footer_links = ",".join([
        "hfstevance@gmail.com |mailto:hfstevance@gmail.com",
    ]),
)

html_last_updated_fmt = "%b %d, %Y"
html_show_sphinx = False


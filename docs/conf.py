# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Import and path setup ---------------------------------------------------

import datetime
import os
import sys

sys.path.insert(0, os.path.abspath("./"))
sys.path.insert(0, os.path.abspath("../"))

# -- Project information -----------------------------------------------------

project = "earthkit-regrid"
author = "European Centre for Medium Range Weather Forecasts"

year = datetime.datetime.now().year
years = "2023-%s" % (year,)
copyright = "%s, European Centre for Medium-Range Weather Forecasts (ECMWF)" % (years,)

# version = earthkit.regrid.__version__
# release = earthkit.regrid.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "nbsphinx",
    "sphinx_issues",
    "earthkit.regrid.sphinxext.xref",
    "earthkit.regrid.sphinxext.module_output",
]


# Path to GitHub repo {group}/{project}  (note that `group` is the GitHub user or organization)
issues_github_path = "ecmwf/earthkit-regrid"


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix of source filenames.
source_suffix = ".rst"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["style.css"]

html_logo = "https://github.com/ecmwf/logos/raw/refs/heads/main/logos/earthkit/earthkit-regrid-dark.svg"

xref_links = {
    "earthkit": ("earthkit", "https://earthkit.readthedocs.io/en/latest/"),
    "earthkit-data": (
        "earthkit-data",
        "https://earthkit-data.readthedocs.io/en/latest/",
    ),
    "earthkit-plots": (
        "earthkit-plots",
        "https://earthkit-plots.readthedocs.io/en/latest/",
    ),
    "fieldlist": (
        "fieldlist",
        "https://earthkit-data.readthedocs.io/en/latest/guide/data_format/grib.html",
    ),
    "field": (
        "field",
        "https://earthkit-data.readthedocs.io/en/latest/guide/data_format/grib.html",
    ),
}

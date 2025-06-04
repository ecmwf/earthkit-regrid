Welcome to earthkit-regrids's documentation
======================================================

|Static Badge| |image1| |License: Apache 2.0| |Latest
Release|

.. |Static Badge| image:: https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE/foundation_badge.svg
   :target: https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE
.. |image1| image:: https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity/incubating_badge.svg
   :target: https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity
.. |License: Apache 2.0| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/apache-2-0
.. |Latest Release| image:: https://img.shields.io/github/v/release/ecmwf/earthkit-regrid?color=blue&label=Release&style=flat-square
   :target: https://github.com/ecmwf/earthkit-regrid/releases


.. important::

    This software is **Incubating** and subject to ECMWF's guidelines on `Software Maturity <https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity>`_.


**earthkit-regrid** is a Python package for regridding. It is one of the components of :xref:`earthkit`.

The API features the :func:`regrid` function to regrid values stored in an ndarray or earthkit-data GRIB :xref:`fieldlist`.

.. note::

    :func:`regrid` is implemented with various backends. The :ref:`default backend <mir-regrid>` uses ECMWF's **MIR (Meteorological Interpolation and Regridding)** library to perform the regridding.


.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/index

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   guide/index
   development

.. toctree::
   :maxdepth: 1
   :caption: Installation

   install
   release_notes/index
   licence


.. toctree::
   :maxdepth: 1
   :caption: Projects

   earthkit <https://earthkit.readthedocs.io/en/latest>


Indices and tables
==================

* :ref:`genindex`

.. * :ref:`modindex`
.. * :ref:`search`

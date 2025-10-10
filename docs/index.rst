Welcome to earthkit-regrid's documentation
======================================================

|Static Badge| |image1| |License: Apache 2.0|

.. |Static Badge| image:: https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE/foundation_badge.svg
   :target: https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE
.. |image1| image:: https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity/emerging_badge.svg
   :target: https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity
.. |License: Apache 2.0| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/apache-2-0

**earthkit-regrid** is a Python package for regridding. It is one of the components of :xref:`earthkit`.

The **earthkit-regrid** API features the :func:`interpolate` function to regrid values stored in an ndarray or earthkit-data GRIB :xref:`fieldlist`. At the moment, regridding is only available for a **pre-defined** set of source and target global grid combinations.


.. toctree::
   :maxdepth: 1
   :caption: Examples
   :titlesonly:

   examples/index

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   interpolate
   gridspec
   inventory/index

.. toctree::
   :maxdepth: 1
   :caption: Installation

   install
   release_notes/index
   development
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

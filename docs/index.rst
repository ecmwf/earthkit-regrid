Welcome to earthkit-regrids's documentation
======================================================

.. warning::

    This project is **BETA** and will be **Experimental** for the foreseeable future. Interfaces and functionality are likely to change, and the project itself may be scrapped. **DO NOT** use this software in any project/software that is operational.


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

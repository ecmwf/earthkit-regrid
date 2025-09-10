Welcome to earthkit-regrid's documentation
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


The API features the :func:`regrid` function taking inputs of Numpy arrays, earthkit-data GRIB :xref:`field` or :xref:`fieldlist` objects, and  Xarray DataArrays or Datasets. It is implemented with various backends, the :ref:`default backend <mir-backend>` uses ECMWF's **MIR (Meteorological Interpolation and Regridding)** library to perform the regridding.


Quick start
-----------

A different interface is available depending on the input data type.

High-level interface
//////////////////////

Use it for data containing geographical information, e.g. earthkit-data :xref:`fieldlist` objects, Xarray DataArrays or Datasets. See: :ref:`regrid() <regrid-high-overview>`.

.. code-block:: python

    import earthkit.data as ekd
    from earthkit.regrid import regrid

    # get fieldlist from a sample GRIB file
    ds = ekd.from_source("sample", "O32_t2.grib2")

    # the target is a regular latitude-longitude grid
    grid = {"grid": [5, 5]}

    ds_res = regrid(ds, grid=grid)


Array-level interface
////////////////////////

Use it for raw data arrays, e.g. Numpy ndarrays. See: :ref:`regrid() <regrid-array-overview>`.

.. code-block:: python

    from earthkit.regrid.array import regrid
    import numpy as np

    vals = np.random.rand(320, 640)
    in_grid = {"grid": [0.25, 0.25]}  # regular latitude-longitude grid
    out_grid = {"grid": "O320"}  # octahedral reduced Gaussian grid

    res_vals, res_grid = regrid(vals, in_grid=in_grid, out_grid=out_grid)



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

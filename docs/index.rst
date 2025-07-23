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


The API features the :func:`regrid` function taking inputs of Numpy arrays or earthkit-data GRIB :xref:`fieldlist` objects. It is implemented with various backends, the :ref:`default backend <mir-regrid>` uses ECMWF's **MIR (Meteorological Interpolation and Regridding)** library to perform the regridding.


Quick start
-----------

.. code-block:: python

    from earthkit.regrid import regrid
    import numpy as np

    # regular latitude-longitude grid with 0.25° increments
    grid_in = {"grid": [0.25, 0.25]}
    # octahedral reduced Gaussian grid
    grid_out = {"grid": "O320"}

    # regrid the data with MIR (the default backend)
    # returns a tuple with the regridded values and the output grid
    vals_res, grid_res = regrid(
        np.random.rand(721, 1440),  # input data
        grid_in=grid_in,  # input grid
        grid_out=grid_out,  # output grid
    )



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

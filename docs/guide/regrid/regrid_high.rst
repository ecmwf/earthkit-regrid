.. _regrid-high-overview:

regrid (high-level)
===============================

.. py:function:: regrid(data, grid=None, interpolation="linear", *, backend="mir", **kwargs)

    Regrid the high-level ``data`` object (with geography information) using the given ``backend`` and options. The ``data`` can be one of the following types:

        - an earthkit-data :xref:`fieldlist`
        - an earthkit-data :xref:`field`
        - a GRIB message as a bytes or :class:`io.BytesIO` object (for ``backend="mir"`` only)
        - an :class:`xarray.DataArray` or :class:`xarray.Dataset`


    To see the available ``**kwargs`` please refer to the documentation of the specific backend. The default backend is :ref:`mir <mir-regrid>`.

    The following ``backends``\ s are available:

    .. list-table::
        :widths: 25 75
        :header-rows: 1

        * - Backend
          - Description
        * - :ref:`mir <mir-regrid-high>`
          - use ECMWF's **Meteorological Interpolation and Regridding library (MIR)** to perform the regridding. This is the default backend.
        * - :ref:`precomputed <precomputed-regrid-high>`
          - use precomputed interpolation weights

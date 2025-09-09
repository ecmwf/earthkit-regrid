.. _regrid-array-overview:

regrid (array-level)
===============================

.. py:function:: regrid(values, in_grid=None, out_grid=None, *, interpolation="linear", backend="mir", **kwargs)

    Regrid the array ``values`` with the given ``backend`` and options.  To see the available ``**kwargs`` please refer to the documentation of the specific backend. The default backend is :ref:`mir <mir-regrid>`.

    The following ``backends``\ s are available:

    .. list-table::
        :widths: 25 75
        :header-rows: 1

        * - Backend
          - Description
        * - :ref:`mir <mir-regrid>`
          - use ECMWF's **Meteorological Interpolation and Regridding library (MIR)** to perform the regridding
        * - :ref:`precomputed <precomputed-regrid>`
          - use precomputed interpolation weights

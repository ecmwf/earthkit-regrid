.. _regrid:

regrid
==============

.. py:function:: regrid(values, backend="mir", **kwargs)

    Regrid the ``values`` with the given ``backend`` and options.  To see the available ``**kwargs`` please refer to the documentation of the specific backend. The default backend is :ref:`mir <mir-regrid>`.


    The following backends are available:

    .. list-table::
        :widths: 25 75
        :header-rows: 1

        * - Backend
          - Description
        * - :ref:`mir <mir-regrid>`
          - use ECMWF's **Meteorological Interpolation and Regridding library (MIR)** to perform the regridding
        * - :ref:`precomputed <precomputed-regrid>`
          - use precomputed interpolation weights stored in a remote inventory managed by ECMWF
        * - :ref:`precomputed-local <precomputed-local-regrid>`
          - use precomputed interpolation weights stored in a local inventory

Version 0.5 Updates
/////////////////////////


Version 0.5.0
===============


Deprecations
+++++++++++++++++++

:ref:`deprecated-interpolate`


Using MIR for regridding
++++++++++++++++++++++++++++

The default backend for the newly added :func:`regrid` method is now :ref:`MIR <mir-regrid>`, ECMWF’s MIR (Meteorological Interpolation and Regridding) library. See the notebook examples:

- :ref:`/examples/mir_numpy_array.ipynb`
- :ref:`/examples/mir_healpix_fieldlist.ipynb`
- :ref:`/examples/mir_octahedral_fieldlist.ipynb`


The regrid method
++++++++++++++++++++++++++++

The :func:`interpolate` method was replaced by :func:`regrid`, which provides a more flexible and powerful interface for regridding data. The new method allows you to specify different ``backends`` and options for regridding. The following backends are available:

    .. list-table::
        :widths: 25 75
        :header-rows: 1

        * - Backend
          - Description
        * - :ref:`mir <mir-regrid>`
          - use ECMWF's **Meteorological Interpolation and Regridding library (MIR)** to perform the regridding. This is the default.
        * - :ref:`precomputed <precomputed-regrid>`
          - use precomputed interpolation weights stored in a remote inventory managed by ECMWF
        * - :ref:`precomputed-local <precomputed-local-regrid>`
          - use precomputed interpolation weights stored in a local inventory


Other new features
++++++++++++++++++++++++++++

- Added :ref:`configuration <config>` control. Currently, it is only related to the :ref:`precomputed <precomputed-regrid>` and :ref:`precomputed-local <precomputed-local-regrid>` backends in :func:`regrid`. See the :ref:`/examples/config.ipynb` notebook for details.
- Added :ref:`in-memory cache <mem_cache>` for precomputed interpolation weights for the :ref:`precomputed <precomputed-regrid>` and :ref:`precomputed-local <precomputed-local-regrid>` backends. See the :ref:`/examples/memory_cache.ipynb` notebook for details.

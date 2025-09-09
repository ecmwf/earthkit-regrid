.. warning::

    With the :ref:`precomputed <precomputed-regrid>` backend we can only perform the regridding if the pre-generated interpolation weights for the given source and target gridspec combination are available. At the moment, the support is limited to the following cases:

    - only global grids are supported
    - for regular latitude-longitude grids only the default scanning mode used at ECMWF is supported (values start at North-West and follow in consecutive rows from West to East)

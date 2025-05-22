.. warning::

    :func:`interpolate` can only perform the interpolation if a pre-generated interpolation matrix for the given source and target gridspec combination is available. At the moment, the support is limited to the following cases:

    - only global grids are supported
    - for regular latitude-longitude grids only the default scanning mode used at ECMWF is supported (values start at North-West and follow in consecutive rows from West to East)

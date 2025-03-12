Interpolation
==============

.. py:function:: interpolate(values, in_grid=None, out_grid=None, matrix_source=None, method='linear')

    Interpolate the ``values`` from the ``in_grid`` onto the ``out_grid``.

    :param values: the input data. It has to be an ndarray representing a single field defined on the ``in_grid``. Alternatively, an earthkit-data GRIB :xref:`fieldlist` can be used, but this only works if ``out_grid`` is a global regular latitude-longitude grid.
    :type values: ndarray, :xref:`fieldlist`
    :param in_grid: the :ref:`gridspec <gridspec>` describing the grid that ``values`` are defined on. When ``values`` is a :xref:`fieldlist` the input grid is automatically detected if ``in_grid`` is not specified.
    :type in_grid: dict
    :param out_grid: the :ref:`gridspec <gridspec>` describing the target grid that ``values`` will be interpolated onto
    :type out_grid: dict
    :param method: the interpolation method. Possible values are ``linear`` and ``nearest-neighbour``. For ``nearest-neighbour`` the following aliases are also supported: ``nn``, ``nearest-neighbor``.
    :type method: str
    :param matrix_source: (experimental) the location of a user specified pre-generated matrix inventory. When it is None the default matrix inventory hosted on an ECMWF download server is used.
    :type matrix_source: str, None
    :return: The same type of data as ``values`` containing the interpolated values.
    :rtype: ndarray, :xref:`fieldlist`
    :raises ValueError: if a pre-generated interpolation matrix is not available
    :raises ValueError: if ``in_grid`` is specified for a :xref:`fieldlist` input

    The interpolation only works when a pre-generated interpolation matrix is available for the given ``in_grid``, ``out_grid`` and ``method`` combination.

    When ``matrix_source`` is None (default) the interpolation matrix is automatically downloaded and stored in a local cache (at ``"~/.cache/earthkit-regrid"``) and when it is needed again the cached version is used.

    Once the matrix is available the interpolation is performed by multiplying the ``values`` vector with it.

.. note::

    Please see the :ref:`inventory <matrix_inventory>` for the list of available matrices.

Examples
--------

    - :ref:`/examples/numpy_arrays.ipynb`
    - :ref:`/examples/healpix_fieldlist.ipynb`
    - :ref:`/examples/octahedral_fieldlist.ipynb`

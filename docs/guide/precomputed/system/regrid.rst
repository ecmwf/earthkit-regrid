.. _precomputed-regrid:

regrid
=====================================

*New in version 0.5.0.*

.. py:function:: regrid(values, in_grid=None, out_grid=None, interpolation='linear', output="values_gridspec", backend="precomputed", **kwargs)
    :noindex:

    Regrid the ``values`` using precomputed weights stored in a remote inventory managed by ECMWF.

    :param values: the following input data types are supported:

        - an ndarray representing a single field defined on the ``in_grid``. A valid ``in_grid`` must be specified.
        - an earthkit-data GRIB :xref:`fieldlist` (requires :xref:`earthkit-data` >= 0.6.0). The input grid is automatically detected from the data (``in_grid`` is ignored). It only works when the ``out_grid`` is a regular latitude-longitude grid.
        - an earthkit-data GRIB :xref:`field` (requires :xref:`earthkit-data` >= 0.6.0). The input grid is automatically detected from the data (``in_grid`` is ignored). It only works when the ``out_grid`` is a regular latitude-longitude grid.

    :type values: ndarray, :xref:`fieldlist`, :xref:`field`
    :param in_grid: the :ref:`gridspec <gridspec-precomputed>` describing the grid that ``values`` are defined on. Ignored when ``values`` is not an ndarray.
    :type in_grid: dict
    :param out_grid: the :ref:`gridspec <gridspec-precomputed>` describing the target grid that ``values`` will be interpolated onto
    :type out_grid: dict
    :param interpolation: the interpolation method. Possible values are ``linear`` and ``nearest-neighbour``. For ``nearest-neighbour`` the following aliases are also supported: ``nn``, ``nearest-neighbor``.
    :type interpolation: str
    :param output: define what is returned when the input is an array, ignored otherwise. Possible values are as follows:

        - "values_gridpec": return a tuple with the interpolated values and the :ref:`gridspec <gridspec-precomputed>` of the output grid. This is the default option.
        - "values": return the interpolated values only
        - "gridpec": return the :ref:`gridspec <gridspec-precomputed>` of the output grid only

    :type output: str
    :return: see the ``output`` parameter for details

    The interpolation only works when a pre-computed interpolation weights are available for the given ``in_grid``, ``out_grid`` and ``interpolation`` combination.

    The interpolation weights are automatically downloaded and stored in a local cache (at ``"~/.cache/earthkit-regrid"``) and when it is needed again the cached version is used.

    Once the weights are available the interpolation is performed by multiplying the ``values`` vector with it (matrix-vector multiplication).

.. note::

    Please see the :ref:`inventory <matrix_inventory>` for the list of supported grid to grid combinations with this backend.

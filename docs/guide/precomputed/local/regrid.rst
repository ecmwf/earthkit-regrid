.. _precomputed-local-regrid:

regrid
===========================================

.. py:function:: regrid(values, in_grid=None, out_grid=None, interpolation='linear', output="values_gridspec", backend="precomputed-local", inventory_path=None)
    :noindex:

    Regrid the ``values`` with using precomputed weights stored at a local path.

    :param values: the following input data types are supported:

        - an ndarray representing a single field defined on the ``in_grid``. A valid ``in_grid`` must be specified.
        - an earthkit-data GRIB :xref:`fieldlist` (requires :xref:`earthkit-data` >= 0.6.0). The input grid is automatically detected from the data (``in_grid`` is ignored).
        - an earthkit-data GRIB :xref:`field` (requires :xref:`earthkit-data` >= 0.6.0). The input grid is automatically detected from the data (``in_grid`` is ignored).

    :type values: ndarray, :xref:`fieldlist`, :xref:`field`
    :param in_grid: the :ref:`gridspec <gridspec>` describing the grid that ``values`` are defined on. Ignored when ``values`` is not an ndarray.
    :type in_grid: dict
    :param out_grid: the :ref:`gridspec <gridspec>` describing the target grid that ``values`` will be interpolated onto
    :type out_grid: dict
    :param interpolation: the interpolation method. Possible values are ``linear`` and ``nearest-neighbour``. For ``nearest-neighbour`` the following aliases are also supported: ``nn``, ``nearest-neighbor``.
    :type interpolation: str
    :param output: define what is returned. Possible values are as follows:

        - "values_gridpec": return a tuple with the interpolated values and the :ref:`gridspec <gridspec>` of the output grid. This is the default option.
        - "values": return the interpolated values only.
        - "gridpec": return the :ref:`gridspec <gridspec>` of the output grid only.

    :type output: str
    :return: see the ``output`` parameter for details

    The interpolation only works when a pre-computed interpolation weights are available for the given ``in_grid``, ``out_grid`` and ``interpolation`` combination in the local inventory specified by ``inventory_path``.

    If the weights are available the interpolation is performed by multiplying the ``values`` vector with it (matrix-vector multiplication).

.. _precomputed-regrid-array:

regrid (array-level) with precomputed weights
========================================================

*New in version 0.5.0.*

.. py:function:: regrid(values, in_grid=None, out_grid=None, *, interpolation='linear', backend="precomputed", inventory="ecmwf")
    :noindex:

    Regrid array ``values`` using precomputed weights.

    :param values: array representing a single field defined on the ``in_grid``.
    :type values: ndarray
    :param in_grid: the :ref:`gridspec <gridspec-precomputed>` describing the grid that ``values`` are defined on.
    :type in_grid: dict
    :param out_grid: the :ref:`gridspec <gridspec-precomputed>` describing the target grid that ``values`` will be interpolated onto
    :type out_grid: dict
    :param interpolation: the interpolation method. Possible values are ``linear`` and ``nearest-neighbour``. For ``nearest-neighbour`` the following aliases are also supported: ``nn``, ``nearest-neighbor``.
    :type interpolation: str
    :param inventory: the path to the inventory of the precomputed weights. The interpolation only works when the weights are available for the given ``in_grid``, ``out_grid`` and ``interpolation`` combination. At present, two inventory types are available:

       - If ``inventory`` is "ecmwf" on None, the remote inventory managed by ECMWF is used. In this case the weights are automatically downloaded and stored in a local cache (at ``"~/.cache/earthkit-regrid"``) and when it is needed again the cached version is used. See the :ref:`inventory <matrix_inventory>` for the list of supported grid to grid combinations with this backend.
       - If ``inventory`` is a local path, a local inventory is used. Please note this in experimental feature only used for development purposes.
    :type inventory: str
    :return: Return a tuple with the interpolated values and the :ref:`gridspec <gridspec-precomputed>` of the output grid.
    :rtype: tuple of ndarray and dict
    :raises ValueError: if the precomputed weights are not available


    The regridding is performed by multiplying the ``values`` vector with the interpolation weights, which forms a sparse matrix (sparse matrix) -vector multiplication).

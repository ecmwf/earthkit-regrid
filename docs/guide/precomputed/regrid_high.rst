.. _precomputed-regrid-high :

regrid (high-level) with precomputed weights
=============================================================

*New in version 0.5.0.*

.. py:function:: regrid(data, grid=None, interpolation='linear', backend="precomputed", inventory="ecmwf")
    :noindex:

    Regrid the high-level ``data`` object (with geography information) using precomputed weights.

    :param data: the input data. The following types are supported:

        - an earthkit-data GRIB :xref:`fieldlist` (requires :xref:`earthkit-data` >= 0.6.0).
        - an earthkit-data GRIB :xref:`field` (requires :xref:`earthkit-data` >= 0.6.0).
        - an :class:`xarray.DataArray` or :class:`xarray.Dataset`
    :type data:  :xref:`fieldlist`, :xref:`field`
    :param grid: the :ref:`gridspec <gridspec-precomputed>` describing the target grid that ``data`` will be interpolated onto
    :type grid: dict
    :param interpolation: the interpolation method. Possible values are ``linear`` and ``nearest-neighbour``. For ``nearest-neighbour`` the following aliases are also supported: ``nn``, ``nearest-neighbor``.
    :type interpolation: str
    :param inventory: the path to the inventory of the precomputed weights. The interpolation only works when the weights are available for the given input grid (automatically determined from the data), target ``grid`` and ``interpolation`` combination. At present, two inventory types are available:

       - If ``inventory`` is "ecmwf" on None, the remote inventory managed by ECMWF is used. In this case the weights are automatically downloaded and stored in a local cache (at ``"~/.cache/earthkit-regrid"``) and when it is needed again the cached version is used. See the :ref:`inventory <matrix_inventory>` for the list of supported grid to grid combinations with this backend.
       - If ``inventory`` is a local path, a local inventory is used. Please note this in experimental feature only used for development purposes.
    :type inventory: str
    :return: The same type of data as ``data`` containing the interpolated values.
    :rtype: :xref:`fieldlist`, :xref:`field`
    :raises ValueError: if the precomputed weights are not available


    The regridding is performed by multiplying the ``data`` vector with the interpolation weights, which forms a sparse matrix (sparse matrix) -vector multiplication).

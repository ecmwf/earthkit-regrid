.. _mir-regrid:

regrid
=============================

*New in version 0.5.0.*

.. py:function:: regrid(values, in_grid=None, out_grid=None, output="values_gridspec", backend="mir", interpolation='linear',  nearest_method="automatic", distance=1, distance_tolerance=1, nclosest=4,  **kwargs)
    :noindex:

    Regrid the ``values`` with the given options using **MIR** (Meteorological Interpolation and Regridding). The ``backend`` parameter is set to "mir" by default so it is not necessary to specify it explicitly.

    :param values: the following input data types are supported:

        - an ndarray representing a single field defined on the ``in_grid``. A valid ``in_grid`` must be specified.
        - an earthkit-data GRIB :xref:`fieldlist` (requires :xref:`earthkit-data` >= 0.6.0). The input grid is automatically detected from the data (``in_grid`` is ignored).
        - an earthkit-data GRIB :xref:`field` (requires :xref:`earthkit-data` >= 0.6.0). The input grid is automatically detected from the data (``in_grid`` is ignored).
        - a GRIB message as a bytes or :class:`io.BytesIO` object. The input grid is automatically detected from the data (``in_grid`` is ignored).

    :type values: ndarray, :xref:`fieldlist`, :xref:`field`, bytes, or :class:`io.BytesIO`
    :param in_grid: the :ref:`gridspec <gridspec>` describing the grid that ``values`` are defined on. Ignored when ``values`` is not an ndarray.
    :type in_grid: dict
    :param out_grid: the :ref:`gridspec <gridspec>` describing the target grid that ``values`` will be interpolated onto
    :type out_grid: dict
    :param output: define what is returned when the input is an array, ignored otherwise. Possible values are as follows:

        - "values_gridpec": return a tuple with the interpolated values and the :ref:`gridspec <gridspec>` of the output grid. This is the default option.
        - "values": return the interpolated values only
        - "gridpec": return the :ref:`gridspec <gridspec>` of the output grid only

    :type output: str
    :param interpolation: the interpolation method. There is a high degree of customisation available to parametrise the available interpolation methods. Please note ot all the interpolation methods support all possible grid types. The possible values are as follows:

        - "linear": Finite Element based interpolation with linear base functions with supporting triangular mesh
        - "grid-box-average": input/output grid box (see [model_grid_box]_) intersections interpolation preserving input value integrals (conservative interpolation).
        - "nearest-neighbour": choose a nearest neighbouring input point to define output point value

    :type interpolation: str

    :param nearest_method: Available for any of the "nearest-" ``interpolation`` methods. The possible values are:

        - "distance": input points with radius (option ``distance``) of output point
        - "nclosest": n-closest input points (option ``nclosest``) to output point (default 4)
        - "distance_and_nclosest": input points respecting ``distance`` :math:`\cap` ``nclosest``.
        - "distance_or_nclosest": input points respecting ``distance`` :math:`\cup` ``nclosest``
        - "nclosest_or_nearest": n-closest input points (option ``nclosest``), if all are at the same distance (within option ``distance_tolerance``) return all points within that distance (robust interpolation of pole values)
        - "nearest_neighbour_with_lowest_index": nearest input point, if at the same distance to other points (option ``nclosest``) chosen by lowest index
        - "sample": sample of n-closest points (option ``nclosest``) out of input points with radius (option ``distance``) of output point, not sorted by distance
        - "sorted_sample": as "sample", sorted by distance
        - "automatic"

    :type nearest_method: str

    :param distance: choice of closest points by distance to input point (metres)
    :type distance: number, default: 1

    :param distance_tolerance: tolerance in metres checking the farthest from nearest points (when ``nearest_method`` is "nclosest" or "nearest").
    :type distance_tolerance: number, default: 1

    :param nclosest: choice of n-closest input points to input point
    :type nclosest: number, default: 4

    :param **kwargs: additional keyword arguments that can be passed to MIR. Since earthkit-regrid only supports the MIR options that are documented above, please use these extra options with care.
    :return: see the ``output`` parameter for details


Examples
--------

- :ref:`/examples/mir_numpy_array.ipynb`
- :ref:`/examples/mir_healpix_fieldlist.ipynb`
- :ref:`/examples/mir_octahedral_fieldlist.ipynb`
- :ref:`/examples/mir_interpolation_types.ipynb`

.. _mir-regrid:

regrid
=============================

.. py:function:: regrid(values, in_grid=None, out_grid=None, output="values_gridspec", backend="mir", interpolation='linear', interpolation_statistics="automatic", nearest_method="automatic", distance_weighting="inverse_distance_weighting_squared", nclosest=4, distance=1, climate_filter_delta=1000, distance_weighting_gaussian_stddev=1, distance_weighting_shepard_power=2,distance_tolerance=1,non_linear="missing_if_heaviest_missing",  **kwargs)
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
    :param interpolation: the interpolation method. The possible values are as follows:

        - "linear"
        - "bilinear"
        - "grid_box_average"
        - "grid_box_statistics"
        - "voronoi_statistics"
        - "k_nearest_neighbours"
        - "k_nearest_neighbours_statistics"
        - "nearest_lsm"
        - "nearest_neighbour"
        - "structured_bicubic"
        - "structured_bilinear"
        - "structured_biquasicubic"
        - "automatic"
    :type interpolation: str
    :param interpolation_statistics: The possible values are as follows:

        - "count"
        - "count_above_upper_limit"
        - "count_below_lower_limit"
        - "maximum"
        - "minimum"
        - "mode_real"
        - "mode_integral"
        - "mode_boolean"
        - "median_integral"
        - "median_boolean"
        - "mean"
        - "variance"
        - "skewness"
        - "kurtosis"
        - "stddev"
        - "automatic"

    :type interpolation_statistics: str
    :param nearest_method: Available for any of the "nearest-" ``interpolation`` methods and also for "k-nearest neighbours" and "nearest_lsm". The possible values are:

        - "distance": input points with radius (option ``distance``) of output point
        - "nclosest": n-closest input points (option ``nclosest``) to output point (default 4)
        - "distance_and_nclosest": input points respecting ``distance`` :math:`\cap` ``nclosest``.
        - "distance_or_nclosest": input points respecting ``distance`` :math:`\cup` ``nclosest``
        - "nclosest_or_nearest": n-closest input points (option ``nclosest``), if all are at the same distance (within option ``distance_tolerance``) return all points within that distance (robust interpolation of pole values)
        - "nearest_neighbour_with_lowest_index": nearest input point, if at the same distance to other points (option ``nclosest``) chosen by lowest index
        - "sample": sample of n-closest points (option ``nclosest``) out of input points with radius (option ``distance``) of output point, not sorted by distance
        - "sorted_sample": as above, sorted by distance
        - "automatic"

    :type nearest_method: str
    :param distance_weighting:
    :type distance_weighting: str, default: "inverse_distance_weighting_squared"

    :param nclosest:
    :type nclosest: number, default: 4

    :param distance:
    :type distance: number, default: 1

    :param climate_filter_delta:
    :type climate_filter_delta: number, default: 1000

    :param distance_weighting_gaussian_stddev:
    :type distance_weighting_gaussian_stddev: number, default: 1

    :param distance_weighting_shepard_power:
    :type distance_weighting_shepard_power: number, default: 2

    :param distance_tolerance:
    :type distance_tolerance: number, default: 1

    :param non_linear:
    :type non_linear: str, default: "missing_if_heaviest_missing"

    :param **kwargs: additional keyword arguments that can be passed to MIR
    :return: see the ``output`` parameter for details

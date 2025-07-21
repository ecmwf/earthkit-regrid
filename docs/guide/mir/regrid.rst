.. _mir-regrid:

regrid
=============================

*New in version 0.5.0.*

.. py:function:: regrid(values, in_grid=None, out_grid=None, output="values_gridspec", backend="mir", interpolation='linear', interpolation_statistics="automatic", nearest_method="automatic", distance=1, distance_tolerance=1, distance_weighting="inverse_distance_weighting_squared", nclosest=4, climate_filter_delta=1000, distance_weighting_gaussian_stddev=1, distance_weighting_shepard_power=2,non_linear="missing_if_heaviest_missing",  **kwargs)
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
        - "bilinear": Finite Element based interpolation with supporting quadrilateral mesh (for reduced grids, possibly containing triangles instead of highly-distorted quadrilaterals)
        - "grid_box_average": input/output grid box intersections interpolation preserving input value integrals (conservative interpolation)
        - "grid_box_statistics": input/output grid box intersections value statistics - see ``interpolation_statistics`` for possible computations.
        - "voronoi_statistics"
        - "k_nearest_neighbours": general method combining nearest method (choice of neighbours) and distance weighting (choice of interpolating neighbour values)
        - "k_nearest_neighbours_statistics"
        - "nearest_neighbour":  parametrised version of "k_nearest_neighbours" to chose a nearest neighbouring input point to define output point value
        - "structured_bicubic": structured methods exploiting grid structure and configurable stencil for fast interpolations (non cacheable, so do not benefit from speedups on subsequent runs).
        - "structured_bilinear"
        - "structured_biquasicubic": computationally economic bicubic interpolatio
        - "automatic"
        .. - "nearest_lsm": interpolated output point takes input only from input points of the same type (land or sea — requires setting land/sea masks)

    :type interpolation: str
    :param interpolation_statistics: Associated options supporting the ``nearest_method``. The possible values are as follows:

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
    :param nearest_method: Available for any of the "nearest-" ``interpolation`` methods and also for "k-nearest neighbours". The possible values are:

        - "distance": input points with radius (option ``distance``) of output point
        - "nclosest": n-closest input points (option ``nclosest``) to output point (default 4)
        - "distance_and_nclosest": input points respecting ``distance`` :math:`\cap` ``nclosest``.
        - "distance_or_nclosest": input points respecting ``distance`` :math:`\cup` ``nclosest``
        - "nclosest_or_nearest": n-closest input points (option ``nclosest``), if all are at the same distance (within option ``distance_tolerance``) return all points within that distance (robust interpolation of pole values)
        - "nearest_neighbour_with_lowest_index": nearest input point, if at the same distance to other points (option ``nclosest``) chosen by lowest index
        - "sample": sample of n-closest points (option ``nclosest``) out of input points with radius (option ``distance``) of output point, not sorted by distance
        - "sorted_sample": as above, sorted by distance
        - "automatic"

    :param distance: choice of closest points by distance to input point (metres)
    :type distance: number, default: 1

    :param distance_tolerance: tolerance in metres checking the farthest from nearest points (when ``nearest_method`` is "nclosest" or "nearest").
    :type distance_tolerance: number, default: 1

    :type nearest_method: str
    :param distance_weighting: only available if ``interpolation`` is "k_nearest_neighbours". General way on how to interpolate input neighbouring point values to output points, including the Inverse Distance Weighting (IDW) class methods (see Wikipedia), which operates over input points returned by ``nearest_method``. Possible values are as follows:

        - "climate_filter": filter for processing topographic data (see IFS documentation, Part IV: Physical Processes,11.3.1 Smoothing operator).
        - "inverse_distance_weighting": IDW of the form :math:`distance^{-1}`. If input points match output point, only that point's value is used for output.
        - "inverse_distance_weighting_squared": IDW of the form :math:`(1 + distance^{2})^{-1}`
        - "shepard": Shepard's method of the form :math:`distance^{-p}` (see ``distance_weighting_shepard_power``)
        - "gaussian": IDW of the form :math:`exp(\frac{-distance^{2}}{2\sigma^{2}})` (see ``distance_weighting_gaussian_stddev``)
        - "nearest_neighbour": emulate ``interpolation`` as "nearest_neighbour`` by picking first point (note that, when ``nearest_method`` is "sample", a random near point is picked).
        - "no": no distance weighting, average input values (irrespective of distance)

    :type distance_weighting: str, default: "inverse_distance_weighting_squared"

    :param nclosest: choice of n-closest input points to input point
    :type nclosest: number, default: 4

    :param distance_weighting_gaussian_stddev: specify Gaussian standard deviation
    :type distance_weighting_gaussian_stddev: number, default: 1

    :param distance_weighting_shepard_power: specify Shepard's method power parameter
    :type distance_weighting_shepard_power: number, default: 2

    :param climate_filter_delta:
    :type climate_filter_delta: number, default: 1000

    :param non_linear:
    :type non_linear: str, default: "missing_if_heaviest_missing"

    :param **kwargs: additional keyword arguments that can be passed to MIR. Since earthkit-regrid only supports the MIR options that are documented above, please use these extra options with care.
    :return: see the ``output`` parameter for details


Examples
--------

- :ref:`/examples/mir_numpy_array.ipynb`
- :ref:`/examples/mir_healpix_fieldlist.ipynb`
- :ref:`/examples/mir_octahedral_fieldlist.ipynb`

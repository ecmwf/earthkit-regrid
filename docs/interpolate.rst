interpolate
==============

.. py:function:: interpolate(values, source_gridspec, target_gridspec, matrix_version=None)

    Interpolate the ``values`` from the ``source_gridspec`` onto the ``target_gridspec``.

    :param values: the input values
    :type values: ndarray
    :param source_gridspec: the gridspec describing the grid that ``values`` are defined on
    :type source_gridspec: dict
    :param target_gridspec: the gridspec describing the target grid that ``values`` will be interpolated onto
    :type target_gridspec: dict
    :param matrix_version: the version of the pre-defined interpolation matrix to be used. None means the latest version will be used.
    :type matrix_version: str
    :rtype: ndarray

Examples
--------

    - :ref:`/examples/interpolation.ipynb`

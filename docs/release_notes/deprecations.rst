Deprecations
=============


.. _deprecated-0.5.0:

Version 0.5.0
-----------------

.. _deprecated-interpolate:

The :func:`interpolate` method is replaced by :func:`regrid`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The :ref:`interpolate` method is deprecated and will be removed in a future release. To perform the same interpolation please use the :ref:`regrid <regrid-precomputed>` method with the "precomputed" backend.


.. list-table::
   :header-rows: 0

   * - Deprecated code
   * -
        .. code-block:: python

            from eathkit.regrid import interpolate
            import numpy as np

            data = np.random.rand(5248)
            interpolated_data = interpolate(
                data, in_grid={"grid": "O32"}, out_grid={"grid": [5, 5]}
            )


   * - New code
   * -

        .. code-block:: python

            from eathkit.regrid import regrid
            import numpy as np

            data = np.random.rand(5248)
            interpolated_data, res_grid = regrid(
                data,
                in_grid={"grid": "O32"},
                out_grid={"grid": [5, 5]},
                backend="precomputed",
            )



See the notebook examples:

- :ref:`/examples/precomp_numpy_array.ipynb`
- :ref:`/examples/precomp_healpix_fieldlist.ipynb`
- :ref:`/examples/precomp_octahedral_fieldlist.ipynb`

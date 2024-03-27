Version 0.3 Updates
/////////////////////////


Version 0.3.0
===============


New features
++++++++++++++++
- restructured and regenerated matrix inventory
- allow using the ``method`` keyword in :func:`interpolate` to specify the interpolation method
- allow using earthkit-data GRIB :xref:`fieldlist` in :func:`interpolate` as input data. This only works when  the output grid is regular a latitude-longitude grid. This feature requires :xref:`earthkit-data` >= 0.6.0
- added notebook examples:

   - :ref:`/examples/healpix_fieldlist.ipynb`
   - :ref:`/examples/octahedral_fieldlist.ipynb`

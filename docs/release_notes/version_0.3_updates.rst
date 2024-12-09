Version 0.3 Updates
/////////////////////////

Version 0.3.5
===============

Fixes
++++++++++++++++
- added support for ORCA input grids in :func:`interpolate`. See the :ref:`ORCA inventory <orca_inventory>` for the list of available ORCA source grids.


Version 0.3.4
===============

Fixes
++++++++++++++++
- fixed issue when the "grid" value in a gridspec could not be specified as a tuple


Version 0.3.3
===============

Fixes
++++++++++++++++
- fixed issue when failed to interpolate earthkit-data :xref:`fieldlist`\ s containing a regular latitude-longitude grid


Version 0.3.2
===============

Fixes
++++++++++++++++
- fixed issue when reading an interpolation matrix from the cache unnecessarily invoked checking of remote matrix files on download server


Version 0.3.1
===============

Fixes
++++++++++++++++
- fixed issue when failed to interpolate from certain reduced Gaussian grids (e.g. O2560, O1280) to regular latitude-longitude grids when the input was an earthkit-data GRIB :xref:`fieldlist`


Version 0.3.0
===============

New features
++++++++++++++++
- restructured and regenerated matrix inventory
- allow using the ``method`` keyword in :func:`interpolate` to specify the interpolation method
- allow using earthkit-data GRIB :xref:`fieldlist` in :func:`interpolate` as input data. This only works when  the output grid is a regular latitude-longitude grid. This feature requires :xref:`earthkit-data` >= 0.6.0
- added notebook examples:

   - :ref:`/examples/healpix_fieldlist.ipynb`
   - :ref:`/examples/octahedral_fieldlist.ipynb`

Version 0.4 Updates
/////////////////////////


Version 0.4.3
===============

Changes
++++++++++++++++

- use new remote host for matrices (:pr:`110`)


Version 0.4.2
===============

Changes
++++++++++++++++

- enabled interpolation from HEALPix nested grids to the 0.05x0.05 degree global latitude-longitude grid. Only the H1024, H512 and H256 HEALPix resolutions are supported for the "linear" and "nearest-neighbour" methods (:pr:`104`). If the input is an earthkit-data GRIB fieldlist `earthkit-data>=0.16.5` is required.


Version 0.4.0
===============

New location of matrix cache
++++++++++++++++++++++++++++

The interpolation  matrix cache is now stored in the user's home directory under the ``~/.cache/earthkit-regrid`` folder. The cache is automatically created if it does not exist. At the moment, no user control is available for the cache and its location cannot be changed, but it will be possible in the future. (:pr:`50`)


New features
++++++++++++++++

- do not download the matrix inventory index file on each startup if it is already available locally (:pr:`49`)
- enabled creating matrices from input and output latitudes and longitudes (experimental feature) (:pr:`52`)
- improved regexp for checking ORCA gridspecs (:pr:`51`)

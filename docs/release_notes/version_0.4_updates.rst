Version 0.4 Updates
/////////////////////////

Version 0.4.1
===============

Fixes
++++++++++++++++++++++++++++

Improved error message when the target grid is not supported for FieldList input


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

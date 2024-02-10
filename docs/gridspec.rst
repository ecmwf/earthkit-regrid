.. _gridspec:

Gridspec
==========

A gridspec describes spatial grids in the form a dict. Its specification is yet to be finalised. However, at the moment, only the ``grid`` key has to be used for the source and target grids earthkit-regrid supports.

The grids supported by earthkit-regrid and their gridspecs are summarised below:


global octahedral reduced gaussian grid
------------------------------------------

The ``grid`` format is::

    OXXX

where *XXX* is the number of latitude lines between the pole and equator. For details about this grid, see `here <https://confluence.ecmwf.int/display/FCST/Introducing+the+octahedral+reduced+Gaussian+grid>`_.

Example:

.. code-block::

    {"grid": "O320"}


global (non-octahedral) reduced gaussian grid
------------------------------------------------

The ``grid`` format is::

    NXXX

where *XXX* is the number of latitude lines between the pole and equator. For details about this grid, see `here <https://confluence.ecmwf.int/display/FCST/Gaussian+grids>`_.

Example:

.. code-block::

    {"grid": "N320"}


global regular latitude-longitude grid
----------------------------------------

The ``grid`` format is::

    [DX, DY]

where *DX* and *DY* are the increments in degrees in longitudes and latitudes, respectively.

Example:

.. code-block::

    {"grid": [1, 1]}

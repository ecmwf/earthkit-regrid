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

    [DLON, DLAT]

where *DLON* and *DLAT* are the increments in degrees in longitudes and latitudes, respectively. This grid definition uses the default scanning mode used at ECMWF: values start at North-West and follow in consecutive rows from West to East, where West is always the 0° meridian.

Example:

.. code-block::

    {"grid": [1, 1]}



HEALPix nested grid
------------------------------------------

The ``grid`` format is::

    HXXX

The ``ordering`` must be set to ``"nested"``. For details about this grid, see `here  <https://en.wikipedia.org/wiki/HEALPix>`_.

Example:

.. code-block::

    {"grid": "H512", "ordering": "nested"}


HEALPix ring grid
------------------------------------------

The ``grid`` format is::

    HXXX

The ``ordering`` can be omitted or set to ``"ring"``.  For details about this grid, see `here  <https://en.wikipedia.org/wiki/HEALPix>`_.

Example:

.. code-block::

    {"grid": "H512", "ordering": "ring"}
    {"grid": "H512"}


ORCA grid
------------------------------------------

The ``grid`` format is::

    eORCAXXX_subtype

The ``subtype`` must be "T", "U", "V" or "W".

Example:

.. code-block::

    {"grid": "eORCA025_T"}

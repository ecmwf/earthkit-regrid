.. _gridspec:

Gridspecs (with the MIR backend)
====================================

A gridspec describes spatial grids in the form a dict.

.. warning::

    The gridspec format is not finalised yet and may change in future releases. Subarea specification is not yet supported.

The gridspecs supported by the ``in_grid`` and ``out_grid`` options in :ref:`regrid() <mir-regrid>` with the (default) MIR backend are summarised below:


Global octahedral reduced Gaussian grid
------------------------------------------

The ``grid`` format is::

    [Oo]XXX

where *XXX* is the number of latitude lines between the pole and equator. For details about this grid, see `here <https://confluence.ecmwf.int/display/FCST/Introducing+the+octahedral+reduced+Gaussian+grid>`_.

Example:

.. code-block::

    {"grid": "O320"}
    {"grid": "o320"}


Global (non-octahedral) reduced Gaussian grid
------------------------------------------------

The ``grid`` format is::

    [Nn]XXX

where *XXX* is the number of latitude lines between the pole and equator. For details about this grid, see `here <https://confluence.ecmwf.int/display/FCST/Gaussian+grids>`_.

Example:

.. code-block::

    {"grid": "N320"}
    {"grid": "n320"}


Global regular latitude-longitude grid
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

    [Hh]XXX

The ``order`` must be set to ``"nested"``. For details about this grid, see `here  <https://en.wikipedia.org/wiki/HEALPix>`_.

Example:

.. code-block::

    {"grid": "H512", "order": "nested"}
    {"grid": "h512", "order": "nested"}


HEALPix ring grid
------------------------------------------

The ``grid`` format is::

    [Hh]XXX

The ``order`` can be omitted or set to ``"ring"``.  For details about this grid, see `here  <https://en.wikipedia.org/wiki/HEALPix>`_.

Example:

.. code-block::

    {"grid": "H512", "order": "ring"}
    {"grid": "H512"}
    {"grid": "h512"}


.. ORCA grid
.. ------------------------------------------

.. The ``grid`` format is::

..     eORCAXXX_subtype

.. The ``subtype`` must be "T", "U", "V" or "W".

.. Example:

.. .. code-block::

..     {"grid": "eORCA025_T"}

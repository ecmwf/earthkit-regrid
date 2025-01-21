.. _mem_cache:

In-memory matrix caching
===========================

*New in version 0.5.0.*

Purpose
-------

earthkit-regrid provides an **in-memory cache** for interpolation matrices. When it is enabled, matrices loaded from the disk are stored in memory and when we call :func:`interpolate` with the same grids they do not have to be loaded from disk again. The cache can be configured to have a maximum size and eviction policy.

.. note::

    Please note that the earthkit-regrid in-memory cache configuration is managed through the :doc:`config`.

.. _mem_cache_policies:

In-memory cache policies
----------------------------

The primary config option to control the in-memory cache is ``matrix-memory-cache-policy``, which can take the following values:

  - :ref:`largest <largest_mem_cache_policy>` (default)
  - :ref:`lru <lru_mem_cache_policy>`
  - :ref:`unlimited <unlimited_mem_cache_policy>`
  - :ref:`off <off_mem_cache_policy>`


.. _largest_mem_cache_policy:

Largest cache policy
++++++++++++++++++++++

When the ``matrix-memory-cache-policy`` is "largest" first evicts the largest matrices from the in-memory cache (default). The cache eviction policy is applied before loading the matrix to ensure that it will fit into the cache. When it is not possible the behaviour depends on the ``matrix-memory-cache-strict-mode`` option. The maximum memory size of the in-memory cache is defined by the ``maximum-matrix-memory-cache-size`` option. The default is 500 MB.

.. code-block:: python

  >>> from earthkit.regrid import cache, config
  >>> config.set("matrix-memory-cache-policy", "user")
  >>> config.get("matrix-memory-cache-policy")
  'user'
  >>> config.get("maximum-matrix-memory-cache-size")
  524288000
  >>> config.get("matrix-memory-cache-strict-mode")
  False


.. _lru_mem_cache_policy:

LRU cache policy
++++++++++++++++++++++

When the ``matrix-memory-cache-policy`` is "lru" first evicts the least recently used matrices from the in-memory cache. The cache eviction policy is applied before loading the matrix to ensure that it will fit into the cache. When it is not possible the behaviour depends on the ``matrix-memory-cache-strict-mode`` option. The maximum memory size of the in-memory cache is defined by the ``maximum-matrix-memory-cache-size`` option. The default is 500 MB.

.. code-block:: python

  >>> from earthkit.regrid import cache, config
  >>> config.set("matrix-memory-cache-policy", "lru")
  >>> config.get("matrix-memory-cache-policy")
  'lru'
  >>> config.get("maximum-matrix-memory-cache-size")
  524288000
  >>> config.get("matrix-memory-cache-strict-mode")
  False


.. _unlimited_mem_cache_policy:

Unlimited cache policy
++++++++++++++++++++++

When the ``matrix-memory-cache-policy`` is "unlimited" will keep all matrices in memory.

.. code-block:: python

  >>> from earthkit.regrid import cache, config
  >>> config.set("matrix-memory-cache-policy", "unlimited")
  >>> config.get("matrix-memory-cache-policy")
  'unlimited'


.. _off_mem_cache_policy:

Off cache policy
++++++++++++++++++++++

When the ``matrix-memory-cache-policy`` is "off" there is no cache, the matrices are always loaded from disk.


.. code-block:: python

  >>> from earthkit.regrid import cache, config
  >>> config.set("matrix-memory-cache-policy", "off")
  >>> config.get("matrix-memory-cache-policy")
  'off'

.. _mem_cache_state:

Getting the state of the in-memory cache
------------------------------------------

The current status of the in-memory cache can be retrieved using the :func:`memory_cache_info` function. It returns a namedtuple with fields ``hits``, ``misses``, ``maxsize``, ``currsize``, ``count`` and  ``policy``.

.. code:: python

  >>> from earthkit.regrid import memory_cache_info
  >>> memory_cache_info()
  CacheInfo(hits=9, misses=1, maxsize=524288000, currsize=259170724, count=1, policy='largest')


.. _mem_cache_clear:

Clearing the in-memory cache
-----------------------------

The in-memory cache can be cleared using the :func:`clear_memory_cache` function.

.. code:: python

  >>> from earthkit.regrid import clear_memory_cache
  >>> clear_memory_cache()
  >>> memory_cache_info()
  CacheInfo(hits=0, misses=0, maxsize=524288000, currsize=0, count=0, policy='largest')

.. _mem_cache_limits:

In-memory cache limits
----------------------------

.. warning::

  These config options are only used when ``matrix-mempry-cache-policy`` is :ref:`largest <largest_mem_cache_policy>` or :ref:`lru <lru_mem_cache_policy>`.

Maximum-matrix-memory-cache-size
  The ``maximum-matrix-memory-cache-size`` option defines the maximum memory size of the in-memory cache in bytes. The default is 500 MB.

Matrix-memory-cache-strict-mode
    When the ``matrix-memory-cache-strict-mode`` option is ``True``, raises ValueError if the matrix cannot be fitted into the cache. If ``False`` and the matrix cannot be fitted into the cache it simply does not load the matrix into the cache. The default is ``False``.


Examples
--------

- :ref:`/examples/memory_cache.ipynb`

.. code-block:: python

    import numpy as np
    from earthkit.regrid import interpolate, config

    # set memory cache with a maximum size of 100 MB to evict the largest matrices first
    config.set(
        matrix_memory_cache_policy="largest",
        maximum_matrix_memory_cache_size=100 * 1024**2,
    )
    print(memory_cache_info())

    # create a random data array and interpolate it
    data = np.random.rand(5248)
    interpolated_data = interpolate(
        data, in_grid={"grid": "O32"}, out_grid={"grid": [5, 5]}
    )
    print(memory_cache_info())

    # repeat interpolation, this time the matrix is loaded from the cache
    data = np.random.rand(5248)
    interpolated_data = interpolate(
        data, in_grid={"grid": "O32"}, out_grid={"grid": [5, 5]}
    )
    print(memory_cache_info())

output: ::

    CacheInfo(hits=0, misses=0, maxsize=104857600, currsize=0, count=0, policy='largest'))
    CacheInfo(hits=0, misses=1, maxsize=104857600, currsize=102340, count=1, policy='largest')
    CacheInfo(hits=1, misses=1, maxsize=104857600, currsize=102340, count=1, policy='largest')

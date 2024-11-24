.. _memory_cache:

Memory cache
==================

.. py:function:: set_memory_cache(policy="largest", max_size=300 * 1024**2, strict=False)

    *New in version 0.4.0.*

    Control the in-memory cache used to store interpolation matrices.

    :param str policy: The matrix in-memory cache policy. The possible values are as follows:

        - ``"off"``: no cache, the matrices are always loaded from disk
        - ``"unlimited"``: keep all matrices in memory
        - ``"largest"``: first evict the largest matrices from the cache (default)
        - ``"lru"``: first evict the least recently used matrices from the cache

    :param int max_size: The maximum memory size of the in-memory cache in bytes. Only used when ``policy`` is ``"largest"`` or ``"lru"``.
    :param bool strict: If ``True``, raises ValueError if the matrix cannot be fit into the cache. If ``False``, the matrix is not loaded into the cache under the same conditions. Only used when ``policy`` is ``"largest"`` or ``"lru"``.
    :raises ValueError: if the estimated size of the matrix to be loaded does not fit into the cache. Only raised when ``strict=True`` and  ``policy`` is ``"largest"`` or ``"lru"``.

    When ``policy`` is ``"largest"`` or ``"lru"`` the cache eviction policy is applied before loading the matrix to ensure that it will fit into the cache. When it is not possible the behaviour depends on the ``strict`` option.


.. py:function:: clear_memory_cache()

    *New in version 0.4.0.*

    Clear the in-memory cache used to store interpolation matrices.


.. py:function:: memory_cache_info()

    *New in version 0.4.0.*

    Return the current status of the in-memory cache used to store interpolation matrices.

    :return: cache status with fields ``hits``, ``misses``, ``maxsize``, ``currsize``, ``count`` and  ``policy``
    :rtype: namedtuple


Examples
--------

- :ref:`/examples/memory_cache.ipynb`


.. code-block:: python

    import numpy as np
    from earthkit.regrid import set_memory_cache, interpolate, memory_cache_info

    # set memory cache with a maximum size of 100 MB to evict the largest matrices first
    set_memory_cache(policy="largest", max_size=100 * 1024**2)
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

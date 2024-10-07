set_memory_cache
==================

.. py:function:: set_memory_cache(policy="largest", max_size=300 * 1024**2, ensure_matrix_size=False)

    *New in version 0.4.0.*

    Control the in-memory cache used to store interpolation matrices.

    :param str policy: The matrix in-memory cache policy. The possible values are as follows:

        - ``"off"``: no cache
        - ``"unlimited"``: keep all matrices in memory
        - ``"largest"``: first removes the largest matrices from memory
        - ``"lru"``: first removes the least recently used matrices from memory

    :param int max_size: The maximum memory size of the in-memory cache in bytes. Only used when the policy is not ``off`` or ``"unlimited"``.
    :param bool ensure_matrix_size: If True, ensure that the matrix fits into the cache before loading it. Only used when ``policy`` is no ``"off"`` or ``"unlimited"``.
    :raises ValueError: if the estimated size of the matrix to be loaded does not fit into the cache. Only raised when ``ensure_matrix_size=True`` and  ``policy`` is not ``"off"`` or ``"unlimited"``.

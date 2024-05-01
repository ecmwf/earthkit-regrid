# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import threading
import time
from collections import namedtuple

from earthkit.regrid.utils.hash import make_sha

LOG = logging.getLogger(__name__)


_MatrixMemoryItem = namedtuple("MatrixMemoryItem", ["data", "size", "last"])
_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize", "count"])


class MatrixMemoryCache:
    """Memory bound LRU cache for interpolation matrices"""

    def __init__(self, max_mem=0):
        """Create a new cache with a maximum memory size in bytes. 0 means no cache."""
        self.items = {}
        self.max_mem = max_mem
        self.curr_mem = 0
        self.hits = 0
        self.misses = 0
        self.lock = threading.Lock()
        self.update()

    def get(self, *args, create):
        if self.max_mem == 0:
            return create(*args)

        with self.lock:
            if self.max_mem == 0:
                return create(*args)

            key = make_sha(args)
            if key in self.items:
                self.hits += 1
                item = self.items[key]
                self.items[key] = _MatrixMemoryItem(item.data, item.size, time.time())
                return item.data

            data = create(*args)
            self.items[key] = _MatrixMemoryItem(
                data, MatrixMemoryCache._matrix_size(data), time.time()
            )

            self.misses += 1
            self._manage()

            return data

    @staticmethod
    def _matrix_size(m):
        # see: https://stackoverflow.com/questions/11173019/determining-the-byte-size-of-a-scipy-sparse-matrix

        m = m[0]
        try:
            # TODO: This works for bsr, csc and csr matrices but not for other types.
            return m.data.nbytes + m.indptr.nbytes + m.indices.nbytes

        except Exception:
            return 0

    def update(self):
        """Called when settings change"""
        from earthkit.regrid.utils.caching import SETTINGS

        max_mem = SETTINGS.get("maximum-matrix-memory-cache-size", 0)

        with self.lock:
            if self.max_mem != max_mem:
                self.max_mem = max_mem
                self._manage()

    def _manage(self):
        # must be called within a lock
        if self.max_mem == 0:
            self._clear()
        elif self.max_mem is not None:
            self.curr_mem = self._curr_mem()

            while self.curr_mem >= self.max_mem:
                (
                    _,
                    oldest_key,
                    oldest_item,
                ) = min((v.last, k, v) for k, v in self.items.items())
                self.curr_mem -= oldest_item.size
                del self.items[oldest_key]
        else:
            self.curr_mem = self._curr_mem()

    def clear(self):
        """Clear the cache"""
        with self.lock:
            self._clear()

    def _clear(self):
        # must be called within a lock
        self.items.clear()
        self.hits = 0
        self.misses = 0
        self.curr_mem = 0

    def _curr_mem(self):
        # must be called within a lock
        return sum(v.size for v in self.items.values())

    def info(self):
        """Report cache statistics"""
        with self.lock:
            return _CacheInfo(
                self.hits, self.misses, self.max_mem, self.curr_mem, len(self.items)
            )


MEMORY_CACHE = MatrixMemoryCache()

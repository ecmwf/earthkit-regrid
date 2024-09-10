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
from collections import OrderedDict, namedtuple

from earthkit.regrid.utils.hash import make_sha

LOG = logging.getLogger(__name__)


_MemoryItem = namedtuple("MemoryItem", ["data", "size", "last"])
_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize", "count"])


def matrix_size(m):
    # see: https://stackoverflow.com/questions/11173019/determining-the-byte-size-of-a-scipy-sparse-matrix
    m = m[0]
    try:
        # TODO: This works for bsr, csc and csr matrices but not for other types.
        return m.data.nbytes + m.indptr.nbytes + m.indices.nbytes

    except Exception as e:
        print(e)
        return 0


class MemoryLRUCache:
    """Memory bound LRU cache for interpolation matrices"""

    def __init__(self, max_mem=0, size_fn=None, size_settings_key=None):
        """Create a new cache with a maximum memory size in bytes. 0 means no cache."""
        self.items = OrderedDict()
        self.max_mem = max_mem
        self.curr_mem = 0
        self.hits = 0
        self.misses = 0

        if size_fn is None:
            raise ValueError("size_fn must be provided")
        self.size_fn = size_fn
        self.size_settings_key = size_settings_key

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
                item = self.items[key]
                self.items.move_to_end(key)
                self.hits += 1
                return item.data

            data = create(*args)
            self.items[key] = _MemoryItem(data, self.size_fn(data), time.time())
            self.curr_mem += self.items[key].size

            self.misses += 1
            self._manage()

            return data

    def update(self):
        """Called when settings change"""
        if self.size_settings_key:
            from earthkit.regrid.utils.caching import SETTINGS

            max_mem = SETTINGS.get(self.size_settings_key, self.max_mem)

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
                _, item = self.items.popitem(0)
                self.curr_mem -= item.size
                del item
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


class MatrixMemoryCache(MemoryLRUCache):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            size_fn=matrix_size,
            size_settings_key="maximum-matrix-memory-cache-size",
            **kwargs,
        )


MEMORY_CACHE = MatrixMemoryCache()

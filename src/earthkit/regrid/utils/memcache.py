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
from abc import ABCMeta, abstractmethod
from collections import OrderedDict, namedtuple

from earthkit.regrid.utils.hash import make_sha
from earthkit.regrid.utils.matrix import matrix_memory_size

LOG = logging.getLogger(__name__)


_MemoryItem = namedtuple("MemoryItem", ["data", "size", "last"])
_CacheInfo = namedtuple(
    "CacheInfo", ["hits", "misses", "maxsize", "currsize", "count", "policy"]
)


def matrix_size(m):
    m = m[0]
    try:
        return matrix_memory_size(m)
    except Exception as e:
        LOG.warning("Could not compute matrix memory size", e)
        return 0


def estimate_matrix_size(entry):
    """Estimate the size of a matrix entry"""
    try:
        return entry["_raw"]["memory"]
    except Exception as e:
        LOG.warning(f"Could not estimate matrix memory size from entry={entry}. {e}")
        return 0


class MemoryCachePolicy(metaclass=ABCMeta):
    name = None

    def __init__(self, cache):
        self.cache = cache
        self.check()

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def reduce(self, *args, **kwargs):
        pass

    @staticmethod
    def make(name):
        if name not in CACHE_POLICIES:
            raise ValueError(f"Unknown cache policy: {name}")
        return CACHE_POLICIES[name]

    @abstractmethod
    def has_cache(self):
        pass

    @abstractmethod
    def has_limit(self):
        pass


class NoPolicy(MemoryCachePolicy):
    name = "off"

    def check(self):
        self.cache.max_mem = 0
        self.cache.strict = False

    def reduce(self, *args, **kwargs):
        self.cache._clear()

    def has_cache(self):
        return False

    def has_limit(self):
        return False


class UnlimitedPolicy(MemoryCachePolicy):
    name = "unlimited"

    def check(self):
        self.cache.max_mem = None
        self.cache.strict = False

    def reduce(self, *args, **kwargs):
        # must be called within a lock
        self.cache.curr_mem = self.cache._curr_mem()

    def has_cache(self):
        return True

    def has_limit(self):
        return False


class LRUPolicy(MemoryCachePolicy):
    name = "lru"

    def check(self):
        if self.cache.max_mem <= 0:
            raise ValueError(f"Cannot use {self.name} policy with max_mem<=0")
        if self.cache.max_mem is None:
            raise ValueError(f"Cannot use {self.name} policy with max_mem=None")

    def reduce(self, target_size):
        # must be called within a lock
        if not self.cache.items:
            return

        while self.cache.curr_mem >= target_size:
            _, item = self.cache.items.popitem(0)
            self.cache.curr_mem -= item.size
            del item
            if not self.cache.items:
                break

    def has_cache(self):
        return True

    def has_limit(self):
        return True


class LargestPolicy(MemoryCachePolicy):
    name = "largest"

    def check(self):
        if self.cache.max_mem <= 0:
            raise ValueError(f"Cannot use {self.name} policy with max_mem<=0")
        if self.cache.max_mem is None:
            raise ValueError(f"Cannot use {self.name} policy with max_mem=None")

    def reduce(self, target_size):
        # must be called within a lock
        if not self.cache.items:
            return

        while self.cache.curr_mem >= target_size:
            _, largest = max((v.size, k) for k, v in self.cache.items.items())
            self.cache.curr_mem -= self.cache.items[largest].size
            if self.cache.curr_mem < 0:
                self.cache.curr_mem = 0
            # LOG.debug(f"evicting={self.cache.items[largest]} curr_mem={self.cache.curr_mem}")
            del self.cache.items[largest]
            if not self.cache.items:
                break

    def has_cache(self):
        return True

    def has_limit(self):
        return True


CACHE_POLICIES = {
    p.name: p for p in [NoPolicy, UnlimitedPolicy, LRUPolicy, LargestPolicy]
}


class MemoryCache:
    MAX_SIZE_KEY = "maximum-matrix-memory-cache-size"
    POLICY_KEY = "matrix-memory-cache-policy"
    STRICT_KEY = "matrix-memory-cache-strict-mode"

    def __init__(
        self,
        max_mem=300 * 1024 * 1024,
        size_fn=None,
        policy="largest",
        strict=False,
    ):
        """
        Memory bound in-memory cache for interpolation matrices.

        Parameters
        ----------
        max_mem: int
            Maximum memory size in bytes. 0 means no cache. None means no limit.
        size_fn: callable
            Function that returns the size of an item in the cache.
        size_settings_key: str
            Key in the settings that holds the maximum memory size.
        policy_settings_key: str
            Key in the settings that holds the cache policy.
        """
        self.items = OrderedDict()
        self.max_mem = max_mem
        self.curr_mem = 0
        self.hits = 0
        self.misses = 0

        if size_fn is None:
            raise ValueError("size_fn must be provided")
        self.size_fn = size_fn
        self.strict = strict

        self.policy = MemoryCachePolicy.make("largest" if policy is None else policy)(
            self
        )

        self._has_settings = True

        self.lock = threading.Lock()
        self.update()

    def get(self, *args, create=None, find_entry=None, create_from_entry=None):
        if not self.policy.has_cache():
            return create(*args)

        with self.lock:
            if not self.policy.has_cache():
                return create(*args)

            key = make_sha(args)
            if key in self.items:
                item = self.items[key]
                # TODO: move_to_end is only required for the "lru" policy
                self.items.move_to_end(key)
                self.hits += 1
                return item.data

            if self.policy.has_limit():
                data = self._create_with_pre_check(find_entry, create_from_entry, *args)
            else:
                data = self._create(create, *args)

            self.items[key] = _MemoryItem(data, self.size_fn(data[0]), time.time())
            self.curr_mem += self.items[key].size

            self.misses += 1
            self._reduce()

            return data

    def _create(self, create, *args):
        if create is None:
            raise ValueError("create must be provided")
        return create(*args)

    def _create_with_pre_check(self, find_entry, create_from_entry, *args):
        if find_entry is None:
            raise ValueError("find_entry must be provided")
        if create_from_entry is None:
            raise ValueError("create_from_entry must be provided")

        entry = find_entry(*args)
        if entry is not None:
            capacity = self._capacity()
            estimated_memory = estimate_matrix_size(entry)
            target_size = self.max_mem - estimated_memory
            # LOG.debug(f"{capacity=} {estimated_memory=} {target_size=}")
            if estimated_memory > capacity and estimated_memory <= self.max_mem:
                assert target_size >= 0
                self._reduce(target_size=target_size)

            if self.strict and self._capacity() < estimated_memory:
                raise ValueError(
                    (
                        "Matrix too large to fit in memory cache. "
                        f"Estimated size: {estimated_memory} bytes > capacity: {self._capacity()} bytes"
                    )
                )

        return create_from_entry(entry)

    def update(self):
        """Called when settings change"""
        if self._has_settings:
            from earthkit.regrid.utils.caching import SETTINGS

            assert self.policy

            def _update(name, key):
                current = getattr(self, name)
                value = SETTINGS.get(key, current)
                if current != value:
                    setattr(self, name, value)
                    return True
                return False

            def _update_policy():
                policy = SETTINGS.get(self.POLICY_KEY, self.policy.name)
                if self.policy.name != policy:
                    self.policy = MemoryCachePolicy.make(policy)(self)
                    return True
                return False

            with self.lock:
                if any(
                    [
                        _update("max_mem", self.MAX_SIZE_KEY),
                        _update("strict", self.STRICT_KEY),
                        _update_policy(),
                    ]
                ):
                    self._reduce()

    def _reduce(self, target_size=None):
        # must be called within a lock
        self.policy.check()

        if not self.policy.has_cache():
            self._clear()
        else:
            if target_size is None:
                target_size = self.max_mem
            self.curr_mem = self._curr_mem()
            self.policy.reduce(target_size=target_size)

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
                self.hits,
                self.misses,
                self.max_mem,
                self.curr_mem,
                len(self.items),
                self.policy.name,
            )

    def _capacity(self):
        # must be called within a lock
        return self.max_mem - self.curr_mem


class MatrixMemoryCache(MemoryCache):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            size_fn=matrix_memory_size,
            **kwargs,
        )


MEMORY_CACHE = MatrixMemoryCache()


# TODO: enable the commented out options when estimate_matrix_size is implemented
def set_memory_cache(
    policy="largest",
    max_size=300 * 1024 * 1024,
    strict=False,
):
    from earthkit.regrid.utils.caching import SETTINGS

    SETTINGS[MEMORY_CACHE.MAX_SIZE_KEY] = max_size
    SETTINGS[MEMORY_CACHE.POLICY_KEY] = policy
    SETTINGS[MEMORY_CACHE.STRICT_KEY] = strict
    MEMORY_CACHE.update()


def clear_memory_cache():
    MEMORY_CACHE.clear()


def memory_cache_info():
    return MEMORY_CACHE.info()

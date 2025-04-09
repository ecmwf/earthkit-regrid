# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os

import numpy as np
import pytest

from earthkit.regrid import interpolate
from earthkit.regrid.utils.testing import earthkit_test_data_path

DB_PATH = earthkit_test_data_path("local", "db")
DATA_PATH = earthkit_test_data_path("local")

# TODO: these tests cannot be run in parallel as they modify the global settings.
# We should refactor the tests once the settings are properly implemented.


def file_in_testdir(filename):
    return os.path.join(DATA_PATH, filename)


def run_interpolate(mode):
    v_in = np.load(file_in_testdir("in_N32.npz"))["arr_0"]
    np.load(file_in_testdir(f"out_N32_10x10_{mode}.npz"))["arr_0"]
    interpolate(v_in, {"grid": "N32"}, {"grid": [10, 10]}, method=mode, matrix_source=DB_PATH)


@pytest.fixture
def patch_estimate_matrix_memory(monkeypatch):
    from earthkit.regrid.backends.db import MatrixIndex

    def patched_estimate_memory(self):
        return 200000

    monkeypatch.setattr(MatrixIndex, "estimate_memory", patched_estimate_memory)


@pytest.mark.parametrize(
    "policy,adjust_to, evict",
    [("lru", "second", "first"), ("largest", "second", "first")],
)
def test_local_memcache_core_1(policy, adjust_to, evict):
    """The cache is large enough to hold two matrices. The first matrix is larger than the second one."""
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    max_mem = 300 * 1024 * 1024

    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, max_mem, 0, 0, policy)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 1
        info = MEMORY_CACHE.info()
        assert info.hits == 0
        assert info.misses == 1
        assert info.maxsize == max_mem
        assert info.currsize > 0
        assert info.count == 1
        mem_first = MEMORY_CACHE.curr_mem

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 1
        assert MEMORY_CACHE.info() == (1, 1, max_mem, mem_first, 1, policy)

        run_interpolate("nearest-neighbour")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 2
        mem_second = MEMORY_CACHE.curr_mem - mem_first
        MEMORY_CACHE.info() == (1, 2, max_mem, MEMORY_CACHE.curr_mem, 2, policy)

        run_interpolate("nearest-neighbour")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 2
        assert MEMORY_CACHE.misses == 2
        assert MEMORY_CACHE.info() == (2, 2, max_mem, MEMORY_CACHE.curr_mem, 2, policy)

        # We rely on the first matrix being larger than the second one.
        assert mem_first > mem_second

        # reduce max size so that the matrix specified by "evict" should be evicted.
        if adjust_to == "first":
            max_mem = mem_first + 10
        elif adjust_to == "second":
            max_mem = mem_second + 10
        else:
            raise ValueError(f"Invalid adjust_to value: {adjust_to}")

        config.set("maximum-matrix-memory-cache-size", max_mem)

        if evict == "first":
            assert MEMORY_CACHE.info() == (2, 2, max_mem, mem_second, 1, policy)
        elif evict == "second":
            assert MEMORY_CACHE.info() == (2, 2, max_mem, mem_first, 1, policy)
        else:
            raise ValueError(f"Invalid evict value: {evict}")


@pytest.mark.parametrize(
    "policy,adjust_to, evict",
    [("lru", "second", "first"), ("largest", "first", "second")],
)
def test_local_memcache_core_2(policy, adjust_to, evict):
    """The cache is large enough to hold two matrices. The first matrix is smaller than the second one."""
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    max_mem = 300 * 1024 * 1024
    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, max_mem, 0, 0, policy)

        run_interpolate("nearest-neighbour")
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 1
        info = MEMORY_CACHE.info()
        assert info.hits == 0
        assert info.misses == 1
        assert info.maxsize == max_mem
        assert info.currsize > 0
        assert info.count == 1
        mem_first = MEMORY_CACHE.curr_mem

        run_interpolate("nearest-neighbour")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 1
        assert MEMORY_CACHE.info() == (1, 1, max_mem, mem_first, 1, policy)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 2
        mem_second = MEMORY_CACHE.curr_mem - mem_first
        MEMORY_CACHE.info() == (1, 2, max_mem, MEMORY_CACHE.curr_mem, 2, policy)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 2
        assert MEMORY_CACHE.misses == 2
        assert MEMORY_CACHE.info() == (2, 2, max_mem, MEMORY_CACHE.curr_mem, 2, policy)

        # We rely on the first matrix being smaller than the second one.
        assert mem_second > mem_first

        # reduce max size so that the matrix specified by "evict" should be evicted.
        if adjust_to == "first":
            max_mem = mem_first + 10
        elif adjust_to == "second":
            max_mem = mem_second + 10
        else:
            raise ValueError(f"Invalid adjust_to value: {adjust_to}")

        config.set("maximum-matrix-memory-cache-size", max_mem)

        if evict == "first":
            assert MEMORY_CACHE.info() == (2, 2, max_mem, mem_second, 1, policy)
        elif evict == "second":
            assert MEMORY_CACHE.info() == (2, 2, max_mem, mem_first, 1, policy)
        else:
            raise ValueError(f"Invalid evict value: {evict}")


@pytest.mark.parametrize("policy", ["largest", "lru"])
def test_local_memcache_small(policy):
    """Test the cache with such a small memory limit that no matrix fits in"""
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    max_mem = 1
    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, max_mem, 0, 0, policy)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 1
        info = MEMORY_CACHE.info()
        assert info.hits == 0
        assert info.misses == 1
        assert info.maxsize == 1
        assert info.currsize == 0
        assert info.count == 0

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 2
        assert MEMORY_CACHE.info() == (0, 2, max_mem, 0, 0, policy)


def test_local_memcache_off_policy():
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    policy = "off"
    max_mem = 0

    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.info()

        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, 0, 0, 0, policy)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        info = MEMORY_CACHE.info()
        assert info.hits == 0
        assert info.misses == 0
        assert info.maxsize == 0
        assert info.currsize == 0
        assert info.count == 0

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == 0
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, 0, 0, 0, policy)


def test_local_memcache_unlimited():
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    policy = "unlimited"
    max_mem = None

    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.max_mem is None
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, None, 0, 0, policy)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem is None
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 1
        info = MEMORY_CACHE.info()
        assert info.hits == 0
        assert info.misses == 1
        assert info.maxsize is None
        assert info.currsize > 0
        assert info.count == 1

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem is None
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 1
        assert MEMORY_CACHE.info() == (1, 1, None, MEMORY_CACHE.curr_mem, 1, policy)


def test_local_memcache_ensure_strict_1(monkeypatch):
    """Test the cache with a memory limit that is too small to hold any estimated matrix size"""
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    policy = "largest"
    max_mem = 300 * 1024 * 1024

    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)
        config.set("matrix-memory-cache-strict-mode", True)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, max_mem, 0, 0, policy)

        def _estimate_memory(entry):
            return max_mem + 1

        from earthkit.regrid.utils import memcache

        monkeypatch.setattr(memcache, "estimate_matrix_size", _estimate_memory)

        with pytest.raises(ValueError) as excinfo:
            run_interpolate("linear")

        assert "Matrix too large" in str(excinfo.value)


def test_local_memcache_strict_2(monkeypatch):
    """Test the cache with a memory limit that can only hold one estimated matrix size"""
    from earthkit.regrid import config
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    policy = "largest"
    max_mem = 300 * 1024 * 1024

    with config.temporary():
        config.set("matrix-memory-cache-policy", policy)
        config.set("maximum-matrix-memory-cache-size", max_mem)
        config.set("matrix-memory-cache-strict-mode", True)

        MEMORY_CACHE.clear()

        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 0
        assert MEMORY_CACHE.info() == (0, 0, max_mem, 0, 0, policy)

        def _estimate_memory(entry):
            return max_mem - 1

        from earthkit.regrid.utils import memcache

        monkeypatch.setattr(memcache, "estimate_matrix_size", _estimate_memory)

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 0
        assert MEMORY_CACHE.misses == 1
        info = MEMORY_CACHE.info()
        assert info.hits == 0
        assert info.misses == 1
        assert info.maxsize == max_mem
        assert info.currsize > 0
        assert info.count == 1
        mem_first = info.currsize

        run_interpolate("linear")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 1
        assert MEMORY_CACHE.info() == (1, 1, max_mem, MEMORY_CACHE.curr_mem, 1, policy)

        # The first matrix should be evicted
        run_interpolate("nearest-neighbour")
        assert MEMORY_CACHE.max_mem == max_mem
        assert MEMORY_CACHE.hits == 1
        assert MEMORY_CACHE.misses == 2
        info = MEMORY_CACHE.info()
        assert info.currsize < mem_first
        assert MEMORY_CACHE.info() == (1, 2, max_mem, MEMORY_CACHE.curr_mem, 1, policy)

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
from earthkit.regrid.db import add_matrix_source

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "local", "db")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "local")


def file_in_testdir(filename):
    return os.path.join(DATA_PATH, filename)


def run_interpolate(mode):
    v_in = np.load(file_in_testdir("in_N32.npz"))["arr_0"]
    np.load(file_in_testdir(f"out_N32_10x10_{mode}.npz"))["arr_0"]
    interpolate(
        v_in,
        {"grid": "N32"},
        {"grid": [10, 10]},
        matrix_source=DB_PATH,
        method=mode,
    )


def test_local_index():
    DB = add_matrix_source(DB_PATH)
    # we have an extra unsupported entry in the index file. We have
    # to be sure the DB is loaded correctly bypassing the unsupported
    # entry.
    import json

    method = "linear"

    index_path = DB.index_file_path()
    with open(index_path, "r") as f:
        d = json.load(f)
        assert len(d["matrix"]) == 11

    assert len(DB) == 10

    # r = DB.find_entry({"grid": [5, 5]}, {"grid": [10, 10]}, method)
    # assert r

    r = DB.find_entry({"grid": "O32"}, {"grid": [10, 10]}, method)
    assert r

    r = DB.find_entry({"grid": "N32"}, {"grid": [10, 10]}, method)
    assert r

    r = DB.find_entry({"grid": "O64"}, {"grid": [10, 10]}, method)
    assert r is None


@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_local_ll_to_ll(method):
    v_in = np.load(file_in_testdir("in_5x5.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_5x5_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, matrix_source=DB_PATH, method=method
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_local_ogg_to_ll(method):
    v_in = np.load(file_in_testdir("in_O32.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_O32_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in, {"grid": "O32"}, {"grid": [10, 10]}, matrix_source=DB_PATH, method=method
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_local_ngg_to_ll(method):
    v_in = np.load(file_in_testdir("in_N32.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_N32_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in,
        {"grid": "N32"},
        {"grid": [10, 10]},
        matrix_source=DB_PATH,
        method=method,
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_local_healpix_ring_to_ll(method):
    v_in = np.load(file_in_testdir("in_H4_ring.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_H4_ring_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in,
        {"grid": "H4", "ordering": "ring"},
        {"grid": [10, 10]},
        matrix_source=DB_PATH,
        method=method,
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_local_healpix_nested_to_ll(method):
    v_in = np.load(file_in_testdir("in_H4_nested.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_H4_nested_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in,
        {"grid": "H4", "ordering": "nested"},
        {"grid": [10, 10]},
        matrix_source=DB_PATH,
        method=method,
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize(
    "gs_in, gs_out",
    [
        ({"grid": [5, 5]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90, 0, -90, 355]}, {"grid": [10, 10]}),
        ({"grid": [5, 5]}, {"grid": [10, 10], "area": [90, 0, -90, 360]}),
        ({"grid": [5, 5]}, {"grid": [10, 10], "area": [90, 0, -90, 350]}),
        (
            {"grid": [5, 5], "area": [90, 0, -90, 360]},
            {"grid": [10, 10], "area": [90, 0, -90, 360]},
        ),
        ({"grid": [5, 5], "shape": [37, 72]}, {"grid": [10, 10], "shape": [19, 36]}),
        ({"grid": [5, 5], "shape": [37, 72]}, {"grid": [10, 10]}),
        ({"grid": [5, 5]}, {"grid": [10, 10], "shape": [19, 36]}),
        ({"grid": "O32"}, {"grid": [10, 10]}),
        ({"grid": "O32", "shape": [5248]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [87.8638, 0, -87.8638, 357.5]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [87.8638, 0.01, -87.8638, 357.5]}, {"grid": [10, 10]}),
        ({"grid": "O32", "global": 1}, {"grid": [10, 10]}),
        (
            {"grid": "O32", "global": 1, "area": [87.8638, 0, -87.8638, 357.5]},
            {"grid": [10, 10]},
        ),
        ({"grid": "N32"}, {"grid": [10, 10]}),
        ({"grid": "N32", "shape": [6114]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [87.8638, 0, -87.8638, 357.188]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [87.8638, 0, -87.8638, 357.189]}, {"grid": [10, 10]}),
        (
            {"grid": "N32", "area": [87.8638, 0.01, -87.8638, 357.188]},
            {"grid": [10, 10]},
        ),
        (
            {"grid": "O32", "area": [87.8638, 0, -87.8638, 357.6]},
            {"grid": [10, 10]},
        ),
        ({"grid": "N32", "global": 1}, {"grid": [10, 10]}),
        (
            {"grid": "N32", "global": 1, "area": [87.8638, 0, -87.8638, 357.188]},
            {"grid": [10, 10]},
        ),
        ({"grid": "H4"}, {"grid": [10, 10]}),
        ({"grid": "H4", "ordering": "ring"}, {"grid": [10, 10]}),
    ],
)
def test_local_gridspec_ok(gs_in, gs_out):
    DB = add_matrix_source(DB_PATH)
    r = DB.find_entry(gs_in, gs_out, "linear")
    assert r, f"gs_in={gs_in} gs_out={gs_out}"


@pytest.mark.parametrize(
    "gs_in,gs_out,err",
    [
        ({"grid": [1, 1]}, {"grid": [2, 2]}, None),
        ({"grid": [5, 5], "area": [90, 0, -90, 350]}, {"grid": [10, 10]}, None),
        ({"grid": [5, 5], "area": [90.001, 0, -90, 360]}, {"grid": [10, 10]}, None),
        ({"grid": [5, 5], "area": [90, 0, -89.0001, 360]}, {"grid": [10, 10]}, None),
        ({"grid": [5, 5], "area": [90, 0.001, -90, 360]}, {"grid": [10, 10]}, None),
        ({"grid": [5, 5], "area": [90, 0, -90, 359.999]}, {"grid": [10, 10]}, None),
        ({"grid": [5, 5], "area": [90, 10, -90, 370]}, {"grid": [10, 10]}, None),
        ({"grid": "G1280", "shape": 6599680}, {"grid": [10, 10]}, ValueError),
        ({"grid": "O32", "shape": 6599680}, {"grid": [10, 10]}, None),
        ({"grid": "O32", "area": [90, 0, -90, 359.999]}, {"grid": [10, 10]}, None),
        ({"grid": "O32", "area": [90, -0.1, -90, 360]}, {"grid": [10, 10]}, None),
        (
            {"grid": "O32", "area": [87.8638, 0, -87.8638, 357.7]},
            {"grid": [10, 10]},
            None,
        ),
        (
            {"grid": "O32", "area": [87.8638, 0.2, -87.8638, 357.5]},
            {"grid": [10, 10]},
            None,
        ),
        ({"grid": "N32", "shape": 6599680}, {"grid": [10, 10]}, None),
        ({"grid": "N32", "area": [90, 0, -90, 359.999]}, {"grid": [10, 10]}, None),
        ({"grid": "N32", "area": [90, -0.1, -90, 360]}, {"grid": [10, 10]}, None),
        ({"grid": "H4", "ordering": "any"}, {"grid": [10, 10]}, ValueError),
    ],
)
def test_local_gridspec_bad(gs_in, gs_out, err):
    DB = add_matrix_source(DB_PATH)
    if err:
        with pytest.raises(err):
            r = DB.find_entry(gs_in, gs_out, "linear")
    else:
        r = DB.find_entry(gs_in, gs_out, "linear")
        assert r is None, f"gs_in={gs_in} gs_out={gs_out}"


def test_local_memcache_default():
    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    MEMORY_CACHE.clear()
    MEMORY_CACHE.update()

    assert MEMORY_CACHE.max_mem == 300 * 1024 * 1024
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 0
    assert MEMORY_CACHE.info() == (0, 0, 300 * 1024 * 1024, 0, 0)

    run_interpolate("linear")
    assert MEMORY_CACHE.max_mem == 300 * 1024 * 1024
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 1
    info = MEMORY_CACHE.info()
    assert info.hits == 0
    assert info.misses == 1
    assert info.maxsize == 300 * 1024 * 1024
    assert info.currsize > 0
    assert info.count == 1
    mem_linear = MEMORY_CACHE.curr_mem

    run_interpolate("linear")
    assert MEMORY_CACHE.max_mem == 300 * 1024 * 1024
    assert MEMORY_CACHE.hits == 1
    assert MEMORY_CACHE.misses == 1
    assert MEMORY_CACHE.info() == (1, 1, 300 * 1024 * 1024, mem_linear, 1)

    run_interpolate("nearest-neighbour")
    assert MEMORY_CACHE.max_mem == 300 * 1024 * 1024
    assert MEMORY_CACHE.hits == 1
    assert MEMORY_CACHE.misses == 2
    mem_nn = MEMORY_CACHE.curr_mem - mem_linear
    MEMORY_CACHE.info() == (1, 2, 300 * 1024 * 1024, MEMORY_CACHE.curr_mem, 2)

    run_interpolate("nearest-neighbour")
    assert MEMORY_CACHE.max_mem == 300 * 1024 * 1024
    assert MEMORY_CACHE.hits == 2
    assert MEMORY_CACHE.misses == 2
    assert MEMORY_CACHE.info() == (2, 2, 300 * 1024 * 1024, MEMORY_CACHE.curr_mem, 2)

    # reduce max size so that only the second matrix fits.
    # The first matrix should be evicted.
    from earthkit.regrid.utils.caching import SETTINGS

    max_mem = mem_nn + 10
    SETTINGS["maximum-matrix-memory-cache-size"] = max_mem

    MEMORY_CACHE.update()
    assert MEMORY_CACHE.info() == (2, 2, max_mem, mem_nn, 1)


def test_local_memcache_small():
    from earthkit.regrid.utils.caching import SETTINGS

    SETTINGS["maximum-matrix-memory-cache-size"] = 1

    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    MEMORY_CACHE.clear()
    MEMORY_CACHE.update()

    assert MEMORY_CACHE.max_mem == 1
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 0
    assert MEMORY_CACHE.info() == (0, 0, 1, 0, 0)

    run_interpolate("linear")
    assert MEMORY_CACHE.max_mem == 1
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 1
    info = MEMORY_CACHE.info()
    assert info.hits == 0
    assert info.misses == 1
    assert info.maxsize == 1
    assert info.currsize == 0
    assert info.count == 0

    run_interpolate("linear")
    assert MEMORY_CACHE.max_mem == 1
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 2
    assert MEMORY_CACHE.info() == (0, 2, 1, 0, 0)


def test_local_memcache_zero():
    from earthkit.regrid.utils.caching import SETTINGS

    SETTINGS["maximum-matrix-memory-cache-size"] = 0

    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    MEMORY_CACHE.clear()
    MEMORY_CACHE.update()

    assert MEMORY_CACHE.info()

    assert MEMORY_CACHE.max_mem == 0
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 0
    assert MEMORY_CACHE.info() == (0, 0, 0, 0, 0)

    run_interpolate("linear")
    assert MEMORY_CACHE.max_mem == 0
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
    assert MEMORY_CACHE.info() == (0, 0, 0, 0, 0)


def test_local_memcache_nolimit():
    from earthkit.regrid.utils.caching import SETTINGS

    SETTINGS["maximum-matrix-memory-cache-size"] = None

    from earthkit.regrid.utils.memcache import MEMORY_CACHE

    MEMORY_CACHE.clear()
    MEMORY_CACHE.update()

    assert MEMORY_CACHE.max_mem is None
    assert MEMORY_CACHE.hits == 0
    assert MEMORY_CACHE.misses == 0
    assert MEMORY_CACHE.info() == (0, 0, None, 0, 0)

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
    assert MEMORY_CACHE.info() == (1, 1, None, MEMORY_CACHE.curr_mem, 1)

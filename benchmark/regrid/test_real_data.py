# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os

import numpy as np
import pytest

from earthkit.regrid import regrid
from earthkit.regrid.utils.memcache import MEMORY_CACHE  # noqa: F401
from earthkit.regrid.utils.testing import ARRAY_BACKENDS
from earthkit.regrid.utils.testing import LOCAL_MATRIX_BACKEND_NAME
from earthkit.regrid.utils.testing import earthkit_test_data_path

DB_PATH = earthkit_test_data_path("local", "db")
DATA_PATH = earthkit_test_data_path("local")
INTERPOLATIONS = ["linear", "nearest-neighbour", "grid-box-average"]


def file_in_testdir(filename):
    return os.path.join(DATA_PATH, filename)


def run_regrid(v_in, in_grid, out_grid, interpolation):
    return regrid(
        v_in,
        in_grid,
        out_grid,
        interpolation=interpolation,
        backend=LOCAL_MATRIX_BACKEND_NAME,
        inventory_path=DB_PATH,
    )


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.benchmark(group="ll_to_ll: ", min_rounds=5, warmup=True)
def test_regrid_local_matrix_ll_to_ll(benchmark, interpolation, array_backend):
    v_in = array_backend.asarray(np.load(file_in_testdir("in_5x5.npz"))["arr_0"])
    v_ref = array_backend.asarray(np.load(file_in_testdir(f"out_5x5_10x10_{interpolation}.npz"))["arr_0"])
    out_grid = {"grid": [10, 10]}

    benchmark.group += f"{interpolation = } - {array_backend.name}"
    v_res, grid_res = benchmark(
        run_regrid, v_in=v_in, in_grid={"grid": [5, 5]}, out_grid=out_grid, interpolation=interpolation
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.benchmark(group="ogg_to_ll: ", min_rounds=5, warmup=True)
def test_regrid_local_matrix_ogg_to_ll(benchmark, interpolation, array_backend):
    v_in = array_backend.asarray(np.load(file_in_testdir("in_O32.npz"))["arr_0"])
    v_ref = array_backend.asarray(np.load(file_in_testdir(f"out_O32_10x10_{interpolation}.npz"))["arr_0"])
    out_grid = {"grid": [10, 10]}

    benchmark.group += f"{interpolation = } - {array_backend.name}"
    v_res, grid_res = benchmark(
        run_regrid, v_in=v_in, in_grid={"grid": "O32"}, out_grid=out_grid, interpolation=interpolation
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.benchmark(group="ngg_to_ll: ", min_rounds=5, warmup=True)
def test_regrid_local_matrix_ngg_to_ll(benchmark, interpolation, array_backend):
    v_in = array_backend.asarray(np.load(file_in_testdir("in_N32.npz"))["arr_0"])
    v_ref = array_backend.asarray(np.load(file_in_testdir(f"out_N32_10x10_{interpolation}.npz"))["arr_0"])
    out_grid = {"grid": [10, 10]}

    benchmark.group += f"{interpolation = } - {array_backend.name}"
    v_res, grid_res = benchmark(
        run_regrid, v_in=v_in, in_grid={"grid": "N32"}, out_grid=out_grid, interpolation=interpolation
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.benchmark(group="healpix_ring_to_ll: ", min_rounds=5, warmup=True)
def test_regrid_local_matrix_healpix_ring_to_ll(benchmark, interpolation, array_backend):
    v_in = array_backend.asarray(np.load(file_in_testdir("in_H4_ring.npz"))["arr_0"])
    v_ref = array_backend.asarray(np.load(file_in_testdir(f"out_H4_ring_10x10_{interpolation}.npz"))["arr_0"])
    out_grid = {"grid": [10, 10]}

    benchmark.group += f"{interpolation = } - {array_backend.name}"
    v_res, grid_res = benchmark(
        run_regrid,
        v_in=v_in,
        in_grid={"grid": "H4", "ordering": "ring"},
        out_grid=out_grid,
        interpolation=interpolation,
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.benchmark(group="healpix_nested_to_ll: ", min_rounds=5, warmup=True)
def test_regrid_local_matrix_nested_to_ll(benchmark, interpolation, array_backend):
    v_in = array_backend.asarray(np.load(file_in_testdir("in_H4_nested.npz"))["arr_0"])
    v_ref = array_backend.asarray(
        np.load(file_in_testdir(f"out_H4_nested_10x10_{interpolation}.npz"))["arr_0"]
    )
    out_grid = {"grid": [10, 10]}

    benchmark.group += f"{interpolation = } - {array_backend.name}"
    v_res, grid_res = benchmark(
        run_regrid,
        v_in=v_in,
        in_grid={"grid": "H4", "ordering": "nested"},
        out_grid=out_grid,
        interpolation=interpolation,
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)

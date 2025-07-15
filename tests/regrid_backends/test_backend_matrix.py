# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import numpy as np
import pytest

from earthkit.regrid import regrid
from earthkit.regrid.utils.testing import ARRAY_BACKENDS
from earthkit.regrid.utils.testing import SYSTEM_MATRIX_BACKEND_NAME
from earthkit.regrid.utils.testing import get_test_data

INTERPOLATIONS = ["linear", "nearest-neighbour"]


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.parametrize(
    "_kwarg,interpolation",
    [
        ({}, "linear"),
        ({"interpolation": "linear"}, "linear"),
        ({"interpolation": "nearest-neighbour"}, "nearest-neighbour"),
        ({"interpolation": "nn"}, "nearest-neighbour"),
        ({"interpolation": "nearest-neighbor"}, "nearest-neighbour"),
        # ({"interpolation": "grid-box-average"}, "grid-box-average"),
    ],
)
def test_regrid_matrix_interpolation_kwarg(_kwarg, interpolation, array_backend):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{interpolation}.npz"])

    v_in = array_backend.asarray(np.load(f_in)["arr_0"])
    v_ref = array_backend.asarray(np.load(f_out)["arr_0"])
    out_grid = {"grid": [10, 10]}
    v_res, grid_res = regrid(
        v_in, {"grid": "O32"}, out_grid=out_grid, backend=SYSTEM_MATRIX_BACKEND_NAME, **_kwarg
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


def _ll_to_ll(interpolation, array_backend):
    f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{interpolation}.npz"])

    v_in = array_backend.asarray(np.load(f_in)["arr_0"])
    v_ref = array_backend.asarray(np.load(f_out)["arr_0"])
    out_grid = {"grid": [10, 10]}
    v_res, res_grid = regrid(
        v_in,
        {"grid": [5, 5]},
        out_grid=out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
    )

    assert v_res.shape == (19, 36), 1
    assert res_grid == out_grid, 1
    assert array_backend.allclose(v_res.flatten(), v_ref), 1

    # repeated use
    v_res, grid_res = regrid(
        v_in,
        {"grid": [5, 5]},
        out_grid=out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
    )

    assert v_res.shape == (19, 36), 2
    assert grid_res == out_grid, 2
    assert array_backend.allclose(v_res.flatten(), v_ref), 2


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
def test_regrid_matrix_ll_to_ll(interpolation, array_backend):
    _ll_to_ll(interpolation, array_backend)


@pytest.mark.download
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
def test_regrid_matrix_ll_to_ll_user_cache(interpolation, array_backend):
    _ll_to_ll(interpolation, array_backend)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
def test_regrid_matrix_ogg_to_ll(interpolation, array_backend):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{interpolation}.npz"])

    v_in = array_backend.asarray(np.load(f_in)["arr_0"])
    v_ref = array_backend.asarray(np.load(f_out)["arr_0"])
    out_grid = {"grid": [10, 10]}
    v_res, grid_res = regrid(
        v_in,
        {"grid": "O32"},
        out_grid=out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
def test_regrid_matrix_ngg_to_ll(interpolation, array_backend):
    f_in, f_out = get_test_data(["in_N32.npz", f"out_N32_10x10_{interpolation}.npz"])

    v_in = array_backend.asarray(np.load(f_in)["arr_0"])
    v_ref = array_backend.asarray(np.load(f_out)["arr_0"])
    out_grid = {"grid": [10, 10]}
    v_res, grid_res = regrid(
        v_in,
        {"grid": "N32"},
        out_grid=out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
def test_regrid_matrix_healpix_ring_to_ll(interpolation, array_backend):
    f_in, f_out = get_test_data(["in_H4_ring.npz", f"out_H4_ring_10x10_{interpolation}.npz"])

    v_in = array_backend.asarray(np.load(f_in)["arr_0"])
    v_ref = array_backend.asarray(np.load(f_out)["arr_0"])
    out_grid = {"grid": [10, 10]}
    v_res, grid_res = regrid(
        v_in,
        {"grid": "H4", "ordering": "ring"},
        out_grid=out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
def test_regrid_matrix_healpix_nested_to_ll(interpolation, array_backend):
    f_in, f_out = get_test_data(["in_H4_nested.npz", f"out_H4_nested_10x10_{interpolation}.npz"])

    v_in = array_backend.asarray(np.load(f_in)["arr_0"])
    v_ref = array_backend.asarray(np.load(f_out)["arr_0"])
    out_grid = {"grid": [10, 10]}
    v_res, grid_res = regrid(
        v_in,
        {"grid": "H4", "ordering": "nested"},
        out_grid=out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
    )

    assert v_res.shape == (19, 36)
    assert grid_res == out_grid
    assert array_backend.allclose(v_res.flatten(), v_ref)


@pytest.mark.tmp_cache
def test_regrid_matrix_unsupported_input_grid() -> None:
    a = np.ones(91 * 180)
    with pytest.raises(ValueError):
        _ = regrid(
            a,
            {"grid": [2.2333424, 2]},
            {"grid": [1, 1]},
            interpolation="linear",
            backend=SYSTEM_MATRIX_BACKEND_NAME,
        )


@pytest.mark.tmp_cache
def test_regrid_matrix_unsupported_output_grid() -> None:
    a = np.ones(181 * 360)
    with pytest.raises(ValueError):
        _ = regrid(
            a,
            {"grid": [1.11323424, 1]},
            {"grid": [5, 5]},
            interpolation="linear",
            backend=SYSTEM_MATRIX_BACKEND_NAME,
        )

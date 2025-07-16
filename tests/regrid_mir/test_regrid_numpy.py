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
from earthkit.regrid.utils.testing import NO_MIR  # noqa: E402
from earthkit.regrid.utils.testing import compare_global_ll_results
from earthkit.regrid.utils.testing import get_test_data

BASE_INTERPOLATIONS = ["linear", "nearest-neighbour"]
INTERPOLATIONS = BASE_INTERPOLATIONS + ["grid-box-average"]


@pytest.mark.skipif(NO_MIR, reason="No mir available")
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
def test_regrid_numpy_kwarg(_kwarg, interpolation):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid(v_in, {"grid": "O32"}, {"grid": [10, 10]}, **_kwarg)

    assert v_res.shape == (19, 36), 1
    compare_global_ll_results(v_res, v_ref, interpolation, rtol=1e-4)


def _ll_to_ll(interpolation):
    f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1

    # repeated use
    v_res, _ = regrid(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_numpy_ll_to_ll(interpolation):
    _ll_to_ll(interpolation)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_numpy_ogg_to_ll_1(interpolation):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid(v_in, {"grid": "O32"}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36)
    compare_global_ll_results(v_res, v_ref, interpolation, rtol=1e-4)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("in_grid", ["O32", "o32"])
def test_regrid_numpy_ogg_to_ll_2(interpolation, in_grid):
    values_in = np.load(get_test_data("in_O32.npz"))["arr_0"]

    values, gridspec = regrid(
        values_in,
        {"grid": in_grid},
        {"grid": [30, 30]},
        interpolation=interpolation,
        output="values_gridspec",
    )

    assert values.shape == (7, 12)
    assert gridspec == dict(grid=[30, 30])


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_numpy_ngg_to_ll(interpolation):
    f_in, f_out = get_test_data(["in_N32.npz", f"out_N32_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid(v_in, {"grid": "N32"}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36)
    compare_global_ll_results(v_res, v_ref, interpolation)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
@pytest.mark.parametrize("in_grid", ["H4", "h4"])
def test_regrid_healpix_ring_to_ll(interpolation, in_grid):
    f_in, f_out = get_test_data(["in_H4_ring.npz", f"out_H4_ring_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid(
        v_in, {"grid": in_grid, "order": "ring"}, {"grid": [10, 10]}, interpolation=interpolation
    )

    assert v_res.shape == (19, 36)
    np.testing.assert_allclose(v_res.flatten(), v_ref, verbose=False)

    v_ref = v_ref.reshape(v_res.shape)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_healpix_nested_to_ll(interpolation):
    f_in, f_out = get_test_data(["in_H4_nested.npz", f"out_H4_nested_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid(
        v_in, {"grid": "H4", "order": "nested"}, {"grid": [10, 10]}, interpolation=interpolation
    )

    assert v_res.shape == (19, 36)
    v_ref = v_ref.reshape(v_res.shape)

    # print(v_res[0, :20] - v_ref[0, :20])
    # print(v_res[1, :20] - v_ref[1, :20])
    # print(v_res[2, :20] - v_ref[2, :20])

    np.testing.assert_allclose(v_res.flatten(), v_ref.flatten(), verbose=False)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.skipif(True, reason="No ORCA support for numpy in MIR")
@pytest.mark.parametrize("interpolation", ["linear"])
def test_regrid_orca_to_ogg(interpolation):
    f_in, f_out = get_test_data(
        ["in_eORCA025_T.npz", f"out_eORCA025_T_O96_{interpolation}.npz"], subfolder="local"
    )

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]

    out_grid = {"grid": "O96"}
    v_res, grid_res = regrid(
        v_in,
        {
            "grid": "eORCA025_T",
        },
        out_grid,
        interpolation=interpolation,
    )

    assert v_res.shape == (40320,)
    assert grid_res == out_grid
    np.testing.assert_allclose(v_res, v_ref, verbose=False)

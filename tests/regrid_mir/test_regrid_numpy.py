# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import numpy as np
import pytest

from earthkit.regrid.array import regrid as regrid_array
from earthkit.regrid.utils.testing import NO_MIR  # noqa: E402
from earthkit.regrid.utils.testing import compare_global_ll_results
from earthkit.regrid.utils.testing import get_test_data

BASE_INTERPOLATIONS = ["linear", "nearest-neighbour"]
INTERPOLATIONS = BASE_INTERPOLATIONS + ["grid-box-average"]


LATLON_REFS_FULL = [
    (0.05, (3601, 7200)),
    (0.1, (1801, 3600)),
    (0.125, (1441, 2880)),
    (0.15, (1201, 2400)),
    (0.2, (901, 1800)),
    (0.25, (721, 1440)),
    (0.3, (601, 1200)),
    (0.35, (517, 1024)),
    (0.4, (451, 900)),
    (0.5, (361, 720)),
    (0.6, (301, 600)),
    (0.7, (257, 515)),
    (0.8, (225, 450)),
    (0.9, (201, 400)),
    (1, (181, 360)),
    (1.2, (151, 300)),
    (1.25, (145, 288)),
    (1.4, (129, 258)),
    (1.5, (121, 240)),
    (1.6, (113, 225)),
    (1.8, (101, 200)),
    (2, (91, 180)),
    (2.5, (73, 144)),
    (5, (37, 72)),
    (10, (19, 36)),
]

LATLON_REFS = [
    (0.5, (361, 720)),
]

RED_GG_O_REFS = [
    ("O48", (10944,)),
    # ("O1280", (6599680,)),
]

RED_GG_N_REFS = [
    ("N48", (13280,)),
    # ("N320", (542080,)),
]

REG_GG_REFS = [
    ("F32", (64, 128)),
]

H_RING_REFS = [
    ("H4", (192,)),
]

H_NESTED_REFS = [
    ("H4", (192,)),
]

ORCA_REFS = [
    ("eORCA025_T", (1740494,)),
]


def make_refs():
    """Create references for the tests."""
    refs = []
    for res_dx, res_shape in LATLON_REFS:
        refs.append(({"grid": [res_dx, res_dx]}, res_shape))

    for out_grid, res_shape in RED_GG_O_REFS:
        refs.append(({"grid": out_grid}, res_shape))

    for out_grid, res_shape in RED_GG_N_REFS:
        refs.append(({"grid": out_grid}, res_shape))

    for out_grid, res_shape in REG_GG_REFS:
        refs.append(({"grid": out_grid}, res_shape))

    for out_grid, res_shape in H_RING_REFS:
        refs.append(({"grid": out_grid, "order": "ring"}, res_shape))

    for out_grid, res_shape in H_NESTED_REFS:
        refs.append(({"grid": out_grid, "order": "nested"}, res_shape))

    for out_grid, res_shape in ORCA_REFS:
        refs.append(({"grid": out_grid}, res_shape))

    return refs


REFS = make_refs()


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
    v_res, _ = regrid_array(v_in, {"grid": "O32"}, {"grid": [10, 10]}, **_kwarg)

    assert v_res.shape == (19, 36), 1
    compare_global_ll_results(v_res, v_ref, interpolation, rtol=1e-4)


def _ll_to_ll(interpolation):
    f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid_array(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1

    # repeated use
    v_res, _ = regrid_array(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_numpy_ll_to_ll_1(interpolation):
    _ll_to_ll(interpolation)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", ["linear"])
@pytest.mark.parametrize("res_dx,res_shape", LATLON_REFS_FULL)
def test_regrid_numpy_ll_to_ll_2(res_dx, res_shape, interpolation):

    values = np.random.random((37, 72))
    res_v, _ = regrid_array(
        values, in_grid={"grid": [5, 5]}, out_grid={"grid": [res_dx, res_dx]}, interpolation=interpolation
    )
    assert res_v.shape == res_shape


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_numpy_ogg_to_ll_1(interpolation):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid_array(v_in, {"grid": "O32"}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36)
    compare_global_ll_results(v_res, v_ref, interpolation, rtol=1e-4)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("in_grid", ["O32", "o32"])
def test_regrid_numpy_ogg_to_ll_2(interpolation, in_grid):
    values_in = np.load(get_test_data("in_O32.npz"))["arr_0"]

    values, gridspec = regrid_array(
        values_in,
        {"grid": in_grid},
        {"grid": [30, 30]},
        interpolation=interpolation,
    )

    assert values.shape == (7, 12)
    assert gridspec == dict(grid=[30, 30])


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize(
    "interpolation",
    [
        "linear",
        "nearest-neighbour",
        "grid-box-average",
        "grid-box-statistics",
        "nn",
        "bilinear",
        "k-nearest-neighbours",
    ],
)
def test_regrid_numpy_ogg_to_ll_interpolations(interpolation):
    # O32
    values = np.random.random(5248)
    res_v, _ = regrid_array(
        values, in_grid={"grid": "O32"}, out_grid={"grid": [10, 10]}, interpolation=interpolation
    )
    assert res_v.shape == (19, 36), f"{interpolation=} failed"


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
def test_regrid_numpy_ngg_to_ll(interpolation):
    f_in, f_out = get_test_data(["in_N32.npz", f"out_N32_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid_array(v_in, {"grid": "N32"}, {"grid": [10, 10]}, interpolation=interpolation)

    assert v_res.shape == (19, 36)
    compare_global_ll_results(v_res, v_ref, interpolation)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", BASE_INTERPOLATIONS)
@pytest.mark.parametrize("in_grid", ["H4", "h4"])
def test_regrid_healpix_ring_to_ll(interpolation, in_grid):
    f_in, f_out = get_test_data(["in_H4_ring.npz", f"out_H4_ring_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res, _ = regrid_array(
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
    v_res, _ = regrid_array(
        v_in, {"grid": "H4", "order": "nested"}, {"grid": [10, 10]}, interpolation=interpolation
    )

    assert v_res.shape == (19, 36)
    v_ref = v_ref.reshape(v_res.shape)

    # print(v_res[0, :20] - v_ref[0, :20])
    # print(v_res[1, :20] - v_ref[1, :20])
    # print(v_res[2, :20] - v_ref[2, :20])

    np.testing.assert_allclose(v_res.flatten(), v_ref.flatten(), verbose=False)


@pytest.mark.skipif(NO_MIR, reason="No mir available")
# @pytest.mark.skipif(True, reason="No ORCA support for numpy in MIR")
@pytest.mark.parametrize("interpolation", ["linear"])
def test_regrid_orca_to_ogg(interpolation):
    f_in = get_test_data("in_eORCA025_T.npz", subfolder="orca")
    f_out = get_test_data(f"out_eORCA025_T_O96_{interpolation}.npz", subfolder="local")

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]

    out_grid = {"grid": "O96"}
    v_res, grid_res = regrid_array(
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


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize("interpolation", ["linear"])
@pytest.mark.parametrize(
    "in_grid,in_shape",
    [
        ({"grid": [5, 5]}, (37, 72)),
        ({"grid": "O32"}, (5248,)),
        ({"grid": "N32"}, (6114,)),
        ({"grid": "F48"}, (96, 192)),
        ({"grid": "H8", "order": "ring"}, (768,)),
        ({"grid": "H8", "order": "nested"}, (768,)),
        ({"grid": "eORCA025_T"}, (1740494,)),
    ],
)
@pytest.mark.parametrize("out_grid,res_shape", REFS)
def test_regrid_numpy_any_to_any(interpolation, in_grid, in_shape, out_grid, res_shape):
    values = np.random.random(in_shape)
    res_v, _ = regrid_array(values, in_grid=in_grid, out_grid=out_grid, interpolation=interpolation)
    assert res_v.shape == res_shape, f"Expected shape {res_shape}, got {res_v.shape}"

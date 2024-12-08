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
METHODS = ["linear", "nearest-neighbour", "grid-box-average"]


def file_in_testdir(filename):
    return os.path.join(DATA_PATH, filename)


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
        assert len(d["matrix"]) == 17

    assert len(DB) == 16

    # r = DB.find_entry({"grid": [5, 5]}, {"grid": [10, 10]}, method)
    # assert r

    r = DB.find_entry({"grid": "O32"}, {"grid": [10, 10]}, method)
    assert r

    r = DB.find_entry({"grid": "N32"}, {"grid": [10, 10]}, method)
    assert r

    r = DB.find_entry({"grid": "O64"}, {"grid": [10, 10]}, method)
    assert r is None

    r = DB.find_entry({"grid": "eORCA025_T"}, {"grid": "O96"}, method)
    assert r


@pytest.mark.parametrize("method", METHODS)
def test_local_ll_to_ll(method):
    v_in = np.load(file_in_testdir("in_5x5.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_5x5_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, matrix_source=DB_PATH, method=method
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("method", METHODS)
def test_local_ogg_to_ll(method):
    v_in = np.load(file_in_testdir("in_O32.npz"))["arr_0"]
    v_ref = np.load(file_in_testdir(f"out_O32_10x10_{method}.npz"))["arr_0"]
    v_res = interpolate(
        v_in, {"grid": "O32"}, {"grid": [10, 10]}, matrix_source=DB_PATH, method=method
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize("method", METHODS)
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


@pytest.mark.parametrize("method", METHODS)
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


@pytest.mark.parametrize("method", METHODS)
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


# TODO: implement this test
# @pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
# def test_local_orca_to_ll(method):
#     v_in = np.load(file_in_testdir("in_eorca025_t.npz"))["arr_0"]
#     v_ref = np.load(file_in_testdir(f"out_eorca025_t_10x10_{method}.npz"))["arr_0"]
#     v_res = interpolate(
#         v_in,
#         {"grid": "eORCA025_T"},
#         {"grid": [10, 10]},
#         matrix_source=DB_PATH,
#         method=method,
#     )

#     assert v_res.shape == (19, 36)
#     assert np.allclose(v_res.flatten(), v_ref)


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
        ({"grid": "eORCA025_T"}, {"grid": "O96"}),
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
        ({"grid": "ORCA025_T"}, {"grid": "O96"}, ValueError),
        ({"grid": "eORCA025_U"}, {"grid": "O96"}, None),
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

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
from earthkit.regrid.db import DB, _use_local_index

PATH = os.path.join(os.path.dirname(__file__), "data", "local")

MATRIX_VERSION = "011801"


def file_in_testdir(filename):
    return os.path.join(PATH, filename)


def test_local_index():
    with _use_local_index(PATH):
        assert len(DB.index) == 3

        r = DB.find_entry({"grid": [5, 5]}, {"grid": [10, 10]})
        assert r

        r = DB.find_entry({"grid": "O32"}, {"grid": [10, 10]})
        assert r

        r = DB.find_entry({"grid": "N32"}, {"grid": [10, 10]})
        assert r

        r = DB.find_entry({"grid": "O64"}, {"grid": [10, 10]})
        assert not r


@pytest.mark.parametrize(
    "_kwargs", [({"matrix_version": MATRIX_VERSION}), ({"matrix_version": None}), ({})]
)
def test_local_ll_to_ll(_kwargs):
    with _use_local_index(PATH):
        v_in = np.load(file_in_testdir("in_5x5.npz"))["arr_0"]
        v_ref = np.load(file_in_testdir(f"out_5x5_10x10_{MATRIX_VERSION}.npz"))["arr_0"]
        v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, **_kwargs)

        assert v_res.shape == (19, 36)
        assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize(
    "_kwargs", [({"matrix_version": MATRIX_VERSION}), ({"matrix_version": None}), ({})]
)
def test_local_gg_to_ll_1(_kwargs):
    with _use_local_index(PATH):
        v_in = np.load(file_in_testdir("in_O32.npz"))["arr_0"]
        v_ref = np.load(file_in_testdir(f"out_O32_10x10_{MATRIX_VERSION}.npz"))["arr_0"]
        v_res = interpolate(v_in, {"grid": "O32"}, {"grid": [10, 10]}, **_kwargs)

        assert v_res.shape == (19, 36)
        assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.parametrize(
    "_kwargs", [({"matrix_version": MATRIX_VERSION}), ({"matrix_version": None}), ({})]
)
def test_local_gg_to_ll_2(_kwargs):
    with _use_local_index(PATH):
        v_in = np.load(file_in_testdir("in_N32.npz"))["arr_0"]
        v_ref = np.load(file_in_testdir(f"out_N32_10x10_{MATRIX_VERSION}.npz"))["arr_0"]
        v_res = interpolate(v_in, {"grid": "N32"}, {"grid": [10, 10]}, **_kwargs)

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
        ({"grid": "O32", "global": 1}, {"grid": [10, 10]}),
        (
            {"grid": "O32", "global": 1, "area": [87.8638, 0, -87.8638, 357.5]},
            {"grid": [10, 10]},
        ),
        ({"grid": "N32"}, {"grid": [10, 10]}),
        ({"grid": "N32", "shape": [6114]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [87.8638, 0, -87.8638, 357.188]}, {"grid": [10, 10]}),
        ({"grid": "N32", "global": 1}, {"grid": [10, 10]}),
        (
            {"grid": "N32", "global": 1, "area": [87.8638, 0, -87.8638, 357.188]},
            {"grid": [10, 10]},
        ),
    ],
)
def test_local_gridspec_ok(gs_in, gs_out):
    with _use_local_index(PATH):
        r = DB.find_entry(gs_in, gs_out)
        assert r, f"gs_in={gs_in} gs_out={gs_out}"


@pytest.mark.parametrize(
    "gs_in, gs_out",
    [
        ({"grid": [1, 1]}, {"grid": [2, 2]}),
        ({"grid": [5, 5], "area": [90, 0, -90, 350]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90.001, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90, 0, -89.0001, 360]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90, 0.001, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90, 0, -90, 359.999]}, {"grid": [10, 10]}),
        ({"grid": [5, 5], "area": [90, 10, -90, 370]}, {"grid": [10, 10]}),
        ({"grid": "G1280", "shape": 6599680}, {"grid": [10, 10]}),
        ({"grid": "O32", "shape": 6599680}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [90, 0, -90, 359.999]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [90, -0.1, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [87.8638, 0, -87.8638, 357.6]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [87.8638, 0.01, -87.8638, 357.5]}, {"grid": [10, 10]}),
        ({"grid": "N32", "shape": 6599680}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [90, 0, -90, 359.999]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [90, -0.1, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [87.8638, 0, -87.8638, 357.189]}, {"grid": [10, 10]}),
        (
            {"grid": "N32", "area": [87.8638, 0.01, -87.8638, 357.188]},
            {"grid": [10, 10]},
        ),
    ],
)
def test_local_gridspec_bad(gs_in, gs_out):
    with _use_local_index(PATH):
        r = DB.find_entry(gs_in, gs_out)
        assert not r, f"gs_in={gs_in} gs_out={gs_out}"

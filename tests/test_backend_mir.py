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

from earthkit.regrid import interpolate

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "local", "db")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "local")
METHODS = ["linear", "nearest-neighbour", "grid-box-average"]


def file_in_testdir(filename):
    return os.path.join(DATA_PATH, filename)


def get_local_db():
    from earthkit.regrid.backends.db import MatrixDb

    return MatrixDb.from_path(DB_PATH)


def run_interpolate(v_in, in_grid, out_grid, method):
    from earthkit.regrid import config

    with config.temporary(local_matrix_directories=DB_PATH, backends=["local-matrix"]):
        # v_in = np.load(file_in_testdir("in_N32.npz"))["arr_0"]
        # np.load(file_in_testdir(f"out_N32_10x10_{method}.npz"))["arr_0"]

        # in_grid = in_grid or {"grid": "N32"}
        # out_grid = out_grid or {"grid": [10, 10]}

        return interpolate(
            v_in,
            in_grid,
            out_grid,
            # matrix_source=DB_PATH,
            method=method,
        )


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
        ({"grid": [5, 5]}, {"grid": [10, 10]}),
        ({"grid": [5, 5]}, {"grid": [10, 10]}),
        ({"grid": [5, 5]}, {"grid": [10, 10]}),
        ({"grid": "O32"}, {"grid": [10, 10]}),
        ({"grid": "O32"}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [87.8638, 0, -87.8638, 357.5]}, {"grid": [10, 10]}),
        # ({"grid": "O32", "area": [87.8638, 0.01, -87.8638, 357.5]}, {"grid": [10, 10]}),
        ({"grid": "O32", "global": 1}, {"grid": [10, 10]}),
        (
            {"grid": "O32", "global": 1, "area": [87.8638, 0, -87.8638, 357.5]},
            {"grid": [10, 10]},
        ),
        ({"grid": "N32"}, {"grid": [10, 10]}),
        ({"grid": "N32"}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [87.8638, 0, -87.8638, 357.188]}, {"grid": [10, 10]}),
        ({"grid": "N32", "area": [87.8638, 0, -87.8638, 357.189]}, {"grid": [10, 10]}),
        # (
        #     {"grid": "N32", "area": [87.8638, 0.01, -87.8638, 357.188]},
        #     {"grid": [10, 10]},
        # ),
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
        # ---
        ({"grid": "H4", "ordering": "nested"}, {"grid": [10, 10]}),
    ],
)
def test_interpolate_with_mir(gs_in, gs_out):
    from mir import Grid

    in_grid = Grid(**gs_in)
    values = np.random.rand(in_grid.size())

    for method in METHODS:
        if gs_in["grid"] == "eORCA025_T" and method == "grid-box-average":
            continue

        result = interpolate(values, gs_in, gs_out, method="linear", backends=["mir"])

        result_grid = Grid(gs_out)  # NOTE: not necessarily true
        assert result.shape == result_grid.shape

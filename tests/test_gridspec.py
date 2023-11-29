# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import pytest

from earthkit.regrid.db import DB


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
def test_gridspec_ok(gs_in, gs_out):
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
def test_gridspec_bad(gs_in, gs_out):
    r = DB.find_entry(gs_in, gs_out)
    assert not r, f"gs_in={gs_in} gs_out={gs_out}"

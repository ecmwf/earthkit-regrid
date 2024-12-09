# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import pytest

from earthkit.regrid.db import SYS_DB


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
        ({"grid": "O32"}, {"grid": [0.1, 0.1]}),
        ({"grid": "O32"}, {"grid": [0.125, 0.125]}),
        ({"grid": "O32"}, {"grid": [0.15, 0.15]}),
        ({"grid": "O32"}, {"grid": [0.2, 0.2]}),
        ({"grid": "O32"}, {"grid": [0.25, 0.25]}),
        ({"grid": "O32"}, {"grid": [0.3, 0.3]}),
        ({"grid": "O32"}, {"grid": [0.4, 0.4]}),
        ({"grid": "O32"}, {"grid": [0.5, 0.5]}),
        ({"grid": "O32"}, {"grid": [0.6, 0.6]}),
        ({"grid": "O32"}, {"grid": [0.7, 0.7]}),
        ({"grid": "O32"}, {"grid": [0.75, 0.75]}),
        ({"grid": "O32"}, {"grid": [0.8, 0.8]}),
        ({"grid": "O32"}, {"grid": [0.9, 0.9]}),
        ({"grid": "O32"}, {"grid": [1, 1]}),
        ({"grid": "O32"}, {"grid": [1.2, 1.2]}),
        ({"grid": "O32"}, {"grid": [1.25, 1.25]}),
        ({"grid": "O32"}, {"grid": [1.4, 1.4]}),
        ({"grid": "O32"}, {"grid": [1.5, 1.5]}),
        ({"grid": "O32"}, {"grid": [1.6, 1.6]}),
        ({"grid": "O32"}, {"grid": [1.8, 1.8]}),
        ({"grid": "O32"}, {"grid": [2, 2]}),
        ({"grid": "O32"}, {"grid": [2.5, 2.5]}),
        ({"grid": "O32"}, {"grid": [5, 5]}),
        ({"grid": "O32"}, {"grid": [10, 10]}),
        ({"grid": "O32", "shape": [5248]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [90, 0, -90, 360]}, {"grid": [10, 10]}),
        ({"grid": "O32", "area": [87.8638, 0, -87.8638, 357.5]}, {"grid": [10, 10]}),
        (
            {"grid": "O32", "area": [87.8638, 0.01, -87.8638, 357.5]},
            {"grid": [10, 10]},
        ),
        (
            {"grid": "O32", "area": [87.8638, 0, -87.8638, 357.6]},
            {"grid": [10, 10]},
        ),
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
        ({"grid": "N32", "global": 1}, {"grid": [10, 10]}),
        (
            {"grid": "N32", "global": 1, "area": [87.8638, 0, -87.8638, 357.188]},
            {"grid": [10, 10]},
        ),
        ({"grid": "H128"}, {"grid": [1, 1]}),
        ({"grid": "H128", "ordering": "ring"}, {"grid": [1, 1]}),
        ({"grid": (5, 5)}, {"grid": (10, 10)}),
        ({"grid": "eORCA025_T"}, {"grid": "O96"}),
    ],
)
def test_gridspec_ok(gs_in, gs_out):
    r = SYS_DB.find_entry(gs_in, gs_out, "linear")
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
        ({"grid": "ORCA025_T"}, {"grid": "O96"}, ValueError),
        ({"grid": "eORCA025_U"}, {"grid": "O96"}, None),
    ],
)
def test_gridspec_bad(gs_in, gs_out, err):
    if err:
        with pytest.raises(err):
            r = SYS_DB.find_entry(gs_in, gs_out, "linear")
    else:
        r = SYS_DB.find_entry(gs_in, gs_out, "linear")
        assert r is None, f"gs_in={gs_in} gs_out={gs_out}"

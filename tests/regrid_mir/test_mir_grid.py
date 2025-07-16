# (C) Copyright 2025- ECMWF.
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

INTERPOLATIONS = ["linear", "nearest-neighbour", "grid-box-average"]


@pytest.mark.skipif(NO_MIR, reason="No mir available")
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
        ({"grid": "H4", "order": "ring"}, {"grid": [10, 10]}),
        # ({"grid": "eORCA025_T"}, {"grid": "O96"}),
        # ---
        ({"grid": "H4", "order": "nested"}, {"grid": [10, 10]}),
    ],
)
def test_regrid_with_mir_gridspec(gs_in, gs_out):
    from mir import Grid

    in_grid = Grid(**gs_in)
    values = np.random.rand(in_grid.size())

    for interpolation in INTERPOLATIONS:
        if gs_in["grid"] == "eORCA025_T" and interpolation == "grid-box-average":
            continue

        # TODO: make this code work
        values_res, _ = regrid(values, gs_in, gs_out, interpolation=interpolation)

        result_grid = Grid(gs_out)  # NOTE: not necessarily true
        assert values_res.shape == result_grid.shape

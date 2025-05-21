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
from earthkit.regrid.utils.testing import get_test_data

INTERPOLATIONS = ["linear", "nearest-neighbour", "grid-box-average"]


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
def test_regrid(interpolation):
    values_in = np.load(get_test_data("in_O32.npz"))["arr_0"]

    values, gridspec = regrid(
        values_in,
        {"grid": "O32"},
        {"grid": [30, 30]},
        interpolation=interpolation,
        output="values_gridspec",
    )

    assert values.shape == (7, 12)
    assert gridspec == dict(grid=[30, 30])


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
def test_regrid_grib(interpolation):
    from io import BytesIO
    from pathlib import Path

    from earthkit.regrid.backends import get_backend

    def check_header(contents):
        assert contents.startswith(b"GRIB") and contents.endswith(b"7777")

    with open(Path(__file__).parent / "o32.grib2", "rb") as fh:
        in_grib = BytesIO(fh.read())
        check_header(in_grib.getvalue())

    mir = get_backend("mir")
    out = mir.regrid_grib(in_grib, {"grid": [30, 30]}, interpolation=interpolation)

    assert out["gridType"] == "regular_ll"
    assert out.shape == (7, 12)

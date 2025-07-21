# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import pytest

from earthkit.regrid import regrid
from earthkit.regrid.utils.testing import NO_EKD  # noqa: E402
from earthkit.regrid.utils.testing import NO_MIR  # noqa: E402
from earthkit.regrid.utils.testing import earthkit_test_data_path

# INTERPOLATIONS = ["linear", "nearest-neighbour", "grid-box-average"]
INTERPOLATIONS = ["linear", "nearest-neighbour"]


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.skipif(NO_EKD, reason="No access to earthkit-data")
@pytest.mark.parametrize("input_format", ["BytesIO", "bytes"])
@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
def test_regrid_grib_message(input_format, interpolation):
    from io import BytesIO

    from earthkit.data.readers.grib.memory import GribFieldInMemory

    def check_header(contents):
        assert contents.startswith(b"GRIB") and contents.endswith(b"7777")

    with open(earthkit_test_data_path("o32.grib2"), "rb") as fh:
        in_grib = BytesIO(fh.read())
        check_header(in_grib.getvalue())
        if input_format == "bytes":
            in_grib = in_grib.getvalue()

    out = regrid(in_grib, out_grid={"grid": [30, 30]}, interpolation=interpolation)

    field = GribFieldInMemory.from_buffer(out)
    assert field.metadata("gridType") == "regular_ll"
    assert field.shape == (7, 12)

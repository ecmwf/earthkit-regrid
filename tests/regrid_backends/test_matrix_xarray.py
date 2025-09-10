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
from earthkit.regrid.utils.testing import compare_dims

if not NO_EKD:
    from earthkit.data import from_source  # noqa


@pytest.mark.skipif(NO_EKD, reason="No earthkit.data available")
@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize(
    "out_grid,dims",
    [
        ({"grid": [10, 10]}, {"step": 2, "latitude": 19, "longitude": 36}),
    ],
)
def test_regrid_matrix_xarray_from_ogg(out_grid, dims):

    ds_in = from_source("sample", "O32_t2.grib2")
    assert len(ds_in) == 2
    ds = ds_in.to_xarray()

    r = regrid(ds["2t"], grid=out_grid, interpolation="linear", backend="precomputed")

    compare_dims(r, dims, sizes=True)


@pytest.mark.skipif(NO_EKD, reason="No earthkit.data available")
@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.parametrize(
    "out_grid,dims",
    [
        ({"grid": [10, 10]}, {"step": 2, "latitude": 19, "longitude": 36}),
    ],
)
def test_regrid_matrix_xarray_from_h_nested(out_grid, dims):

    ds_in = from_source("sample", "H8_nested_t2.grib2")
    assert len(ds_in) == 2
    ds = ds_in.to_xarray()

    r = regrid(ds["2t"], grid=out_grid, interpolation="linear", backend="precomputed")

    compare_dims(r, dims, sizes=True)

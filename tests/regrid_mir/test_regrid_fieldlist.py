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
from earthkit.regrid.utils.testing import NO_EKD  # noqa: E402
from earthkit.regrid.utils.testing import NO_MIR  # noqa: E402
from earthkit.regrid.utils.testing import get_test_data  # noqa: E402
from earthkit.regrid.utils.testing import get_test_data_path  # noqa: E402

if not NO_EKD:
    from earthkit.data import from_source  # noqa


def _create_fieldlist(filename, field_type):
    ds = from_source("url", get_test_data_path(filename))
    if field_type == "array":
        return ds.to_fieldlist()
    elif field_type == "grib":
        return ds
    else:
        raise ValueError(f"Unknown field type: {field_type}")


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.skipif(NO_EKD, reason="No access to earthkit-data")
@pytest.mark.parametrize(
    "_kwarg,interpolation",
    [
        ({}, "linear"),
        ({"interpolation": "linear"}, "linear"),
        ({"interpolation": "nearest-neighbour"}, "nearest-neighbour"),
        ({"interpolation": "nn"}, "nearest-neighbour"),
        ({"interpolation": "nearest-neighbor"}, "nearest-neighbour"),
    ],
)
@pytest.mark.parametrize("field_type", ["grib", "array"])
def test_regrid_fieldlist_reg_ll(_kwarg, interpolation, field_type):
    ds = _create_fieldlist("5x5.grib", field_type)

    f_ref = get_test_data(f"out_5x5_10x10_{interpolation}.npz")
    v_ref = np.load(f_ref)["arr_0"]
    metadata_ref = ds.metadata(["param", "level", "date", "time", "gridType"])

    r = regrid(ds, out_grid={"grid": [10, 10]}, **_kwarg)

    assert len(r) == 1
    assert r[0].shape == (19, 36)
    assert np.allclose(r[0].values, v_ref)
    assert r.metadata(["param", "level", "date", "time", "gridType"]) == metadata_ref

    grid_ref = {"iDirectionIncrementInDegrees": 10.0, "jDirectionIncrementInDegrees": 10.0}
    for f in r:
        for k, v in grid_ref.items():
            assert np.isclose(f.metadata(k), v), k


@pytest.mark.skipif(NO_MIR, reason="No mir available")
@pytest.mark.skipif(NO_EKD, reason="No access to earthkit-data")
@pytest.mark.parametrize(
    "_kwarg,interpolation",
    [
        ({}, "linear"),
        ({"interpolation": "linear"}, "linear"),
        ({"interpolation": "nearest-neighbour"}, "nearest-neighbour"),
        ({"interpolation": "nn"}, "nearest-neighbour"),
        ({"interpolation": "nearest-neighbor"}, "nearest-neighbour"),
    ],
)
@pytest.mark.parametrize("field_type", ["grib", "array"])
def test_regrid_fieldlist_gg(_kwarg, interpolation, field_type):
    ds = _create_fieldlist("O32.grib", field_type)

    f_ref = get_test_data(f"out_O32_10x10_{interpolation}.npz")
    v_ref = np.load(f_ref)["arr_0"]
    metadata_ref = ds.metadata(["param", "level", "date", "time", "gridType"])

    r = regrid(ds, out_grid={"grid": [10, 10]}, **_kwarg)

    assert len(r) == 1
    assert r[0].shape == (19, 36)
    assert np.allclose(r[0].values, v_ref)
    assert r.metadata(["param", "level", "date", "time"]) == metadata_ref

    grid_ref = {"iDirectionIncrementInDegrees": 10.0, "jDirectionIncrementInDegrees": 10.0}
    for f in r:
        for k, v in grid_ref.items():
            assert np.isclose(f.metadata(k), v), k

    assert r.metadata("gridType") == ["regular_ll"]

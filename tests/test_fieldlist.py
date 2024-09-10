# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
import sys

import numpy as np
import pytest

from earthkit.regrid import interpolate

here = os.path.dirname(__file__)
sys.path.insert(0, here)
from testing import get_test_data  # noqa: E402
from testing import get_test_data_path  # noqa: E402

try:
    from earthkit.data import from_source  # noqa

    NO_EKD = False
except Exception:
    NO_EKD = True


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.skipif(NO_EKD, reason="No access to earthkit-data")
@pytest.mark.parametrize(
    "_kwarg,method",
    [
        ({}, "linear"),
        ({"method": "linear"}, "linear"),
        ({"method": "nearest-neighbour"}, "nearest-neighbour"),
        ({"method": "nn"}, "nearest-neighbour"),
        ({"method": "nearest-neighbor"}, "nearest-neighbour"),
    ],
)
def test_fieldlist_reg_ll(_kwarg, method):
    ds = from_source("url", get_test_data_path("5x5.grib"))

    f_ref = get_test_data(f"out_5x5_10x10_{method}.npz")
    v_ref = np.load(f_ref)["arr_0"]

    r = interpolate(ds, out_grid={"grid": [10, 10]}, **_kwarg)

    assert len(r) == 1
    assert r[0].shape == (19, 36)
    assert np.allclose(r[0].values, v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.skipif(NO_EKD, reason="No access to earthkit-data")
@pytest.mark.parametrize(
    "_kwarg,method",
    [
        ({}, "linear"),
        ({"method": "linear"}, "linear"),
        ({"method": "nearest-neighbour"}, "nearest-neighbour"),
        ({"method": "nn"}, "nearest-neighbour"),
        ({"method": "nearest-neighbor"}, "nearest-neighbour"),
    ],
)
def test_fieldlist_gg(_kwarg, method):
    ds = from_source("url", get_test_data_path("O32.grib"))

    f_ref = get_test_data(f"out_O32_10x10_{method}.npz")
    v_ref = np.load(f_ref)["arr_0"]

    r = interpolate(ds, out_grid={"grid": [10, 10]}, **_kwarg)

    assert len(r) == 1
    assert r[0].shape == (19, 36)
    assert np.allclose(r[0].values, v_ref)

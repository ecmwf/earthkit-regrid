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
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{interpolation}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = regrid(v_in, {"grid": "O32"}, {"grid": [10, 10]}, interpolation=interpolation, backends=["mir"])

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)

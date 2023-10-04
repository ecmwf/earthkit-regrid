# (C) Copyright 2023 ECMWF.
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

PATH = os.path.dirname(__file__)


def file_in_testdir(filename):
    return os.path.join(PATH, filename)


def test_regular_ll_1x1() -> None:
    a = np.ones(181 * 360)
    r = interpolate(a, {"grid": [1, 1]}, {"grid": [2, 2]})

    assert r.shape == (91, 180)
    assert np.isclose(r[0, 0], 1.0)


def test_o1280() -> None:
    a = np.ones(6599680)
    r = interpolate(a, {"grid": "O1280"}, {"grid": [2, 2]})

    assert r.shape == (91, 180)
    assert np.isclose(r[0, 0], 1.0)


def test_unsupported_input_grid() -> None:
    a = np.ones(91 * 180)
    with pytest.raises(ValueError):
        _ = interpolate(a, {"grid": [2, 2]}, {"grid": [1, 1]})


def test_unsupported_output_grid() -> None:
    a = np.ones(181 * 360)
    with pytest.raises(ValueError):
        _ = interpolate(a, {"grid": [1, 1]}, {"grid": [5, 5]})

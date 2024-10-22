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

METHODS = ["linear", "nearest-neighbour"]


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize(
    "_kwarg,method",
    [
        ({}, "linear"),
        ({"method": "linear"}, "linear"),
        ({"method": "nearest-neighbour"}, "nearest-neighbour"),
        ({"method": "nn"}, "nearest-neighbour"),
        ({"method": "nearest-neighbor"}, "nearest-neighbour"),
        # ({"method": "grid-box-average"}, "grid-box-average"),
    ],
)
def test_method_kwarg(_kwarg, method):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "O32"}, {"grid": [10, 10]}, **_kwarg)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1


def _ll_to_ll(method):
    f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, method=method)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1

    # repeated use
    v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, method=method)

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", METHODS)
def test_ll_to_ll(method):
    _ll_to_ll(method)


@pytest.mark.download
@pytest.mark.parametrize("method", METHODS)
def test_ll_to_ll_user_cache(method):
    _ll_to_ll(method)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", METHODS)
def test_ogg_to_ll(method):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "O32"}, {"grid": [10, 10]}, method=method)

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", METHODS)
def test_ngg_to_ll(method):
    f_in, f_out = get_test_data(["in_N32.npz", f"out_N32_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "N32"}, {"grid": [10, 10]}, method=method)

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", METHODS)
def test_healpix_ring_to_ll(method):
    f_in, f_out = get_test_data(["in_H4_ring.npz", f"out_H4_ring_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(
        v_in, {"grid": "H4", "ordering": "ring"}, {"grid": [10, 10]}, method=method
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", METHODS)
def test_healpix_nested_to_ll(method):
    f_in, f_out = get_test_data(
        ["in_H4_nested.npz", f"out_H4_nested_10x10_{method}.npz"]
    )

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(
        v_in, {"grid": "H4", "ordering": "nested"}, {"grid": [10, 10]}, method=method
    )

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.tmp_cache
def test_unsupported_input_grid() -> None:
    a = np.ones(91 * 180)
    with pytest.raises(ValueError):
        _ = interpolate(a, {"grid": [2.2333424, 2]}, {"grid": [1, 1]}, method="linear")


@pytest.mark.tmp_cache
def test_unsupported_output_grid() -> None:
    a = np.ones(181 * 360)
    with pytest.raises(ValueError):
        _ = interpolate(a, {"grid": [1.11323424, 1]}, {"grid": [5, 5]}, method="linear")

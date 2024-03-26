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

URL_ROOT = "https://get.ecmwf.int/repository/test-data/earthkit-regrid/test-data"


def simple_download(url, target):
    import requests

    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    open(target, "wb").write(r.content)


def get_test_data(filename, subfolder="global_0_360"):
    if not isinstance(filename, list):
        filename = [filename]

    res = []
    for fn in filename:
        d_path = os.path.join(PATH, "data", subfolder)
        os.makedirs(d_path, exist_ok=True)
        f_path = os.path.join(d_path, fn)
        if not os.path.exists(f_path):
            simple_download(url=f"{URL_ROOT}/{subfolder}/{fn}", target=f_path)
        res.append(f_path)

    if len(res) == 1:
        return res[0]
    else:
        return res


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
@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_ll_to_ll(method):
    _ll_to_ll(method)

    # f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{method}.npz"])

    # v_in = np.load(f_in)["arr_0"]
    # v_ref = np.load(f_out)["arr_0"]
    # v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, method=method)

    # assert v_res.shape == (19, 36), 1
    # assert np.allclose(v_res.flatten(), v_ref), 1

    # # repeated use
    # v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]}, method=method)

    # assert v_res.shape == (19, 36), 1
    # assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.download
@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_ll_to_ll_user_cache(method):
    _ll_to_ll(method)

    # f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{MATRIX_VERSION}.npz"])

    # v_in = np.load(f_in)["arr_0"]
    # v_ref = np.load(f_out)["arr_0"]
    # v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]})

    # assert v_res.shape == (19, 36), 1
    # assert np.allclose(v_res.flatten(), v_ref), 1

    # # repeated use
    # v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]})

    # assert v_res.shape == (19, 36), 1
    # assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_ogg_to_ll(method):
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "O32"}, {"grid": [10, 10]}, method=method)

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
def test_ngg_to_ll(method):
    f_in, f_out = get_test_data(["in_N32.npz", f"out_N32_10x10_{method}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "N32"}, {"grid": [10, 10]}, method=method)

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
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
@pytest.mark.parametrize("method", ["linear", "nearest-neighbour"])
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

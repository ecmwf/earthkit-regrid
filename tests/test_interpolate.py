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

MATRIX_VERSION = "011801"


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
def test_ll_to_ll():
    f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{MATRIX_VERSION}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]})

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1

    # repeated use
    v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]})

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.download
def test_ll_to_ll_user_cache():
    f_in, f_out = get_test_data(["in_5x5.npz", f"out_5x5_10x10_{MATRIX_VERSION}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]})

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1

    # repeated use
    v_res = interpolate(v_in, {"grid": [5, 5]}, {"grid": [10, 10]})

    assert v_res.shape == (19, 36), 1
    assert np.allclose(v_res.flatten(), v_ref), 1


@pytest.mark.download
@pytest.mark.tmp_cache
def test_gg_to_ll_1():
    f_in, f_out = get_test_data(["in_O32.npz", f"out_O32_10x10_{MATRIX_VERSION}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "O32"}, {"grid": [10, 10]})

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.download
@pytest.mark.tmp_cache
def test_gg_to_ll_2():
    f_in, f_out = get_test_data(["in_N32.npz", f"out_N32_10x10_{MATRIX_VERSION}.npz"])

    v_in = np.load(f_in)["arr_0"]
    v_ref = np.load(f_out)["arr_0"]
    v_res = interpolate(v_in, {"grid": "N32"}, {"grid": [10, 10]})

    assert v_res.shape == (19, 36)
    assert np.allclose(v_res.flatten(), v_ref)


@pytest.mark.tmp_cache
def test_unsupported_input_grid() -> None:
    a = np.ones(91 * 180)
    with pytest.raises(ValueError):
        _ = interpolate(a, {"grid": [2.2333424, 2]}, {"grid": [1, 1]})


@pytest.mark.tmp_cache
def test_unsupported_output_grid() -> None:
    a = np.ones(181 * 360)
    with pytest.raises(ValueError):
        _ = interpolate(a, {"grid": [1.11323424, 1]}, {"grid": [5, 5]})

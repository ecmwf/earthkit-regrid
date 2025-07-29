# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
from importlib import import_module

from earthkit.utils.testing import get_array_backend

PATH = os.path.dirname(__file__)

URL_ROOT = "https://get.ecmwf.int/repository/test-data/earthkit-regrid/test-data"

_ROOT_DIR = top = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
if not os.path.exists(os.path.join(_ROOT_DIR, "tests", "data")):
    _ROOT_DIR = "./"


ARRAY_BACKENDS = get_array_backend(["numpy", "torch", "cupy"], raise_on_missing=False)


def earthkit_file(*args):
    return os.path.join(_ROOT_DIR, *args)


def earthkit_test_data_path(*args):
    return os.path.join(_ROOT_DIR, "tests", "data", *args)


def simple_download(url, target):
    import requests

    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    open(target, "wb").write(r.content)


def get_test_data_path(filename, subfolder="global_0_360"):
    return os.path.join(URL_ROOT, subfolder, filename)


def get_test_data(filename, subfolder="global_0_360"):
    if not isinstance(filename, list):
        filename = [filename]

    res = []
    for fn in filename:
        d_path = earthkit_test_data_path(subfolder)
        os.makedirs(d_path, exist_ok=True)
        f_path = os.path.join(d_path, fn)
        if not os.path.exists(f_path):
            simple_download(url=f"{URL_ROOT}/{subfolder}/{fn}", target=f_path)
        res.append(f_path)

    if len(res) == 1:
        return res[0]
    else:
        return res


def modules_installed(*modules):
    for module in modules:
        try:
            import_module(module)
        except ImportError as e:
            print(f"earthkit-regrid testing: {module=} is not installed: {e}")
            return False
    return True


NO_EKD = not modules_installed("earthkit.data")

try:
    NO_MIR = not modules_installed("mir")
except Exception:
    NO_MIR = True

# TODO: remove these constants when the backend names are finalized
LOCAL_MATRIX_BACKEND_NAME = "precomputed-local"
SYSTEM_MATRIX_BACKEND_NAME = "precomputed"
REMOTE_MATRIX_BACKEND_NAME = "precomputed-remote"


def compare_global_ll_results(v_res, v_ref, interpolation, **kwargs):
    """
    Compare the results of the regrid operation with the reference values.
    """
    import numpy as np

    if interpolation in ("nearest-neighbour", "nn", "nearest-neighbor"):
        v_ref = v_ref.reshape(v_res.shape)

        np.testing.assert_allclose(v_res[0].flatten(), v_ref[0].flatten(), rtol=10, verbose=False)
        np.testing.assert_allclose(v_res[-1].flatten(), v_ref[0].flatten(), rtol=10, verbose=False)
        np.testing.assert_allclose(v_res[1:-1].flatten(), v_ref[1:-1].flatten(), verbose=False, **kwargs)
    else:
        np.testing.assert_allclose(v_res.flatten(), v_ref.flatten(), verbose=False, **kwargs)

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
from importlib import import_module

import numpy as np

PATH = os.path.dirname(__file__)

URL_ROOT = "https://get.ecmwf.int/repository/test-data/earthkit-regrid/test-data"

_ROOT_DIR = top = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)
if not os.path.exists(os.path.join(_ROOT_DIR, "tests", "data")):
    _ROOT_DIR = "./"


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


def compare_dims(ds, ref_coords, order_ref_var=None, sizes=False):
    compare_dim_order(ds, ref_coords, order_ref_var=order_ref_var)
    if not sizes:
        for k, v in ref_coords.items():
            compare_coord(ds, k, v, mode="dim")
    else:
        compare_dim_size(ds, ref_coords)


def compare_coords(ds, ref_coords):
    for k, v in ref_coords.items():
        compare_coord(ds, k, v, mode="coord")


def compare_coord(ds, name, ref_vals, mode="coord"):
    assert name in ds.coords, f"{name=} not in {ds.coords}"
    if mode == "dim":
        assert name in ds.sizes, f"{name=} not in {ds.sizes}"
        assert ds.sizes[name] == len(ref_vals), f"{name=} {ds.sizes[name]} != {len(ref_vals)}"

    vals = ds.coords[name].values
    if isinstance(ref_vals[0], str):
        assert vals.tolist() == ref_vals, f"{name=} {vals.tolist()} != {ref_vals}"
    else:
        vals = np.asarray(vals).flatten()
        ref_vals = np.asarray(ref_vals).flatten()

        assert vals.shape == ref_vals.shape, f"{name=} {vals.shape} != {ref_vals.shape}"
        # datetime/timedelta 64
        if np.issubdtype(vals.dtype, np.datetime64) or np.issubdtype(vals.dtype, np.timedelta64):
            for i in range(len(ref_vals)):
                assert vals[i] == ref_vals[i], f"{name=} {vals[i]} != {ref_vals[i]}"
        # other arrays
        else:
            assert np.allclose(ds.coords[name].values, vals), f"{name=} {ds.coords[name].values} != {vals}"


def compare_dim_order(ds, dims, order_ref_var, check_coord=True):
    if order_ref_var is None:
        return

    dim_order = []

    for d in ds[order_ref_var].dims:
        if d in dims:
            dim_order.append(d)
            if check_coord:
                assert d in ds.coords, f"{d} not in {ds.coords}"

    if isinstance(dims, dict):
        assert dim_order == list(dims.keys()), f"{dim_order=} != {list(dims.keys())}"
    else:
        assert dim_order == dims, f"{dim_order=} != {dims}"


def compare_dim_size(ds, dims):
    for name, v in dims.items():
        assert name in ds.sizes, f"{name=} not in {ds.sizes}"
        assert ds.sizes[name] == v, f"{name=} {ds.sizes[name]} != {v}"

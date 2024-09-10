# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os

PATH = os.path.dirname(__file__)

URL_ROOT = "https://get.ecmwf.int/repository/test-data/earthkit-regrid/test-data"


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

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import sys

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(here))

from utils.matrix import make_matrix  # noqa

logging.basicConfig(level=logging.DEBUG)

grids = [
    ["5/5", "10/10"],
    ["N32", "10/10"],
    ["O32", "10/10"],
    ["H4_ring", "10/10"],
    ["H4_nested", "10/10"],
]


# methods = ["linear", "nearest-neighbour"]
methods = ["grid-box-average"]
build_dir = "_test_local_data_20241021"

index_file = os.path.join(build_dir, "index.json")

for method in methods:
    for g_in, g_out in grids:
        make_matrix(
            g_in,
            g_out,
            method,
            build_dir,
            index_file=index_file,
            download_index=False,
            delete_tmp_json=True,
        )

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import glob
import logging
import os
import shutil
import sys

import numpy as np

import earthkit.regrid

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(here))

logging.basicConfig(level=logging.DEBUG)

"""
FOR MAINTENANCE ONLY!!!
-----------------------

This script generates and runs tests for newly built (partial) matrix inventory.
"""

build_root_dir = "_build_20240808"
db_dir = os.path.join(build_root_dir, "db")
index_file = os.path.join(build_root_dir, "index", "index.json")
test_dir = os.path.join(build_root_dir, "test")

methods = ["linear", "nearest-neighbour"]
build_matrix_dirs = ["matrices_linear", "matrices_nn"]


def build_test_dir():
    # the target dir must not exist
    os.makedirs(test_dir, exist_ok=True)

    # copy matrices
    for m_dir in build_matrix_dirs:
        m_dir = os.path.join(db_dir, m_dir)
        for d in glob.glob(m_dir + "/*"):
            if os.path.isdir(d):
                name = os.path.basename(d)
                d_target = os.path.join(test_dir, name)
                os.symlink(os.path.abspath(d), d_target)
                # os.symlink(os.path.abspath(d), os.path.abspath(d_target)

    # copy index file
    shutil.copy(index_file, os.path.join(test_dir, "index.json"))


if not os.path.exists(test_dir):
    build_test_dir()

# TODO: make the tests automatic
gs_in = {"grid": "N256"}
gs_out = {"grid": "O400"}
for method in methods:
    v = np.ones(348528)
    r = earthkit.regrid.interpolate(
        v, gs_in, gs_out, matrix_source=test_dir, method=method
    )
    assert len(r) == 654400

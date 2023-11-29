# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os

in_grids = ["5/5", "O32", "N32"]
out_grids = ["10/10"]
matrix_dir = "local_matrices"

for g_in in in_grids:
    for g_out in out_grids:
        if g_in != g_out:
            cmd = f"zsh ./make-matrix.sh {g_in} {g_out} {matrix_dir}"
            os.system(cmd)

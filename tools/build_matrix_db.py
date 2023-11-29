# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os

gg_res = [1280, 1024, 640, 512, 400, 320, 256, 200, 160, 128, 96, 80, 64, 48, 32]

in_grids_ll = []
in_grids_O_gg = [2560] + gg_res
in_grids_N_gg = gg_res
out_grids_ll = [
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.75,
    0.8,
    0.9,
    1,
    1.2,
    1.25,
    1.4,
    1.5,
    1.6,
    1.8,
    2,
    2.5,
    5,
    10,
]


matrix_dir = "matrices"


# define input grids
in_grids = []
for g in in_grids_ll:
    in_grids.append(f"{g}/{g}")

for g in in_grids_O_gg:
    in_grids.append(f"O{g}")

for g in in_grids_N_gg:
    in_grids.append(f"N{g}")

# define output grids
out_grids = []
for g in out_grids_ll:
    out_grids.append(f"{g}/{g}")

for g_in in in_grids:
    for g_out in out_grids:
        if g_in != g_out:
            cmd = f"zsh ./make-matrix.sh {g_in} {g_out} {matrix_dir}"
            os.system(cmd)


# for testing
out_grids = ["10/10"]
in_grids = ["5/5"]

for g_in in in_grids:
    for g_out in out_grids:
        if g_in != g_out:
            cmd = f"zsh ./make-matrix.sh {g_in} {g_out} {matrix_dir}"
            os.system(cmd)

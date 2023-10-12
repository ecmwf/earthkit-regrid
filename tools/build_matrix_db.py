import os
import sys

# import earthkit.data
# import earthkit.regrid

in_grids_ll = [
    0.1, 0.5, 1, 5
]

#in_grids_O_gg = [2000, 1280, 1024, 640, 512, 400, 320, 256, 200, 160, 128, 96, 80, 64, 48]
#in_grids_N_gg = [2000, 1280, 1024, 640, 512, 400, 320, 256, 200, 160, 128, 96, 80, 64, 48]

in_grids_O_gg = [2000, 1280, 1024, 640, 512, 32]
in_grids_N_gg = [2000, 1280, 1024, 640, 512, 32]
out_grids_ll = [0.1, 0.5, 1, 5, 10]

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

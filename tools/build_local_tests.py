import os

in_grids = ["5/5", "O32", "N32"]
out_grids = ["10/10"]
matrix_dir = "local_matrices"

for g_in in in_grids:
    for g_out in out_grids:
        if g_in != g_out:
            cmd = f"zsh ./make-matrix.sh {g_in} {g_out} {matrix_dir}"
            os.system(cmd)

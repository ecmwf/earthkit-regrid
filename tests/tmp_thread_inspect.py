from earthkit.regrid import regrid


grids = [
    ({"grid": "H4", "order": "nested"}, {"grid": [10, 10]}),
    ({"grid": "h4", "order": "nested"}, {"grid": [10, 10]}),
]


def run_example(in_grid, out_grid):
    import numpy as np

    values = np.random.rand(192)

    # TODO: make this code work
    values_res, _ = regrid(values, in_grid, out_grid, interpolation="linear")


def __main__():
    for gs_in, gs_out in grids:
        print(f"Regridding from {gs_in} to {gs_out}")
        run_example(gs_in, gs_out)


if __name__ == "__main__":
    __main__()

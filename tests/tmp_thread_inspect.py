# from earthkit.regrid import regrid

# grids = [
#     ({"grid": "H4", "order": "nested"}, {"grid": [10, 10]}),
#     ({"grid": "h4", "order": "nested"}, {"grid": [10, 10]}),
# ]


# def run_example(in_grid, out_grid):
#     import numpy as np

#     values = np.random.rand(192)

#     # TODO: make this code work
#     values_res, _ = regrid(values, in_grid, out_grid, interpolation="linear")


# def __main__():
#     for gs_in, gs_out in grids:
#         print(f"Regridding from {gs_in} to {gs_out}")
#         run_example(gs_in, gs_out)


def __main__():
    import mir
    import numpy as np

    values = np.random.rand(192)

    in_grid = {"grid": "H4", "order": "nested"}
    out_grid = {"grid": [10, 10]}

    input = mir.ArrayInput(values, in_grid)
    out = mir.ArrayOutput()

    job = mir.Job()
    job.set("grid", out_grid)
    job.set("interpolation", "linear")
    job.execute(input, out)

    assert out.values()
    assert out.spec


if __name__ == "__main__":
    __main__()

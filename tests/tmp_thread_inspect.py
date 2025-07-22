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

    print("1", flush=True)
    values = np.random.rand(192)

    print("2", flush=True)
    in_grid = {"grid": "H4", "order": "nested"}
    out_grid = {"grid": [10, 10]}

    print("3", flush=True)
    input = mir.ArrayInput(values, in_grid)

    print("4", flush=True)
    out = mir.ArrayOutput()

    print("5", flush=True)
    job = mir.Job()
    job.set("grid", out_grid)
    job.set("interpolation", "linear")

    print("6", flush=True)
    job.execute(input, out)

    print("7", flush=True)
    assert len(out.values())
    assert out.spec

    print("8", flush=True)


if __name__ == "__main__":
    __main__()

def __main__():
    import mir
    import numpy as np

    print("1", flush=True)
    values = np.random.rand(192)
    values = np.random.rand(37, 72)

    print("2", flush=True)
    in_grid = {"grid": "H4", "order": "nested"}
    in_grid = {"grid": [5, 5]}
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

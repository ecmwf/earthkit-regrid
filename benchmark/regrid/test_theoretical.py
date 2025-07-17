# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


import numpy as np
import pytest

from earthkit.regrid import regrid
from earthkit.regrid.utils.memcache import MEMORY_CACHE  # noqa: F401
from earthkit.regrid.utils.testing import ARRAY_BACKENDS
from earthkit.regrid.utils.testing import SYSTEM_MATRIX_BACKEND_NAME
from earthkit.regrid.utils.testing import earthkit_test_data_path

DB_PATH = earthkit_test_data_path("local", "db")
DATA_PATH = earthkit_test_data_path("local")
INTERPOLATIONS = ["linear", "nearest-neighbour"]

IN_GRIDS = [
    # ({"grid": "O2560"}, (26306560,)),
    ({"grid": "O1280"}, (6599680,)),
    ({"grid": "N320"}, (542080,)),
]

OUT_GRIDS = [
    # {"grid": "O48"},
    {"grid": [0.25, 0.25]},
    {"grid": [0.5, 0.5]},
    {"grid": [0.1, 0.1]},
]


def run_regrid(v_in, in_grid, out_grid, interpolation):
    return regrid(
        v_in,
        in_grid,
        out_grid,
        interpolation=interpolation,
        backend=SYSTEM_MATRIX_BACKEND_NAME,
        # inventory_path=DB_PATH,
    )


@pytest.mark.parametrize("interpolation", INTERPOLATIONS)
@pytest.mark.parametrize("array_backend", ARRAY_BACKENDS)
@pytest.mark.parametrize("in_grid", IN_GRIDS)
@pytest.mark.parametrize("out_grid", OUT_GRIDS)
@pytest.mark.benchmark(group="", min_rounds=5, warmup=True)
def test_regrid(
    benchmark, interpolation, array_backend, in_grid: tuple[dict, tuple[int, ...]], out_grid: dict
):

    fake_input = np.random.rand(*in_grid[1])
    v_in = array_backend.asarray(fake_input)

    benchmark.group = f"{interpolation = } - {array_backend.name}: {in_grid = } -> {out_grid = }"
    benchmark(run_regrid, v_in=v_in, in_grid=in_grid[0], out_grid=out_grid, interpolation=interpolation)

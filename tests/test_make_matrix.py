# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from pathlib import Path

import pytest
from scipy.sparse import load_npz

from earthkit.regrid.utils.mir import mir_make_another_matrix

L1 = [1.0, 2.0, 3.0, 4.0]
L2 = [1.1, 1.9, 3.1, 3.9]


@pytest.mark.skip(reason="This test is disabled until further integration.")
@pytest.mark.parametrize(
    "input_grid, output_grid, interpolation, shape",
    [
        (dict(grid="1/1"), dict(grid="H2", ordering="nested"), "nn", (48, 360 * 181)),
        (dict(grid=[2, 2]), dict(grid="o2"), "linear", (88, 180 * 91)),
        (
            dict(grid=[3, 3]),
            dict(grid="3/3"),
            "linear",
            (120 * 61, 120 * 61),
        ),  # identity
        (dict(grid=[1, 1]), dict(grid="H2", ordering="nested"), "nn", (48, 360 * 181)),
        (dict(grid="2/2"), dict(grid="o2"), "linear", (88, 180 * 91)),
        (
            dict(grid="3/3"),
            dict(grid=[3, 3]),
            "linear",
            (120 * 61, 120 * 61),
        ),  # identity
    ],
)
def test_make_matrix(tmp_path, input_grid, output_grid, interpolation, shape):
    mat = Path(tmp_path) / "matrix.npz"

    mir_make_another_matrix(
        in_grid=input_grid,
        out_grid=output_grid,
        output=mat,
        interpolation=interpolation,
    )

    assert mat.exists()
    array = load_npz(mat)
    assert array.shape == shape
    mat.unlink()


@pytest.mark.skip(reason="This test is disabled until further integration.")
def test_make_matrix_unstructured_to_gridspec(tmp_path):
    mat = Path(tmp_path) / "matrix.npz"

    mir_make_another_matrix(
        in_lat=L1,
        in_lon=L2,
        out_grid=dict(grid="h2"),
        output=mat,
        interpolation="nn",
    )

    assert mat.exists()
    array = load_npz(mat)
    assert array.shape == (48, 4)
    mat.unlink()


@pytest.mark.skip(reason="This test is disabled until further integration.")
def test_make_matrix_gridspec_to_unstructured(tmp_path):
    mat = Path(tmp_path) / "matrix.npz"

    mir_make_another_matrix(
        in_grid=dict(grid="h2"),
        out_lat=L2,
        out_lon=L1,
        output=mat,
        interpolation="nn",
    )

    assert mat.exists()
    array = load_npz(mat)
    assert array.shape == (4, 48)
    mat.unlink()


@pytest.mark.skip(reason="This test is disabled until further integration.")
def test_make_matrix_unstructured_to_unstructured(tmp_path):
    mat = Path(tmp_path) / "matrix.npz"

    mir_make_another_matrix(
        in_lat=L1,
        in_lon=L2,
        out_lat=L2,
        out_lon=L1,
        output=mat,
        interpolation="nn",
    )

    assert mat.exists()
    array = load_npz(mat)
    assert array.shape == (4, 4)
    mat.unlink()


if __name__ == "__main__":
    pytest.main([__file__])

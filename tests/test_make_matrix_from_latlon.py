# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from pathlib import Path

import pytest

from earthkit.regrid.utils.mir import mir_cached_matrix_to_array
from earthkit.regrid.utils.mir import mir_make_matrix

X = [1.0, 2.0, 3.0, 4.0]
Y = [10.0, 20.0, 30.0, 40.0]
Z = [5.0]


@pytest.mark.skip(reason="This test is disabled until further integration.")
@pytest.mark.parametrize(
    "in_lat, in_lon, out_lat, out_lon",
    [
        (X, X, X + Z, Y + Z),
        (X, X, Y + Z, X + Z),
        (X, X, Y + Z, Y + Z),
        (X, Y, X + Z, X + Z),
        (X, Y, Y + Z, X + Z),
        (X, Y, Y + Z, Y + Z),
        (Y + Z, X + Z, X, X),
        (Y + Z, X + Z, X, Y),
        (Y + Z, X + Z, Y, Y),
        (Y + Z, Y + Z, X, X),
        (Y + Z, Y + Z, X, Y),
        (Y + Z, Y + Z, Y, X),
    ],
)
def test_make_matrix_from_latlon(tmp_path, in_lat, in_lon, out_lat, out_lon):
    matrix_path = Path(tmp_path) / "matrix.mat"

    mir_make_matrix(
        in_lat,
        in_lon,
        out_lat,
        out_lon,
        matrix_path,
        mir="mir",
        interpolation="nn",
    )
    assert matrix_path.exists()

    array = mir_cached_matrix_to_array(matrix_path)
    assert array.shape == (len(out_lat), len(in_lat))


if __name__ == "__main__":
    pytest.main([__file__])

# #!/usr/bin/env python

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import numpy as np
from scipy.sparse import csr_array, save_npz

from .stream import Stream


def dtype_uint(little_endian, size):
    order = "<" if little_endian else ">"
    return np.dtype({4: np.uint32}[size]).newbyteorder(order)


def dtype_float(little_endian, size):
    order = "<" if little_endian else ">"
    return np.dtype({4: np.float32, 8: np.float64}[size]).newbyteorder(order)


def mir_cached_matrix_to_array(path):
    with open(path, "rb") as f:
        s = Stream(f)
        rows = s.read_unsigned_long()  # rows
        cols = s.read_unsigned_long()  # cols
        s.read_unsigned_long()  # non-zeros, ignored

        little_endian = s.read_int() != 0  # little_endian
        index_item_size = s.read_unsigned_long()  # sizeof(index)
        scalar_item_size = s.read_unsigned_long()  # sizeof(scalar)
        s.read_unsigned_long()  # sizeof(size), ignored

        outer = s.read_large_blob()  # outer
        inner = s.read_large_blob()  # inner
        data = s.read_large_blob()  # data

        outer = np.frombuffer(
            outer,
            dtype=dtype_uint(little_endian, index_item_size),
        )

        inner = np.frombuffer(
            inner,
            dtype=dtype_uint(little_endian, index_item_size),
        )

        data = np.frombuffer(
            data,
            dtype=dtype_float(little_endian, scalar_item_size),
        )

        return csr_array((data, inner, outer), shape=(rows, cols))


def mir_cached_matrix_to_file(path, target):
    if not target.endswith(".npz"):
        raise ValueError("target must end with .npz")

    z = mir_cached_matrix_to_array(path)
    save_npz(target, z)


def mir_write_latlon_to_griddef(path, lats, lons):
    count = len(lats)
    if count != len(lons) or count == 0:
        raise ValueError(
            "Latitudes and longitudes must be non-empty and have the same length."
        )

    version = 1
    with open(path, "wb") as f:
        s = Stream(f)
        s.write_unsigned_long(version)
        s.write_unsigned_long(count)
        for lat, lon in zip(lats, lons):
            s.write_double(lat)
            s.write_double(lon)


def mir_make_matrix(matrix_path, in_lat, in_lon, out_lat, out_lon, mir="mir", **kwargs):
    from pathlib import Path
    from shutil import move
    import subprocess
    from tempfile import TemporaryDirectory
    from os import devnull, environ

    msg = "mir_make_matrix: "

    with TemporaryDirectory() as tmpdir:
        cwd = Path(tmpdir)
        env = environ.copy()
        env["MIR_DEBUG"] = "1"
        env["MIR_CACHE_PATH"] = tmpdir

        mir_write_latlon_to_griddef(cwd / "in.griddef", in_lat, in_lon)
        mir_write_latlon_to_griddef(cwd / "out.griddef", out_lat, out_lon)

        try:
            result = subprocess.run(
                [
                    mir,
                    devnull,
                    devnull,
                    "--input={artificialInput:constant,constant:0.,gridded:True,gridType:unstructured_grid,griddef:in.griddef}",
                    "--griddef=out.griddef",
                ]
                + [f"--{k}={v}" for k, v in kwargs.items()],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
                cwd=cwd,
                env=env,
            )

            matrix_path_temp = next(cwd.rglob("*.mat"), None)
            if matrix_path_temp:
                move(matrix_path_temp, matrix_path)

            if not Path(matrix_path).exists():
                raise FileNotFoundError(msg + f"matrix file '{matrix_path}' not found.")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(msg + f"error ({result.returncode}): {e.stdout}.") from e

        except Exception as e:
            raise RuntimeError(msg + f"error: {e}.") from e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MIR matrix to npz")
    parser.add_argument("input", help="Path to MIR matrix")
    parser.add_argument("output", help="Path to output npz file")
    args = parser.parse_args()

    mir_cached_matrix_to_file(args.input, args.output)

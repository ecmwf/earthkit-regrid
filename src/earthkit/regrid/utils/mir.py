#!/usr/bin/env python

# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
from scipy.sparse import csr_array
from scipy.sparse import save_npz

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
    if not target.suffix == ".npz":
        raise ValueError("target must end with .npz")

    z = mir_cached_matrix_to_array(path)
    save_npz(target, z)


def mir_write_latlon_to_griddef(path, lats, lons):
    count = len(lats)
    if count != len(lons) or count == 0:
        raise ValueError("Latitudes and longitudes must be non-empty and have the same length.")

    version = 1
    with open(path, "wb") as f:
        s = Stream(f)
        s.write_unsigned_long(version)
        s.write_unsigned_long(count)
        for lat, lon in zip(lats, lons):
            s.write_double(lat)
            s.write_double(lon)


def _yaml_from_dict(d):
    import yaml

    return yaml.dump(d, default_flow_style=True).strip()


def _griddef_from_latlon(lat, lon, dir=None):
    import hashlib

    version = 1
    coord = str(version) + str(lat) + str(lon)
    hash = hashlib.md5(coord.encode()).hexdigest()

    name = Path(hash + ".griddef")
    if dir:
        name = dir / name

    if not name.exists():
        mir_write_latlon_to_griddef(name, lat, lon)

    return str(name)


def mir_make_matrix(
    in_grid: Optional[Dict] = None,
    in_lat: Optional[List] = None,
    in_lon: Optional[List] = None,
    out_grid: Optional[Dict] = None,
    out_lat: Optional[List] = None,
    out_lon: Optional[List] = None,
    output=None,
    **kwargs,
):
    import mir

    ext = Path(output).suffix if output is not None else None
    if output is not None and ext not in (".mat", ".npz"):
        raise ValueError("mir_make_matrix: output must have extension .mat or .npz")

    job = mir.Job()

    if in_grid is not None and in_lat is None and in_lon is None:
        input = mir.GridSpecInput(_yaml_from_dict(in_grid))
    elif in_grid is None and in_lat is not None and in_lon is not None:
        input = mir.GriddefInput(_griddef_from_latlon(in_lat, in_lon, mir.cache()))
    else:
        raise ValueError("mir_make_matrix: input grid or lats/lons must be provided.")

    if out_grid is not None and out_lat is None and out_lon is None:
        job.set("grid", _yaml_from_dict(out_grid))
    elif out_grid is None and out_lat is not None and out_lon is not None:
        job.set("griddef", _griddef_from_latlon(out_lat, out_lon, mir.cache()))
    else:
        raise ValueError("mir_make_matrix: output grid or lats/lons must be provided.")

    mat = Path(output)
    if ext == ".mat":
        job.set("interpolation-matrix", str(mat))
    elif ext == ".npz":
        mat = mat.with_name(mat.name + ".mat")  # later unlinked
        job.set("interpolation-matrix", str(mat))

    for key, val in kwargs.items():
        job.set(key, val)

    try:
        job.execute(input, mir.EmptyOutput())
    except Exception as e:
        raise RuntimeError(f"mir_make_matrix: error: {e}.") from e

    if ext and not mat.exists():
        raise FileNotFoundError(f"mir_make_matrix: matrix file '{mat}' not found.")

    if ext == ".npz":
        mir_cached_matrix_to_file(str(mat), output)
        mat.unlink()
        assert Path(output).exists()
    elif not ext:
        return mir_cached_matrix_to_array(mat)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MIR matrix to npz")
    parser.add_argument("input", help="Path to MIR matrix")
    parser.add_argument("output", help="Path to output npz file")
    args = parser.parse_args()

    mir_cached_matrix_to_file(args.input, args.output)

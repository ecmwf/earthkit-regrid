# #!/usr/bin/env python

# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import subprocess
from abc import abstractmethod
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


def mir_make_matrix(in_lat, in_lon, out_lat, out_lon, output=None, mir=None, **kwargs):
    import shutil
    from tempfile import TemporaryDirectory

    mir = mir or os.getenv("MIR_COMMAND", "mir")

    ext = Path(output).suffix if output is not None else None
    if output is not None and ext not in (".mat", ".npz"):
        raise ValueError("mir_make_matrix: output must have extension .mat or .npz")

    with TemporaryDirectory() as tmpdir:
        cwd = Path(tmpdir)
        env = os.environ.copy()
        env["MIR_DEBUG"] = "1"
        env["MIR_CACHE_PATH"] = tmpdir

        mir_write_latlon_to_griddef(cwd / "in.griddef", in_lat, in_lon)
        mir_write_latlon_to_griddef(cwd / "out.griddef", out_lat, out_lon)

        cmd = [
            mir,
            os.devnull,
            os.devnull,
            (
                "--input={artificialInput:constant,constant:0.,gridded:True,"
                "gridType:unstructured_grid,griddef:in.griddef}"
            ),
            "--griddef=out.griddef",
            *[f"--{k}={v}" for k, v in kwargs.items()],
        ]

        try:
            subprocess.run(cmd, check=True, cwd=cwd, env=env)

            matrices = list(cwd.rglob("*.mat"))
            if not matrices:
                raise FileNotFoundError("mir_make_matrix: no matrix file found in output directory.")

            if len(matrices) > 1:
                raise RuntimeError("mir_make_matrix: multiple matrix files found in output directory.")

            if output is None:
                return mir_cached_matrix_to_array(matrices[0])

            if ext == ".npz":
                mir_cached_matrix_to_file(matrices[0], output)
            else:
                shutil.move(matrices[0], output)

        except Exception as e:
            raise RuntimeError(f"mir_make_matrix: error: {e}.") from e


class _GridArgument:
    @abstractmethod
    def describe_as_input(self):
        pass

    @abstractmethod
    def describe_as_output(self):
        pass


class _GridAsUnstructured(_GridArgument):
    def __init__(self, lats, lons):
        self.lats = lats
        self.lons = lons
        self.hash = None

    def _path(self):
        # This is a hack to generate a unique path for the griddef file
        # (a temporary working directory should be used in the actual implementation)
        if self.hash is None:
            import hashlib

            coord = str(self.lats) + str(self.lons)
            self.hash = hashlib.md5(coord.encode()).hexdigest()

        name = Path(self.hash + ".griddef")
        if not name.exists(name):
            mir_write_latlon_to_griddef(name, self.lats, self.lons)

        return name

    def describe_as_input(self):
        import yaml

        d = dict(
            artificialInput="constant",
            constant=0.0,
            gridded=True,
            gridType="unstructured_grid",
            griddef=f"{self._path()}",
        )
        return "--input=" + yaml.dump(d, default_flow_style=True).strip()

    def describe_as_output(self):
        return f"--griddef={self._path()}"


class _GridAsGridspec(_GridArgument):
    def __init__(self, gridspec):
        self.gridspec = gridspec

    def describe_as_input(self):
        import yaml

        d = dict(artificialInput="gridspec", gridspec=self.gridspec)
        return "--input=" + yaml.dump(d, default_flow_style=True).strip()

    def describe_as_output(self):
        import yaml

        return "--grid=" + yaml.dump(self.gridspec, default_flow_style=True).strip()


def mir_make_another_matrix(
    input_grid: Optional[Dict] = None,
    input_lat: Optional[List] = None,
    input_lon: Optional[List] = None,
    output_grid: Optional[Dict] = None,
    output_lat: Optional[List] = None,
    output_lon: Optional[List] = None,
    output=None,
    mir=None,
    **kwargs,
):
    import shutil
    from tempfile import TemporaryDirectory

    mir = mir or os.getenv("MIR_COMMAND", "mir")

    ext = Path(output).suffix if output is not None else None
    if output is not None and ext not in (".mat", ".npz"):
        raise ValueError("mir_make_matrix: output must have extension .mat or .npz")

    def grid_argument(spec, lat, lon):
        if spec is not None and lat is None and lon is None:
            return _GridAsGridspec(spec)
        if spec is None and lat is not None and lon is not None:
            return _GridAsUnstructured(lat, lon)
        raise ValueError("mir_make_another_matrix: either grid or lat/lon must be provided.")

    input_grid = grid_argument(input_grid, input_lat, input_lon).describe_as_input()
    output_grid = grid_argument(output_grid, output_lat, output_lon).describe_as_output()

    with TemporaryDirectory() as tmpdir:
        cwd = Path(tmpdir)
        env = os.environ.copy()
        env["MIR_DEBUG"] = "1"
        env["MIR_CACHE_PATH"] = tmpdir

        cmd = [
            mir,
            os.devnull,
            os.devnull,
            input_grid,
            output_grid,
            *[f"--{k}={v}" for k, v in kwargs.items()],
        ]

        try:
            subprocess.run(cmd, check=True, cwd=cwd, env=env)

            matrices = list(cwd.rglob("*.mat"))
            if not matrices:
                raise FileNotFoundError("mir_make_another_matrix: no matrix file found in output directory.")

            if len(matrices) > 1:
                raise RuntimeError(
                    "mir_make_another_matrix: multiple matrix files found in output directory."
                )

            if output is None:
                return mir_cached_matrix_to_array(matrices[0])

            if ext == ".npz":
                mir_cached_matrix_to_file(matrices[0], output)
            else:
                shutil.move(matrices[0], output)

        except Exception as e:
            raise RuntimeError(f"mir_make_another_matrix: error: {e}.") from e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MIR matrix to npz")
    parser.add_argument("input", help="Path to MIR matrix")
    parser.add_argument("output", help="Path to output npz file")
    args = parser.parse_args()

    mir_cached_matrix_to_file(args.input, args.output)

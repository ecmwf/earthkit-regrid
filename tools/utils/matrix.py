# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import re
from functools import cache

LOG = logging.getLogger(__name__)

GRIB_DIR = "grib"
MIR_PATH = os.path.expanduser("~/build/mir/release/bin/mir")
MIR_INTERPOLATE_OPTION = "interpolation"


def download_index_file(target):
    import requests

    from earthkit.regrid.db import _INDEX_GZ_FILENAME, _SYSTEM_URL

    path = os.path.join(_SYSTEM_URL, _INDEX_GZ_FILENAME)
    requests.get(path)
    r = requests.get(path, allow_redirects=True)
    target_gz = target + ".gz"
    open(target_gz, "wb").write(r.content)
    import gzip

    with gzip.open(target_gz, "rb") as f:
        data = f.read()
        with open(target, "wb") as f_out:
            f_out.write(data)


def adjust_grid_name(name):
    d = {"n": "N", "o": "O", "f": "F", "/": "x"}
    for k, v in d.items():
        name = name.replace(k, v)
    return name


@cache
def get_mir_version():
    import subprocess

    res = subprocess.run(
        [MIR_PATH, "--version", "x", "x"],
        stdout=subprocess.PIPE,
    )
    for line in res.stdout.decode("utf-8").split("\n"):
        if line.lower().startswith("mir"):
            return line.split(" ")[1]


def get_grib_file(grid, grib_file):
    if not os.path.exists(grib_file):
        from earthkit.data import from_source

        _class = "od"
        expver = "1"
        if grid in ["N2560", "O2560"]:
            _class = "rd"
            expver = "i4ql"

        ds = from_source(
            "mars",
            {
                "levtype": "sfc",
                "param": "2t",
                "grid": grid,
                "class": _class,
                "expver": expver,
                "type": "fc",
                "time": "0",
            },
        )
        ds.save(grib_file)


def create_matrix_files(
    matrix_dir,
    src_grid_label,
    target_grid_label,
    target_grid,
    options,
    grib_file,
    index_file,
    add_to_index=True,
    delete_tmp_json=False,
):
    # generate interpolation matrix
    if options:
        kwargs = " ".join([f"--{k}={v}" for k, v in options.items()])
    else:
        kwargs = ""

    matrix_json = f"{target_grid_label}-{src_grid_label}"
    if MIR_INTERPOLATE_OPTION in options:
        matrix_json += "-" + options[MIR_INTERPOLATE_OPTION]
    matrix_json = os.path.join(matrix_dir, f"{matrix_json}.json")

    if not os.path.exists(matrix_json):
        cmd = (
            f"{MIR_PATH} --grid={target_grid} {kwargs} --dump-weights-info={matrix_json}"
            f" {grib_file} /dev/null"
        )
        LOG.debug(f" {cmd=}")
        os.system(cmd)

    if not os.path.exists(matrix_json):
        print(f"{matrix_json} does not exist!")

    if add_to_index:
        # process matrix and add it to index json file
        from earthkit.regrid.utils.matrix import make_matrix

        make_matrix(
            matrix_json,
            matrix_dir,
            index_file=index_file,
            global_input=True,
            global_output=True,
        )

    if delete_tmp_json:
        os.remove(matrix_json)


def make_matrix(
    src_grid,
    target_grid,
    method,
    matrix_dir,
    index_file=None,
    download_index=False,
    delete_tmp_json=False,
):
    LOG.debug(f"{src_grid=} {target_grid=} {matrix_dir=} {index_file=}")

    options = {}

    src_grid_label = src_grid
    target_grid_label = target_grid

    options[MIR_INTERPOLATE_OPTION] = method

    if not re.match(r"[Hh]\d+_[A-z]+", src_grid):
        #     if src_grid.endswith("_nested"):
        #         options[MIR_INTERPOLATE_OPTION] = "nearest-neighbor"
        # else:
        src_grid_label = adjust_grid_name(src_grid)

    if not re.match(r"[Hh]\d+_[A-z]+", target_grid):
        target_grid_label = adjust_grid_name(target_grid)

    os.makedirs(matrix_dir, exist_ok=True)
    if index_file is None:
        index_file = os.path.join(matrix_dir, "index.json")

    assert os.path.exists(GRIB_DIR)
    assert os.path.exists(matrix_dir)
    assert index_file is not None

    if download_index:
        download_index_file(index_file)
        assert os.path.exists(index_file)

    grib_file = os.path.join(GRIB_DIR, f"{src_grid_label}.grib")
    get_grib_file(src_grid, grib_file)

    # version = get_mir_version()

    create_matrix_files(
        matrix_dir,
        src_grid_label,
        target_grid_label,
        target_grid,
        options,
        grib_file,
        index_file,
        add_to_index=True,
        delete_tmp_json=delete_tmp_json,
    )

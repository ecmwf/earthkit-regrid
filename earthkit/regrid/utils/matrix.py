# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import os

from .mir import mir_cached_matrix_to_file


def regular_ll(entry):
    bb = entry["bbox"]
    d = {
        "grid": [entry["increments"][x] for x in ("west_east", "south_north")],
        "shape": [entry["nj"], entry["ni"]],
        "area": [bb["north"], bb["west"], bb["south"], bb["east"]],
    }
    if "global" in entry:
        d["global"] = entry["global"]
    return d


def reduced_gg(entry):
    pl = entry["pl"]
    G = "O" if pl[1] - pl[0] == 4 else "N"
    N = entry["N"]
    bb = entry["bbox"]

    d = {
        "grid": f"{G}{N}",
        "shape": [sum(pl)],
        "area": [bb["north"], bb["west"], bb["south"], bb["east"]],
    }

    if "global" in entry:
        d["global"] = entry["global"]

    return d


def make_matrix(
    input_path, output_path, global_input=None, global_output=None, version=None
):
    with open(input_path) as f:
        entry = json.load(f)

    cache_file = entry.pop("cache_file")
    name, _ = os.path.splitext(os.path.basename(cache_file))

    # print(f"MATRICES={MATRICES}")

    if version is None:
        version = "0" * 6
    else:
        version = "".join([f"{int(x):02d}" for x in version.split(".")])

    os.makedirs(output_path, exist_ok=True)

    print(f"entry={entry}")
    npz_file = os.path.join(output_path, f"{name}-{version}.npz")

    mir_cached_matrix_to_file(cache_file, npz_file)

    index_file = os.path.join(output_path, "index.json")
    if os.path.exists(index_file):
        with open(index_file) as f:
            index = json.load(f)
    else:
        index = {}

    def convert(x):
        proc = globals()[x["type"]]
        return proc(x)

    if global_input is not None and "global" not in entry["input"]:
        entry["input"]["global"] = 1 if global_input else 0

    if global_output is not None and "global" not in entry["output"]:
        entry["output"]["global"] = 1 if global_output else 0

    index[name] = dict(
        name=name,
        versions=[version],
        input=convert(entry["input"]),
        output=convert(entry["output"]),
    )

    with open(index_file, "w") as f:
        json.dump(index, f, indent=4)

    print("Written", npz_file)
    print("Written", index_file)

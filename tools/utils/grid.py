# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def make_ll(g):
    return f"{g}/{g}"


def make_O_rgg(g):
    return f"O{g}"


def make_N_rgg(g):
    return f"N{g}"


def make_H_ring(g):
    return f"H{g}_ring"


def make_H_nested(g):
    return f"H{g}_nested"


def make_other(g):
    return f"{g}"


makers = {
    k: globals()[f"make_{k}"] for k in ["ll", "O_rgg", "N_rgg", "H_ring", "H_nested"]
}


def make_grid_id(grids):
    r = []
    for k, v in grids.items():
        m = makers.get(k, make_other)
        for x in v:
            r.append(m(x))
    return r

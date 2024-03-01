# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from utils.grid import make_grid_id
from utils.matrix import make_matrix

LOG = logging.getLogger(__name__)


# shorthand for grid definition:
# ll : 1 - > 1/1
# O_rgg: 32 -> O32
# N_rgg: 32 -> N32
# H_ring: 32 -> H32_ring
# H_nested: 32 -> H32_nested


logging.basicConfig(level=logging.DEBUG)

in_grids = {
    "ll": [],
    "O_rgg": [],
    "N_rgg": [],
    # "H_ring": [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2],
    "H_nested": [1024, 512, 256, 128, 64, 32, 16, 8, 4, 2],
}
out_grids = {
    "ll": [
        0.1,
        0.15,
        0.2,
        0.25,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.75,
        0.8,
        0.9,
        1,
        1.2,
        1.25,
        1.4,
        1.5,
        1.6,
        1.8,
        2,
        2.5,
        5,
        10,
    ]
}

matrix_dir = "matrices_29022024"
# index_file = "index/index.json"

in_grids = make_grid_id(in_grids)
out_grids = make_grid_id(out_grids)

LOG.debug(f"{in_grids=}")
LOG.debug(f"{out_grids=}")

for g_in in in_grids:
    for g_out in out_grids:
        if g_in != g_out:
            make_matrix(g_in, g_out, matrix_dir, index_file=None, download_index=False)

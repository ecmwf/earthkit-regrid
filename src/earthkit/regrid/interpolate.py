# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import deprecation

from .data import get_data_handler


@deprecation.deprecated(deprecated_in="0.5.0", removed_in=None, details="Use regrid() instead")
def interpolate(values, in_grid=None, out_grid=None, method="linear", **kwargs):
    h = get_data_handler(values)
    if h is None:
        raise ValueError(f"Cannot call interpolate() with data type={type(values)}")

    return h.interpolate(values, in_grid=in_grid, out_grid=out_grid, method=method, **kwargs)

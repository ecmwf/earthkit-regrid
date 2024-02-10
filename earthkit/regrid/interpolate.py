# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from earthkit.regrid.db import DB


def interpolate(values, source_gridspec, target_gridspec, matrix_version=None):
    z, shape = DB.find(source_gridspec, target_gridspec, matrix_version=matrix_version)

    if z is None:
        raise ValueError("No matrix found that matches the source and target gridspecs")

    # This should check for 1D (GG) and 2D (LL) matrices
    values = values.reshape(-1, 1)

    values = z @ values

    return values.reshape(shape)

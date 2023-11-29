# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from earthkit.regrid.db import DB


def interpolate(x, gridspec_in, gridspec_out, matrix_version=None):
    z, shape = DB.find(gridspec_in, gridspec_out, matrix_version=matrix_version)

    if z is None:
        raise ValueError("No matrix found that matches the input and output gridspecs")

    # This should check for 1D (GG) and 2D (LL) matrices
    x = x.reshape(-1, 1)

    x = z @ x

    return x.reshape(shape)

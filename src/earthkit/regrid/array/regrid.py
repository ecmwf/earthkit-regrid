# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
#


def regrid(values, in_grid=None, out_grid=None, *, interpolation="linear", backend="mir", **kwargs):
    from earthkit.regrid.data.numpy import handler

    h = handler()
    kwargs = kwargs.copy()
    return h.regrid(
        values, in_grid=in_grid, out_grid=out_grid, interpolation=interpolation, backend=backend, **kwargs
    )

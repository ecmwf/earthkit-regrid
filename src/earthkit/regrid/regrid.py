# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def _is_array(values):  # IGNORE
    import numpy as np

    return isinstance(values, np.ndarray)  # IGNORE


def regrid(values, grid=None, *, interpolation="linear", backend="mir", **kwargs):
    from earthkit.regrid.data import get_data_handler

    h = get_data_handler(values)
    if h is None:
        if _is_array(values):
            txt = (
                f"Unsupported data type={type(values)}. Use earthkit.regrid.array.regrid.regrid() for arrays"
            )
        else:
            txt = f"Unsupported type={type(values)}"
        raise ValueError(txt)

    kwargs = kwargs.copy()
    return h.regrid(values, grid=grid, interpolation=interpolation, backend=backend, **kwargs)

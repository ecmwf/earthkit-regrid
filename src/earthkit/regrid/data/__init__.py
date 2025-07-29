# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from importlib import import_module

DATA_HANDLERS = []
for name in ["numpy", "fieldlist", "grib", "xarray"]:
    module = import_module(f".{name}", package=__name__)
    lst = getattr(module, "handler", [])
    if not isinstance(lst, list):
        lst = [lst]
    assert isinstance(lst, list), f"Expected a list of handlers in {module.__name__}"
    DATA_HANDLERS.extend(lst)


def get_data_handler(values):
    for h in DATA_HANDLERS:
        if h.match(values):
            return h

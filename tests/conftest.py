# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


def pytest_runtest_setup(item):
    # print(f"config {item.config.option}")

    marks_in_items = list([m.name for m in item.iter_markers()])

    from earthkit.regrid.db import DB
    from earthkit.regrid.utils.caching import CACHE, SETTINGS

    DB.clear_index()

    if "tmp_cache" in marks_in_items:
        # ensure these tests use a temporary cache
        SETTINGS["cache-policy"] = "temporary"
        CACHE._settings_changed()
    else:
        SETTINGS["cache-policy"] = "user"
        CACHE._settings_changed()

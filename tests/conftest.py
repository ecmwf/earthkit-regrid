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

    from earthkit.regrid.backends.db import SYS_DB

    SYS_DB._clear_index()

    tmp_cache = "tmp_cache" in marks_in_items

    # settings
    from earthkit.regrid import config

    # ensure settings are not saved automatically
    config.autosave = False

    # ensure all the tests use the default settings
    if tmp_cache:
        # ensure these tests use a temporary cache
        config.reset()
        config.set("cache-policy", "temporary")
    else:
        config.reset()
        config.set("cache-policy", "user")

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

try:
    # There is a bug in tqdm that expects ipywidgets
    # to be installed if running in a notebook
    import ipywidgets  # noqa F401
    from tqdm.auto import tqdm  # noqa F401
except ImportError:
    from tqdm import tqdm  # noqa F401


def progress_bar(*, total=None, iterable=None, initial=0, desc=None):
    return tqdm(
        iterable=iterable,
        total=total,
        initial=initial,
        unit_scale=True,
        unit_divisor=1024,
        unit="B",
        disable=False,
        leave=False,
        desc=desc,
        # dynamic_ncols=True, # make this the default?
    )

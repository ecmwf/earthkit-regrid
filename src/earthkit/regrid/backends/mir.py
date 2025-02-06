# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from . import Backend


class MirBackend(Backend):
    name = "mir"

    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        raise NotImplementedError("This method is not implemented yet")

        # TODO: Implement the interpolation using the 'mir' package.
        # The code below is a placeholder and should be replaced with the actual implementation.
        # try:
        #     import pymir
        # except ImportError:
        #     self.enabled = False
        #     raise ImportError("The 'mir' package is required for this operation")

        # return pymir.interpolate(values, in_grid, out_grid, method, **kwargs)


backend = MirBackend

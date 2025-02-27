# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from earthkit.regrid.utils import yaml_from_dict

from . import Backend


class MirBackend(Backend):
    name = "mir"

    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        try:
            import mir
        except ImportError:
            self.enabled = False
            raise ImportError("The 'mir' package is required for this operation")

        # TODO: Implement the interpolation using the 'mir' package.
        import mir

        in_grid = mir.GridSpecInput(yaml_from_dict(in_grid))
        out_grid = mir.GridSpecOutput(yaml_from_dict(out_grid))

        job = mir.Job()

        job.set("grid", out_grid)
        job.set("method", method)
        for key, val in kwargs.items():
            job.set(key, val)

        # TODO: execute the job, pass the values, and return the result


backend = MirBackend

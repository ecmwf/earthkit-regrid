# (C) Copyright 2025- ECMWF.
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
        import mir

        input = mir.ArrayInput(values, in_grid)

        job = mir.Job()
        job.set("grid", out_grid)
        job.set("interpolation", method)  # NOTE: needs generalisation
        for k, v in kwargs.items():
            job.set(k, v)

        output = mir.ArrayOutput()
        job.execute(input, output)

        # NOTE: this discards output metadata, such as output.spec
        return output.values()


backend = MirBackend

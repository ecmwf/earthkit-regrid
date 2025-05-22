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

    def regrid(self, values, in_grid, out_grid, interpolation, output=Backend.outputs[0], **kwargs):
        import mir

        input = mir.ArrayInput(values, in_grid)
        out = mir.ArrayOutput()

        job = mir.Job()
        job.set("grid", out_grid)
        job.set("interpolation", interpolation)  # NOTE: needs generalisation
        for k, v in kwargs.items():
            job.set(k, v)

        job.execute(input, out)

        if output == "values_gridspec":
            return out.values(), out.spec
        elif output == "values":
            return out.values()
        elif output == "gridspec":
            return out.spec

        raise ValueError("No output found!")

    def regrid_grib(self, message, out_grid, **kwargs):
        from io import BytesIO

        import mir

        in_data = mir.GribMemoryInput(message.getvalue())
        out = BytesIO()

        job = mir.Job()
        job.set("grid", out_grid)
        for k, v in kwargs.items():
            job.set(k, v)

        job.execute(in_data, out)

        return out.getvalue()


backend = MirBackend

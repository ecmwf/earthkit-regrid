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

    def regrid(self, values, in_grid, out_grid, interpolation, output=Backend.outputs, **kwargs):
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

    def regrid_grib(self, in_grib, out_grid, **kwargs):
        from io import BytesIO

        import mir
        from earthkit.data.readers.grib.codes import GribField
        from earthkit.data.readers.grib.memory import GribFieldInMemory

        if isinstance(in_grib, GribField):
            buf = BytesIO(in_grib.message())
            input = mir.GribMemoryInput(buf.getvalue())
        elif isinstance(in_grib, BytesIO):
            input = mir.GribMemoryInput(in_grib.getvalue())
        else:
            raise ValueError("Input must be a GribField or BytesIO object")

        out = BytesIO()

        job = mir.Job()
        job.set("grid", out_grid)
        for k, v in kwargs.items():
            job.set(k, v)

        job.execute(input, out)

        return GribFieldInMemory.from_buffer(out.getvalue())


backend = MirBackend

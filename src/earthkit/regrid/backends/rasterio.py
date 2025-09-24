# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from . import Backend


class RasterioBackend(Backend):

    name = "rasterio"

    def regrid(self, values, in_grid, out_grid, resampling=None, **kwargs):
        from rasterio.enums import Resampling
        from rasterio.warp import reproject

        print("RASTERIO_REGRID kwargs", kwargs)
        reproject_kwargs = {"src_crs": in_grid, "dst_crs": out_grid}

        # TODO: by default an "interpolation" kwarg is provided and set to "linear" by default
        #       linear is "bilinear" in rasterio and not the default that rasterio users are
        #       used to (nearest is default in rasterio)
        if resampling is not None:
            reproject_kwargs["resampling"] = Resampling[resampling]

        # TODO: go through kwargs and apply valid ones (default interpolation can be just handed over)

        print(reproject_kwargs)
        return reproject(source=values, **reproject_kwargs)


backend = RasterioBackend

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import functools
import logging

from .handler import DataHandler

LOG = logging.getLogger(__name__)


class XarrayDataHandler(DataHandler):
    @staticmethod
    def match(values):
        from earthkit.regrid.utils import is_module_loaded

        if not is_module_loaded("xarray"):
            return False

        try:
            import xarray as xr

            return isinstance(values, (xr.DataArray, xr.Dataset))
        except Exception:
            return False

    def _find_dim_names(self, size):
        match size:
            case 1:
                return ["values"]
            case 2:
                return ["latitude", "longitude"]
            case _:
                return None

    def regrid(self, values, **kwargs):
        from .numpy import NumpyDataHandler

        # backend = self.backend_from_kwargs(kwargs)

        in_grid = kwargs.pop("in_grid", None)
        if in_grid is None:
            in_grid = values.attrs.get("gridspec", None)
            if in_grid is None and "earthkit" in values:
                in_grid = values.earthkit.grid_spec

        out_grid = kwargs.pop("out_grid")

        import xarray as xr

        assert in_grid is not None, "in_grid must be provided"
        assert out_grid is not None, "out_grid must be provided"

        shape = None
        # _, shape = find(in_grid, out_grid, **kwargs)

        default_in_dims = self._find_dim_names(len(values.dims))
        if "in_dims" not in kwargs and default_in_dims is None:
            raise ValueError(f"Unknown number of input dimensions: {len(values.dims)}")

        in_dims = kwargs.pop("in_dims", default_in_dims)
        in_dims = [in_dims] if not isinstance(in_dims, list) else in_dims

        default_out_dims = self._find_dim_names(len(shape))
        if "out_dims" not in kwargs and default_out_dims is None:
            raise ValueError("Unknown number of output dimensions.")

        out_dims = kwargs.pop("out_dims", default_out_dims)
        out_dims = [out_dims] if not isinstance(out_dims, list) else out_dims

        ds_out = xr.apply_ufunc(
            functools.partial(NumpyDataHandler().regrid, in_grid=in_grid, out_grid=out_grid, **kwargs),
            values,
            input_core_dims=[in_dims],
            output_core_dims=[out_dims],
            vectorize=True,
            dask="parallelized",
            dask_gufunc_kwargs={
                "output_sizes": {dim: shape[i] for i, dim in enumerate(out_dims)},
                "allow_rechunk": True,
            },
            output_dtypes=[values.dtype],
        )
        # self.set_coords(ds_out, out_grid, **kwargs)
        # ds_out.earthkit.set_grid(out_grid)

        return ds_out

    def set_coords(self, ds_out, out_grid, **kwargs):
        import earthkit.geo as ekg

        lat, lon = ekg.to_latlon(out_grid)
        ds_out.coords["latitude"] = lat
        ds_out.coords["longitude"] = lon


handler = XarrayDataHandler()

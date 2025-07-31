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

from earthkit.regrid.utils import ensure_list

from .handler import DataHandler

LOG = logging.getLogger(__name__)


# TODO: This is a temporary wrapper to use the grid interface
class GridWrapper:
    def __init__(self, grid_spec):
        from mir import Grid

        self._grid = Grid(**grid_spec)
        self._grid_spec = grid_spec

    def __getattr__(self, name):
        return getattr(self._grid, name)

    def to_latlons(self):
        import numpy as np

        lat, lon = self._grid.to_latlons()
        return np.array(lat), np.array(lon)

    @property
    def grid_spec(self):
        return self.spec

    def is_spectral(self):
        return False

    def to_distinct_latlons(self, field_shape):
        if len(self._grid.shape) == 2:
            lat, lon = self.to_latlons()
            lat = lat.reshape(self._grid.shape)
            lon = lon.reshape(self._grid.shape)
            d_lat = self._distinct_lats(lat)
            if d_lat is not None:
                d_lon = self._distinct_lons(lon)
                if d_lon is not None and len(d_lat) == field_shape[0] and len(d_lon) == field_shape[1]:
                    return d_lat, d_lon

        return None, None

    @staticmethod
    def _distinct_lats(lats):
        import numpy as np

        assert len(lats.shape) == 2
        rows = lats.shape[0]
        r = np.ones(rows)
        if rows > 0:
            for i in range(rows):
                vals = lats[i, :]
                delta = np.diff(vals)
                if np.allclose(delta, delta[0]):
                    r[i] = vals[0]
                else:
                    return None
            return r
        return None

    @staticmethod
    def _distinct_lons(lons):
        import numpy as np

        assert len(lons.shape) == 2
        cols = lons.shape[1]
        r = np.ones(cols)
        if cols > 0:
            for i in range(cols):
                vals = lons[:, i]
                delta = np.diff(vals)
                if np.allclose(delta, delta[0]):
                    r[i] = vals[0]
                else:
                    return None
            return r
        return None


# TODO: move this code to earthkit-geo
class XarrrayGeographyBuilder:
    def __init__(self, grid_spec):
        self.grid = GridWrapper(grid_spec)
        self.grid_spec = grid_spec

    @property
    def shape(self):
        return self.grid.shape

    def geo_dims(self):
        """
        Determine the geographical dimensions of the dataset.
        """
        num = len(self.shape)
        if num >= 2:
            return ["latitude", "longitude"]
        if num == 1:
            return ["values"]

        raise ValueError("Geography is not supported.")

    def coords(self):
        import math

        field_shape = self.grid.shape

        coords = {}
        dims = {}
        coords_dim = {}

        if self.grid.is_spectral():
            if len(field_shape) == 1:
                dims["values"] = field_shape[0]
        else:
            if len(field_shape) == 1:
                dims["values"] = field_shape[0]
                try:
                    lat, lon = self.grid.to_latlons()
                    if lat is not None and lon is not None:
                        coords["latitude"] = lat
                        coords["longitude"] = lon
                        coords_dim = {k: ("values",) for k in coords}
                except Exception:
                    pass
            elif len(field_shape) == 2:
                try:
                    lat, lon = self.grid.to_distinct_latlons(field_shape)
                    if (
                        lat is not None
                        and lon is not None
                        and len(lat) == field_shape[0]
                        and len(lon) == field_shape[1]
                    ):
                        coords["latitude"] = lat
                        coords["longitude"] = lon
                        coords_dim["latitude"] = ("latitude",)
                        coords_dim["longitude"] = ("longitude",)
                        dims["latitude"] = lat.size
                        dims["longitude"] = lon.size
                        assert coords["latitude"].size == field_shape[0]
                        assert coords["longitude"].size == field_shape[1]
                        assert dims["latitude"] == field_shape[0]
                        assert dims["longitude"] == field_shape[1]
                except Exception as e:
                    print(e)
                    pass

                if not coords or not dims:
                    lat, lon = self.grid.to_latlons()
                    # print("to_latlons:", type(lat), type(lon))
                    if lat is not None and lon is not None:
                        lat = lat.reshape(field_shape)
                        lon = lon.reshape(field_shape)
                        coords["latitude"] = lat
                        coords["longitude"] = lon
                        coords_dim = {k: ("y", "x") for k in coords}
                        dims["y"] = field_shape[0]
                        dims["x"] = field_shape[1]
                        # print("field_shape:", field_shape, lat.shape, lon.shape)
                        assert coords["latitude"].shape == field_shape
                        assert coords["longitude"].shape == field_shape
            else:
                raise ValueError(f"Unsupported field shape {field_shape}")

        for k, v in coords.items():
            assert k in coords_dim, f"{k=}, {coords_dim=}"
            assert all(x in dims for x in coords_dim[k]), f"{k=}, {coords_dim=} {dims=}"
            assert v.size == math.prod([dims[x] for x in coords_dim[k]])

        return dims, coords, coords_dim


def xr_geo_dims(ds):
    """
    Determine the geographical dimensions of the dataset/dataarray.
    """
    dims = list(ds.sizes.keys())
    if len(ds.dims) >= 1:
        if dims[-1] == "values":
            return ["values"]
    if len(dims) >= 2:
        if dims[-2] == "latitude" and dims[-1] == "longitude":
            return ["latitude", "longitude"]

    raise ValueError("Dataset geography is not supported.")


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

    @staticmethod
    def get_in_grid(ds, kwargs):
        """
        Get the input grid from the dataset or from the kwargs.
        """
        in_grid = kwargs.pop("in_grid", None)
        if in_grid is None:
            try:
                in_grid = ds.attrs.get("gridspec", None)
                if in_grid is None:
                    in_grid = ds.earthkit.grid_spec
            except AttributeError:
                pass

        if in_grid is None:
            raise ValueError("in_grid must be provided")

        return GridWrapper(in_grid)

    @staticmethod
    def get_out_geo(kwargs):
        """
        Get the output geography from the out_grid.
        """
        out_grid = kwargs.pop("out_grid")
        if out_grid is None:
            raise ValueError("out_grid must be provided")

        out_geo = XarrrayGeographyBuilder(out_grid)
        return out_geo

    @staticmethod
    def add_geo_coords(ds, out_geo):
        """
        Add the geographical coordinates to the dataset.
        """
        dims, coords, coords_dim = out_geo.coords()

        import xarray as xr

        for k, v in coords.items():
            c_dims = {x: dims[x] for x in coords_dim[k]}
            ds.coords[k] = xr.Variable(c_dims, v)

        return ds

    def regrid(self, values, **kwargs):
        from .numpy import NumpyDataHandler

        kwargs = kwargs.copy()

        in_grid = self.get_in_grid(values, kwargs)
        out_geo = self.get_out_geo(kwargs)

        in_dims = kwargs.pop("in_dims", None)
        if in_dims is None:
            in_dims = xr_geo_dims(values)

        if in_dims is None:
            raise ValueError(f"Could not determine geography related input dimensions: {values.dims}")

        out_dims = kwargs.pop("out_dims", None)
        if out_dims is None:
            out_dims = out_geo.geo_dims()

        if out_dims is None:
            raise ValueError(f"Could not determine geography related output dimensions: {values.dims}")

        in_dims = ensure_list(in_dims)
        out_dims = ensure_list(out_dims)

        import xarray as xr

        exclude_dims = set()
        if set(in_dims) == set(out_dims):
            exclude_dims = set(in_dims)

        class _RegridMethod:
            def __init__(self, in_grid, out_grid, **kwargs):
                self.out_grid = out_grid
                self.method = functools.partial(
                    NumpyDataHandler().regrid,
                    in_grid=in_grid,
                    out_grid=out_grid,
                    # output="values",
                    **kwargs,
                )

            def __call__(self, vals):
                vals, self.out_grid = self.method(vals)
                return vals

        # method = functools.partial(
        #     NumpyDataHandler().regrid,
        #     in_grid=in_grid.grid_spec,
        #     out_grid=out_geo.grid_spec,
        #     output="values",
        #     **kwargs,
        # )

        method = _RegridMethod(in_grid.grid_spec, out_geo.grid_spec, **kwargs)

        def _regrid(da):
            return xr.apply_ufunc(
                method,
                da,
                input_core_dims=[in_dims],
                output_core_dims=[out_dims],
                exclude_dims=exclude_dims,
                vectorize=True,
                dask="parallelized",
                dask_gufunc_kwargs={
                    "output_sizes": {dim: out_geo.shape[i] for i, dim in enumerate(out_dims)},
                    "allow_rechunk": True,
                },
                output_dtypes=[da.dtype],
            )

        if isinstance(values, xr.Dataset):
            ds_out = xr.Dataset()
            for var_name, var in values.data_vars.items():
                ds_out[var_name] = _regrid(var)

        else:
            ds_out = _regrid(values)

        # The output geography might have changed, so we need to create a new geography builder
        # with the new grid spec
        out_geo = XarrrayGeographyBuilder(method.out_grid)

        self.add_geo_coords(ds_out, out_geo)

        return ds_out


handler = XarrayDataHandler

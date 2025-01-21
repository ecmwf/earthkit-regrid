# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import functools

from earthkit.regrid.db import find


def interpolate(values, in_grid=None, out_grid=None, method="linear", **kwargs):
    interpolator = _find_interpolator(values)
    if interpolator is None:
        raise ValueError(f"Cannot interpolate data with type={type(values)}")

    return interpolator(
        values, in_grid=in_grid, out_grid=out_grid, method=method, **kwargs
    )


def _find_interpolator(values):
    for interpolator in INTERPOLATORS:
        if interpolator.match(values):
            return interpolator
    return None


def _interpolate(values, in_grid, out_grid, method, **kwargs):
    z, shape = find(in_grid, out_grid, method, **kwargs)

    if z is None:
        raise ValueError(f"No matrix found! {in_grid=} {out_grid=} {method=}")

    # This should check for 1D (GG) and 2D (LL) matrices
    values = values.reshape(-1, 1)

    values = z @ values

    return values.reshape(shape)


class NumpyInterpolator:
    @staticmethod
    def match(values):
        import numpy as np

        return isinstance(values, np.ndarray)

    def __call__(self, values, **kwargs):
        in_grid = kwargs.pop("in_grid")
        out_grid = kwargs.pop("out_grid")
        method = kwargs.pop("method")
        return _interpolate(values, in_grid, out_grid, method, **kwargs)


class XarrayInterpolator:
    @staticmethod
    def match(values):
        try:
            import xarray as xr

            return isinstance(values, xr.DataArray) or isinstance(values, xr.Dataset)
        except ImportError:
            return False

    def _find_dim_names(self, size):
        match size:
            case 1:
                return ["values"]
            case 2:
                return ["latitude", "longitude"]
            case _:
                return None

    def __call__(self, values, **kwargs):
        import xarray as xr

        in_grid = kwargs.pop("in_grid", None)
        if in_grid is None:
            in_grid = values.attrs.get("gridspec", None)
        if in_grid is None and 'earthkit' in values:
            in_grid = values.earthkit.metadata.gridspec

        out_grid = kwargs.pop("out_grid")

        assert in_grid is not None, "in_grid must be provided"
        assert out_grid is not None, "out_grid must be provided"

        _, shape = find(in_grid, out_grid, **kwargs)

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

        return xr.apply_ufunc(
            functools.partial(
                NumpyInterpolator(), in_grid=in_grid, out_grid=out_grid, **kwargs
            ),
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


class FieldListInterpolator:
    @staticmethod
    def match(values):
        try:
            import earthkit.data

            return isinstance(values, earthkit.data.FieldList)
        except ImportError:
            return False

    def __call__(self, values, **kwargs):
        import earthkit.data

        ds = values
        in_grid = kwargs.pop("in_grid")
        if in_grid is not None:
            raise ValueError("in_grid cannot be used for FieldList interpolation")
        out_grid = kwargs.pop("out_grid")
        method = kwargs.pop("method")

        r = earthkit.data.FieldList()
        for f in ds:
            vv = f.to_numpy(flatten=True)
            v_res = _interpolate(
                vv,
                f.metadata().gridspec,
                out_grid,
                method,
                **kwargs,
            )
            md_res = f.metadata().override(gridspec=out_grid)
            r += ds.from_numpy(v_res, md_res)

        return r


INTERPOLATORS = [NumpyInterpolator(), FieldListInterpolator(), XarrayInterpolator()]

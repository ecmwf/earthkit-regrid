# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
from abc import ABCMeta
from abc import abstractmethod
import functools

LOG = logging.getLogger(__name__)


class DataHandler(metaclass=ABCMeta):
    @abstractmethod
    def regrid(self, values, **kwargs):
        pass

    def backend_from_kwargs(self, kwargs):
        return self.get_backend(kwargs.pop("backend"), inventory_path=kwargs.pop("inventory_path", None))

    def get_backend(self, backend, inventory_path=None):
        from earthkit.regrid.backends import get_backend

        if backend == "precomputed-local":
            backend = get_backend(backend, path_or_url=inventory_path)
        else:
            if inventory_path:
                raise ValueError(
                    f"Cannot use inventory_path={inventory_path} with backend={backend}. "
                    "Only available for backend='precomputed-local'."
                )
            backend = get_backend(backend)

        if not backend:
            raise ValueError(f"No backend={backend} found")

        return backend


class NumpyDataHandler(DataHandler):
    @staticmethod
    def match(values):
        import numpy as np

        return isinstance(values, np.ndarray)

    def regrid(self, values, **kwargs):
        in_grid = kwargs.pop("in_grid")
        out_grid = kwargs.pop("out_grid")
        backend = self.backend_from_kwargs(kwargs)
        return backend.regrid(values, in_grid, out_grid, **kwargs)


class FieldListDataHandler(DataHandler):
    @staticmethod
    def match(values):
        from earthkit.regrid.utils import is_module_loaded

        if not is_module_loaded("earthkit.data"):
            return False

        try:
            import earthkit.data

            return isinstance(values, earthkit.data.FieldList)
        except Exception:
            return False

    @staticmethod
    def input_gridspec(user_grid, field, index):
        in_grid = user_grid
        if in_grid is None:
            try:
                in_grid = field.metadata().gridspec
            except Exception as e:
                LOG.exception(f"Cannot get input gridspec from metadata for field[{index}]: {e}")
                raise
            if in_grid is None:
                raise ValueError(f"Cannot get input gridspec from metadata for field[{index}]")
        return in_grid

    def regrid(self, values, **kwargs):
        backend = self.backend_from_kwargs(kwargs)

        if hasattr(backend, "regrid_grib"):
            # TODO: remove this when ecCodes supports setting the gridSpec on a GRIB handle
            return self._regrid_grib(values, backend, **kwargs)
        else:
            return self._regrid_array(values, backend, **kwargs)

    def _regrid_array(self, values, backend, **kwargs):
        import earthkit.data

        ds = values
        in_grid = kwargs.pop("in_grid", None)
        if not in_grid:
            in_grid = None

        out_grid = kwargs.pop("out_grid")
        # TODO: refactor this when this limitation is removed
        from .gridspec import GridSpec

        out_grid = GridSpec.from_dict(out_grid)
        if not out_grid.is_regular_ll():
            raise ValueError("Fieldlists can only be regridded to global regular lat-lon target grids")

        r = earthkit.data.FieldList()
        for i, f in enumerate(ds):
            vv = f.to_numpy(flatten=True)

            in_grid_f = self.input_gridspec(in_grid, f, i)

            v_res, out_grid = backend.regrid(
                vv,
                in_grid_f,
                out_grid,
                output="values_gridspec",
                **kwargs,
            )
            md_res = f.metadata().override(gridspec=out_grid)
            r += ds.from_numpy(v_res, md_res)

        return r

    def _regrid_grib(self, values, backend, **kwargs):
        # TODO: remove this when ecCodes supports setting the gridSpec on a GRIB handle
        from earthkit.data.readers.grib.codes import GribField
        from earthkit.data.readers.grib.memory import GribFieldInMemory

        assert hasattr(backend, "regrid_grib")

        ds = values
        kwargs.pop("in_grid", None)
        out_grid = kwargs.pop("out_grid")
        kwargs.pop("output", None)

        r = []
        for i, f in enumerate(ds):
            if isinstance(f, GribField):
                message = f.message()
            elif hasattr(f, "handle"):
                from earthkit.data import create_encoder

                encoder = create_encoder("grib")
                message = encoder.encode(f).to_bytes()
            else:
                raise ValueError(f"field type={type(f)} is not supported in regrid!")

            v_res = backend.regrid_grib(message, out_grid, **kwargs)
            r.append(GribFieldInMemory.from_buffer(v_res))

        return ds.from_fields(r)


class FieldDataHandler(DataHandler):
    @staticmethod
    def match(values):
        from earthkit.regrid.utils import is_module_loaded

        if not is_module_loaded("earthkit.data"):
            return False

        try:
            import earthkit.data

            return isinstance(values, earthkit.data.Field)
        except Exception:
            return False

    def regrid(self, values, **kwargs):
        from earthkit.data import FieldList

        ds = FieldList.from_fields([values])
        return FIELDLIST_DATA_HANDLER.regrid(ds, **kwargs)[0]


class GribMessageDataHandler(DataHandler):
    @staticmethod
    def match(values):
        if isinstance(values, bytes):
            return True
        else:
            from io import BytesIO

            # TODO: add further checks to see if the object is a GRIB message
            if isinstance(values, BytesIO):
                return True
        return False

    def regrid(self, values, **kwargs):
        backend = self.backend_from_kwargs(kwargs)
        # backend = self.get_backend(kwargs.pop("backend"), matrix_source=kwargs.pop("matrix_source", None))
        if hasattr(backend, "regrid_grib"):
            if not isinstance(values, bytes):
                from io import BytesIO

                if isinstance(values, BytesIO):
                    values = values.getvalue()

            kwargs.pop("in_grid", None)
            return backend.regrid_grib(values, **kwargs)
        else:
            raise ValueError(f"regrid() does not support GRIB message input for {backend=}!")


class XarrayDataHandler(DataHandler):
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

    def regrid(self, values, **kwargs):
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

        ds_out = xr.apply_ufunc(
            functools.partial(
                NumpyDataHandler().regrid, in_grid=in_grid, out_grid=out_grid, **kwargs
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
        # self.set_coords(ds_out, out_grid, **kwargs)
        # ds_out.earthkit.set_grid(out_grid)

        return ds_out

    def set_coords(self, ds_out, out_grid, **kwargs):
        import earthkit.geo as ekg
        lat, lon = ekg.to_latlon(out_grid)
        ds_out.coords["latitude"] = lat
        ds_out.coords["longitude"] = lon


FIELDLIST_DATA_HANDLER = FieldListDataHandler()
DATA_HANDLERS = [NumpyDataHandler(), FIELDLIST_DATA_HANDLER, FieldDataHandler(), GribMessageDataHandler(), XarrayDataHandler()]


def get_data_handler(values):
    for h in DATA_HANDLERS:
        if h.match(values):
            return h

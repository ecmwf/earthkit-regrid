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

LOG = logging.getLogger(__name__)


class DataHandler(metaclass=ABCMeta):
    @abstractmethod
    def regrid(self, values, **kwargs):
        pass

    def backend_from_kwargs(self, kwargs):
        return self.get_backend(kwargs.pop("backend"), matrix_source=kwargs.pop("matrix_source", None))

    def get_backend(self, backend, matrix_source=None):
        from earthkit.regrid.backends import get_backend

        if backend == "local-matrix":
            backend = get_backend("local-matrix", path_or_url=matrix_source)
        else:
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
            r.append(GribFieldInMemory.from_buffer(v_res.getvalue()))

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
        from io import BytesIO

        # TODO: add further checks to see if the object is a GRIB message
        if isinstance(values, BytesIO):
            return True
        return False

    def regrid(self, values, **kwargs):
        backend = self.get_backend(kwargs.pop("backend"), matrix_source=kwargs.pop("matrix_source", None))
        if backend.hasattr(backend, "regrid_grib"):
            return backend.regrid_grib(values, **kwargs)
        else:
            raise ValueError(f"regrid() does not support GRIB message input for {backend=}!")


FIELDLIST_DATA_HANDLER = FieldListDataHandler()
DATA_HANDLERS = [NumpyDataHandler(), FIELDLIST_DATA_HANDLER, FieldDataHandler(), GribMessageDataHandler()]


def get_data_handler(values):
    for h in DATA_HANDLERS:
        if h.match(values):
            return h

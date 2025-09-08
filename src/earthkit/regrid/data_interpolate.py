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

import deprecation

LOG = logging.getLogger(__name__)

# TODO: this module is deprecated and will be removed in a future version.


class DataHandler(metaclass=ABCMeta):
    @abstractmethod
    def interpolate(self, values, **kwargs):
        pass

    def backend_from_kwargs(self, kwargs):
        if "backend" in kwargs:
            raise ValueError("backend should not be passed as a keyword argument to interpolate()")

        matrix_source = kwargs.pop("matrix_source", None)
        from earthkit.regrid.backends import get_backend

        if matrix_source is not None:
            backend = get_backend("precomputed", inventory=matrix_source)
        else:
            backend = get_backend("precomputed")

        if not backend:
            raise ValueError(f"No backend={backend} found")

        return backend


class NumpyDataHandler(DataHandler):
    @staticmethod
    def match(values):
        import numpy as np

        return isinstance(values, np.ndarray)

    @deprecation.deprecated(deprecated_in="0.5.0", removed_in=None, details="Use regrid() instead")
    def interpolate(self, values, **kwargs):
        in_grid = kwargs.pop("in_grid")
        out_grid = kwargs.pop("out_grid")
        backend = self.backend_from_kwargs(kwargs)
        return backend.interpolate(values, in_grid, out_grid, **kwargs)


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
                LOG.exception(
                    f"interpolate(): cannot get input gridspec from metadata for field[{index}]: {e}"
                )
                raise
            if in_grid is None:
                raise ValueError(f"interpolate(): cannot get input gridspec from metadata for field[{index}]")
        return in_grid

    @deprecation.deprecated(deprecated_in="0.5.0", removed_in=None, details="Use regrid() instead")
    def interpolate(self, values, **kwargs):
        backend = self.backend_from_kwargs(kwargs)

        import earthkit.data

        ds = values
        in_grid = kwargs.pop("in_grid")
        out_grid = kwargs.pop("out_grid")

        # TODO: refactor this when this limitation is removed
        from .gridspec import GridSpec

        out_grid = GridSpec.from_dict(out_grid)
        if not out_grid.is_regular_ll():
            raise ValueError(
                "interpolate(): Fieldlists can only be interpolated to global regular lat-lon target grids"
            )

        r = earthkit.data.FieldList()
        for i, f in enumerate(ds):
            vv = f.to_numpy(flatten=True)

            in_grid_f = self.input_gridspec(in_grid, f, i)

            v_res = backend.interpolate(
                vv,
                in_grid_f,
                out_grid,
                **kwargs,
            )
            md_res = f.metadata().override(gridspec=out_grid)
            r += ds.from_numpy(v_res, md_res)

        return r


DATA_HANDLERS = [NumpyDataHandler(), FieldListDataHandler()]


def get_data_handler(values):
    for h in DATA_HANDLERS:
        if h.match(values):
            return h

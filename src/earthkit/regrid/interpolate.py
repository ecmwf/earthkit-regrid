# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

LOG = logging.getLogger(__name__)


def interpolate(values, in_grid=None, out_grid=None, method="linear", backends=None, **kwargs):
    h = _find_data_handler(values)
    if h is None:
        raise ValueError(f"Cannot interpolate data with type={type(values)}")

    return h(values, in_grid=in_grid, out_grid=out_grid, method=method, backends=backends, **kwargs)


def _find_data_handler(values):
    for h in DATA_HANDLERS:
        if h.match(values):
            return h


class DataHandler:
    @staticmethod
    def _interpolate(values, in_grid, out_grid, **kwargs):
        from earthkit.regrid.backends import MANAGER

        method = kwargs.pop("method")
        user_backends = kwargs.pop("backends", None)
        backends = MANAGER.backends(user_backends)

        if not backends:
            raise ValueError(f"No backend found for {user_backends}")

        if len(backends) == 1:
            if backends[0].enabled:
                return backends[0].interpolate(values, in_grid, out_grid, method, **kwargs)
            raise ValueError("No backend could interpolate the data")
        else:
            errors = []
            for p in backends:
                if p.enabled:
                    LOG.debug(f"Trying backend {p}")
                    try:
                        return p.interpolate(values, in_grid, out_grid, method, **kwargs)
                    except Exception as e:
                        errors.append(e)

            raise ValueError("No backend could interpolate the data", errors)


class NumpyDataHandler(DataHandler):
    @staticmethod
    def match(values):
        import numpy as np

        return isinstance(values, np.ndarray)

    def __call__(self, values, **kwargs):
        in_grid = kwargs.pop("in_grid")
        out_grid = kwargs.pop("out_grid")
        return self._interpolate(values, in_grid, out_grid, **kwargs)


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

    def __call__(self, values, **kwargs):
        import earthkit.data

        ds = values
        in_grid = kwargs.pop("in_grid")
        # if in_grid is not None:
        #     raise ValueError(f"in_grid {in_grid} cannot be used for FieldList interpolation")
        out_grid = kwargs.pop("out_grid")

        r = earthkit.data.FieldList()
        for f in ds:
            vv = f.to_numpy(flatten=True)
            v_res = self._interpolate(
                vv,
                f.metadata().gridspec if in_grid is None else in_grid,
                out_grid,
                # method,
                **kwargs,
            )
            md_res = f.metadata().override(gridspec=out_grid)
            r += ds.from_numpy(v_res, md_res)

        return r


DATA_HANDLERS = [NumpyDataHandler(), FieldListDataHandler()]

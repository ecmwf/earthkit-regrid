# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from . import Backend


class MatrixBackend(Backend):
    name = "precomputed"
    system_inventory_id = "ecmwf"

    def __init__(self, inventory=None):
        self.path_or_url = inventory
        self.db = self.get_db(inventory)

    def regrid(self, values, in_grid, out_grid, interpolation):
        z, shape = self.db.find(in_grid, out_grid, interpolation)

        if z is None:
            raise ValueError(f"No precomputed interpolator found! {in_grid=} {out_grid=} {interpolation=}")

        # This should check for 1D (GG) and 2D (LL) matrices
        values = values.reshape(-1, 1)

        values = z @ values
        values = values.reshape(shape)

        return values, out_grid

        # if output == "values_gridspec":
        #     return values, out_grid
        # elif output == "values":
        #     return values
        # elif output == "gridspec":
        #     return out_grid

        # raise ValueError(f"Unknown output={output} for backend={self.name}")

    # TODO: will be removed
    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        z, shape = self.db.find(in_grid, out_grid, method, **kwargs)

        if z is None:
            raise ValueError(f"No matrix found! {in_grid=} {out_grid=} {method=}")

        # This should check for 1D (GG) and 2D (LL) matrices
        values = values.reshape(-1, 1)

        values = z @ values

        return values.reshape(shape)

    def get_db(self, path_or_url):
        if path_or_url is None or path_or_url == self.system_inventory_id:
            from .db import SYS_DB

            return SYS_DB
        elif path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            from .db import MatrixDb

            return MatrixDb.from_url(path_or_url)
        elif path_or_url:
            from .db import MatrixDb

            return MatrixDb.from_path(path_or_url)
        else:
            raise ValueError(f"Invalid path_or_url={path_or_url} for backend={self.name}")


# class LocalMatrixBackend(MatrixBackend):
#     name = "precomputed-local"
#     # path_config_key = "local-matrix-directories"

#     @cached_property
#     def db(self):
#         from .db import MatrixDb

#         return MatrixDb.from_path(self.path_or_url)


# class RemoteMatrixBackend(MatrixBackend):
#     name = "precomputed-remote"
#     # path_config_key = "remote-matrix-directories"

#     @cached_property
#     def db(self):
#         from .db import MatrixDb

#         return MatrixDb.from_url(self.path_or_url)


# class SystemRemoteMatrixBackend(RemoteMatrixBackend):
#     name = "precomputed"
#     # path_config_key = None

#     @cached_property
#     def db(self):
#         from .db import SYS_DB

#         return SYS_DB


# backend = {v.name: v for v in [LocalMatrixBackend, RemoteMatrixBackend, SystemRemoteMatrixBackend]}

backend = MatrixBackend

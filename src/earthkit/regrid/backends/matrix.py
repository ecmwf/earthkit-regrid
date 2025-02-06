# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from abc import abstractmethod
from functools import cached_property

from . import Backend


class MatrixBackend(Backend):
    def __init__(self, path_or_url=None):
        self.path_or_url = path_or_url

    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        z, shape = self.db.find(in_grid, out_grid, method, **kwargs)

        if z is None:
            raise ValueError(f"No matrix found! {in_grid=} {out_grid=} {method=}")

        # This should check for 1D (GG) and 2D (LL) matrices
        values = values.reshape(-1, 1)

        # print("values.shape", values.shape)
        # print("z.shape", z.shape)

        values = z @ values

        # print("values.shape", values.shape)

        return values.reshape(shape)

    @property
    @abstractmethod
    def db(self):
        pass


class LocalMatrixBackend(MatrixBackend):
    name = "local-matrix"
    path_config_key = "local-matrix-directories"

    @cached_property
    def db(self):
        from .db import MatrixDb

        return MatrixDb.from_path(self.path_or_url)


class RemoteMatrixBackend(MatrixBackend):
    name = "remote-matrix"
    path_config_key = "remote-matrix-directories"

    @cached_property
    def db(self):
        from .db import MatrixDb

        return MatrixDb.from_url(self.path_or_url)


class SystemRemoteMatrixBackend(RemoteMatrixBackend):
    name = "system-matrix"
    path_config_key = None

    @cached_property
    def db(self):
        from .db import SYS_DB

        return SYS_DB


backend = {v.name: v for v in [LocalMatrixBackend, RemoteMatrixBackend, SystemRemoteMatrixBackend]}

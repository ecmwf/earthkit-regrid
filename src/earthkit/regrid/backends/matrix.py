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

from earthkit.utils.array import backend_from_array, ArrayBackend

from . import Backend



def npz_to_backend(z, backend: ArrayBackend):
    """Convert a numpy sparse matrix to the specified backend."""
    xp = backend.namespace
    if backend.name == "numpy":
        return z
    elif backend.name == "torch":
        return xp.sparse_csr_tensor(
            z.indptr,
            z.indices,
            z.data,
            size=z.shape,
        )
    elif backend.name == "cupy":
        return xp.sparse.csr_matrix(
            z,
            shape=z.shape,
        )
    
    raise NotImplementedError(f"Unsupported backend: {backend.name}. Supported backends are: numpy, torch, cupy.")


class MatrixBackend(Backend):
    def __init__(self, path_or_url=None):
        self.path_or_url = path_or_url

    def regrid(self, values, in_grid, out_grid, interpolation, **kwargs):
        z, shape = self.db.find(in_grid, out_grid, interpolation, **kwargs)

        if z is None:
            raise ValueError(f"No precomputed interpolator found! {in_grid=} {out_grid=} {interpolation=}")

        array_backend = backend_from_array(values)

        # This should check for 1D (GG) and 2D (LL) matrices
        values = values.reshape(-1, 1)
        z =  npz_to_backend(z, array_backend)

        if array_backend.name == 'torch': # TODO: Use from utils
            z = z.to(values)
        values = z @ values

        return values.reshape(shape), out_grid

    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        return self.regrid(values, in_grid, out_grid, method, **kwargs)[0]

    @property
    @abstractmethod
    def db(self):
        pass


class LocalMatrixBackend(MatrixBackend):
    name = "local-matrix"
    # path_config_key = "local-matrix-directories"

    @cached_property
    def db(self):
        from .db import MatrixDb

        return MatrixDb.from_path(self.path_or_url)


class RemoteMatrixBackend(MatrixBackend):
    name = "remote-matrix"
    # path_config_key = "remote-matrix-directories"

    @cached_property
    def db(self):
        from .db import MatrixDb

        return MatrixDb.from_url(self.path_or_url)


class SystemRemoteMatrixBackend(RemoteMatrixBackend):
    name = "system-matrix"
    # path_config_key = None

    @cached_property
    def db(self):
        from .db import SYS_DB

        return SYS_DB


backend = {v.name: v for v in [LocalMatrixBackend, RemoteMatrixBackend, SystemRemoteMatrixBackend]}

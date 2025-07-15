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
from typing import TYPE_CHECKING

from earthkit.utils.array import backend_from_array
from scipy.sparse import load_npz

from . import Backend

if TYPE_CHECKING:
    from .db import MatrixDb


class BaseMatrixLoader:
    name: str

    def __init__(self, device=None, dtype=None):
        self.device = device
        self.dtype = dtype

    @abstractmethod
    def load(self, path):
        """
        Load the matrix from the given path.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def __hash__(self):
        return hash((self.__class__, str(self.device), str(self.dtype)))


class NumpyMatrixLoader(BaseMatrixLoader):
    name = "numpy"

    def load(self, path):
        return load_npz(path).astype(self.dtype)


class TorchMatrixLoader(BaseMatrixLoader):
    name = "torch"

    def load(self, path):
        z = load_npz(path)
        import torch

        return torch.sparse_csr_tensor(
            z.indptr,
            z.indices,
            z.data,
            size=z.shape,
            device=self.device,
            dtype=self.dtype,
        )


class CupyMatrixLoader(BaseMatrixLoader):
    name = "cupy"

    def load(self, path):
        import cupy as cp

        z = load_npz(path)
        return cp.sparse.csr_matrix((z.data, z.indices, z.indptr), shape=z.shape, dtype=self.dtype)


MATRIX_LOADERS = [NumpyMatrixLoader, TorchMatrixLoader, CupyMatrixLoader]


class MatrixBackend(Backend):
    def __init__(self, path_or_url=None):
        self.path_or_url = path_or_url

    def _get_matrix_loader(self, values) -> BaseMatrixLoader:
        values_backend = backend_from_array(values).name

        for loader in MATRIX_LOADERS:
            if loader.name == values_backend:
                return loader(getattr(values, "device", None), getattr(values, "dtype", None))

        raise ValueError(
            f"Unsupported backend: {values_backend}. Supported backends are numpy, torch, and cupy."
        )

    def regrid(self, values, in_grid, out_grid, interpolation, output=Backend.outputs[0], **kwargs):

        matrix_loader = self._get_matrix_loader(values)
        z, shape = self.db.find(in_grid, out_grid, interpolation, matrix_loader, **kwargs)

        if z is None:
            raise ValueError(f"No precomputed interpolator found! {in_grid=} {out_grid=} {interpolation=}")

        # This should check for 1D (GG) and 2D (LL) matrices
        values = values.reshape(-1, 1)

        values = z @ values
        values = values.reshape(shape)

        if output == "values_gridspec":
            return values, out_grid
        elif output == "values":
            return values
        elif output == "gridspec":
            return out_grid

        raise ValueError(f"Unknown output={output} for backend={self.name}")

    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        return self.regrid(values, in_grid, out_grid, method, **kwargs)[0]

    @property
    @abstractmethod
    def db(self) -> "MatrixDb":
        pass


class LocalMatrixBackend(MatrixBackend):
    name = "precomputed-local"
    # path_config_key = "local-matrix-directories"

    @cached_property
    def db(self):
        from .db import MatrixDb

        return MatrixDb.from_path(self.path_or_url)


class RemoteMatrixBackend(MatrixBackend):
    name = "precomputed-remote"
    # path_config_key = "remote-matrix-directories"

    @cached_property
    def db(self):
        from .db import MatrixDb

        return MatrixDb.from_url(self.path_or_url)


class SystemRemoteMatrixBackend(RemoteMatrixBackend):
    name = "precomputed"
    # path_config_key = None

    @cached_property
    def db(self):
        from .db import SYS_DB

        return SYS_DB


backend = {v.name: v for v in [LocalMatrixBackend, RemoteMatrixBackend, SystemRemoteMatrixBackend]}

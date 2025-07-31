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

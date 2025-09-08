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


OPTIONAL_BACKENDS_KWARGS = ["inventory"]


class DataHandler(metaclass=ABCMeta):
    @abstractmethod
    def regrid(self, values, **kwargs):
        pass

    def backend_from_kwargs(self, kwargs):
        backend = kwargs.pop("backend", None)
        if backend is None:
            raise ValueError("Missing 'backend' keyword argument")

        b_kwargs = {}
        for k in OPTIONAL_BACKENDS_KWARGS:
            if k in kwargs:
                b_kwargs[k] = kwargs.pop(k)
        return self.get_backend(backend, **b_kwargs)

    def get_backend(self, backend, **backend_kwargs):
        from earthkit.regrid.backends import get_backend

        backend = get_backend(backend, **backend_kwargs)

        if not backend:
            raise ValueError(f"No backend={backend} found")

        return backend

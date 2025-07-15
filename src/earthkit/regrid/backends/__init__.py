# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
import threading
from abc import ABCMeta
from abc import abstractmethod

# from collections import namedtuple
from importlib import import_module

from earthkit.regrid.utils.config import CONFIG

LOG = logging.getLogger(__name__)


class Backend(metaclass=ABCMeta):
    name = None
    path_config_key = None
    enabled = True

    outputs = ("values_gridspec", "values", "gridspec")

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def regrid(self, values, in_grid, out_grid, method, **kwargs):
        pass

    # @abstractmethod
    # def regrid(
    #     self,
    #     values,
    #     in_grid,
    #     out_grid,
    #     interpolation,
    #     output="values_gridspec",
    #     **kwargs,
    # ):
    #     pass


class BackendLoader:
    kind = "backend"

    def load_module(self, module):
        return import_module(module, package=__name__).backend

    def load_entry(self, entry):
        entry = entry.load()
        if callable(entry):
            return entry
        return entry.backend

    def load_remote(self, name):
        return None


class BackendMaker:
    BACKENDS = {}
    BACKEND_OBJECTS = {}

    def __init__(self):
        self.BACKENDS = self._builtins()

    def _make_key(self, name, *args, **kwargs):
        if args or kwargs:
            key = [name, *args, *list(kwargs.items())]
            return tuple(key)
        else:
            return name

    def __call__(self, name, *args, **kwargs):
        loader = BackendLoader()

        key = self._make_key(name, *args, **kwargs)
        if key in self.BACKEND_OBJECTS:
            return self.BACKEND_OBJECTS[key]

        if name in self.BACKENDS:
            klass = self.BACKENDS[name]
        else:
            # TODO: implement a plugin loader
            raise ValueError(f"Unknown backend: {name}")

        backend = klass(*args, **kwargs)
        self.BACKEND_OBJECTS[key] = backend

        return backend

    def plugin_names(self):
        """Return the list of plugin names."""
        from earthkit.regrid.utils.plugins import load_plugins

        return list(load_plugins("backend").keys())

    def _builtins(self):
        """Scan for built-in backend classes."""
        r = {}
        here = os.path.dirname(__file__)
        for path in sorted(os.listdir(here)):
            if path[0] in ("_", "."):
                continue

            if path.endswith(".py") or os.path.isdir(os.path.join(here, path)):
                name, _ = os.path.splitext(path)
                try:
                    module = import_module(f".{name}", package=__name__)
                    if hasattr(module, "backend"):
                        w = getattr(module, "backend")
                        if isinstance(w, dict):
                            for k, v in w.items():
                                r[k] = v
                        else:
                            r[name] = w
                except Exception:
                    LOG.exception("Error loading backend %s", name)

        LOG.debug(f"built-in backend classes: {r}")
        return r


MAKER = BackendMaker()


def get_backend(name, *args, **kwargs):
    """Get a backend by name."""
    return MAKER(name, *args, **kwargs)

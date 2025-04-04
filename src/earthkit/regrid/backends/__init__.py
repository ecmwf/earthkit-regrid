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
from typing import Literal

from earthkit.regrid.utils.config import CONFIG

LOG = logging.getLogger(__name__)

# InterpolatorKey = namedtuple("InterpolatorKey", ["name", "path", "path_config_key", "plugin"])

# DEFAULT_ORDER = ["local-matrix", "plugins", "remote-matrix", "system-matrix", "mir"]


class Backend(metaclass=ABCMeta):
    name = None
    path_config_key = None
    enabled = True

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def regrid(self, values, in_grid, out_grid, method, **kwargs):
        pass


class LazyBackend:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.lock = threading.Lock()
        self._backend = None
        self._exception = None

    @property
    def backend(self):
        if self._backend is None:
            with self.lock:
                try:
                    LOG.debug(f"Making backend object name={self.name}")
                    self._backend = MAKER(self.name, *self.args, **self.kwargs)
                    LOG.debug(f"Created backend object {self._backend}")
                except Exception as e:
                    LOG.exception(e)
                    self._exception = e
                    raise
        return self._backend

    def interpolate(self, *args, **kwargs):
        return self.backend.interpolate(*args, **kwargs)

    def __getattr__(self, name):
        if self._exception is not None:
            raise self._exception(name)
        assert name != "interpolate"
        return getattr(self.backend, name)


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
            from earthkit.regrid.utils.plugins import find_plugin

            # klass = find_plugin(os.path.dirname(__file__), name, loader)
            klass = find_plugin([], name, loader)
            self.BACKENDS[name] = klass

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


# class BackendListCache:
#     def __init__(self):
#         self._cache = {}

#     def get(self, order, names):
#         def _copy(x):
#             if x is None:
#                 return None
#             return tuple(x)

#         cache_key = (_copy(order), _copy(names))
#         if cache_key in self._cache:
#             return self._cache[cache_key]

#     def add(self, order, names, value):
#         def _copy(x):
#             if x is None:
#                 return None
#             return tuple(x)

#         cache_key = (_copy(order), _copy(names))
#         self._cache[cache_key] = value

#     def clear(self):
#         self._cache.clear()


# class BackendManager:
#     BACKENDS = {}

#     def __init__(self, *args, **kwargs):
#         self.order = []
#         self._cache = BackendListCache()
#         self.lock = threading.Lock()
#         self.update()

#     def update(self):
#         with self.lock:
#             LOG.debug("Update backends")
#             if not self.BACKENDS:
#                 self._init_backends()
#             else:
#                 self._update_backends()

#             self.order = self._to_list(CONFIG.get("backends", None), keep_none=True)
#             LOG.debug(f"backend order: {self.order}")

#     def backends(self, backend=None):
#         """Filter and reorder backends based on the order and names."""
#         with self.lock:
#             names = self._to_list(backend, keep_none=True)

#             if r := self._cache.get(self.order, names):
#                 return r

#             if isinstance(names, str):
#                 if v := self._single(names):
#                     return [v]

#             r = []
#             if names:
#                 _order = list(names)
#             else:
#                 _order = self.order or DEFAULT_ORDER

#             # print("names", names)
#             # print("order", _order)
#             # print("self", self.INTERPOLATORS.keys())

#             collected = {}
#             for name in _order:
#                 # print("name", name)
#                 for key, p in self.BACKENDS.items():
#                     # print(" key", key)
#                     if key not in collected:
#                         # if p.enabled:
#                         found = False
#                         if key.name == name:
#                             # print("  (bt) -> p", p)
#                             found = True
#                         elif name == "plugins":
#                             if key.plugin:
#                                 # print("  (pl) -> p", p)
#                                 found = True
#                         if found:
#                             collected[key] = p
#                             break

#             LOG.debug(f" collected: {collected}")

#             r = list(collected.values())

#             self._cache.add(self.order, names, r)

#             return r

#     def _single(self, name):
#         """Must be called within a lock"""
#         for k, v in self.BACKENDS.items():
#             if k.name == name and k.path is None:
#                 return v

#     def _to_list(self, value, keep_none=False):
#         if value is None:
#             if keep_none:
#                 return None
#             return []
#         if isinstance(value, str):
#             lst = value.split(",")
#         elif isinstance(value, list):
#             lst = [*value]
#         else:
#             lst = list(value)

#         lst = [x.strip() for x in lst if x.strip()]
#         if lst and lst[0] == "":
#             lst = []

#         return lst

#     def _config_paths(self, key):
#         dirs = CONFIG.get(key, [])
#         dirs = self._to_list(dirs, keep_none=False)
#         for d in dirs:
#             if not d:
#                 raise ValueError(f"Empty path in config option {key}={CONFIG.get(key, [])}")
#         return dirs

#     def _init_backends(self):
#         """Must be called within a lock"""
#         LOG.debug("Initial registration of backends:")
#         self.BACKENDS = {}
#         for name, v in MAKER.BACKENDS.items():
#             # backends with a path
#             if v.path_config_key is not None:
#                 for d in self._config_paths(v.path_config_key):
#                     key = InterpolatorKey(name, d, v.path_config_key, False)
#                     LOG.debug(f" add: {key}")
#                     self.BACKENDS[key] = LazyBackend(name, d)
#             # single backends
#             else:
#                 key = InterpolatorKey(name, None, None, False)
#                 LOG.debug(f" add: {key}")
#                 self.BACKENDS[key] = LazyBackend(name)

#         # plugins
#         for name in MAKER.plugin_names():
#             key = InterpolatorKey(name, None, None, True)
#             if key not in self.BACKENDS:
#                 LOG.debug(" add:", key)
#                 self.BACKENDS[key] = LazyBackend(name, plugin=True)

#         assert self.BACKENDS

#     def _update_backends(self):
#         """Must be called within a lock"""
#         LOG.debug("Adjustment to config update:")
#         # existing backends with a path
#         changed = False
#         for key in list(self.BACKENDS.keys()):
#             if key in self.BACKENDS:
#                 if key.path_config_key is not None:
#                     dirs = self._config_paths(key.path_config_key)
#                     # add new paths
#                     for d in dirs:
#                         key = InterpolatorKey(name, d, key.path_config_key, False)
#                         if key not in self.BACKENDS:
#                             LOG.debug(f" add: {key}")
#                             self.BACKENDS[key] = LazyBackend(name, d)
#                             changed = True
#                     # remove paths not used anymore
#                     for k in list(self.BACKENDS.keys()):
#                         if k.name == key.name and k.path not in dirs:
#                             LOG.debug(f" remove: {k}")
#                             del self.BACKENDS[k]
#                             changed = True

#         # new backends with a path
#         for name, v in MAKER.BACKENDS.items():
#             if v.path_config_key is not None and not any(k.name == name for k in self.BACKENDS):
#                 for d in self._config_paths(v.path_config_key):
#                     key = InterpolatorKey(name, d, v.path_config_key, False)
#                     LOG.debug(f" add: {key}")
#                     self.BACKENDS[key] = LazyBackend(name, d)
#                     changed = True

#         if changed:
#             self._cache.clear()


# MANAGER = BackendManager()

# CONFIG.on_change(MANAGER.update)

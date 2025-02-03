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
from collections import namedtuple
from importlib import import_module

from earthkit.regrid.utils.config import CONFIG

LOG = logging.getLogger(__name__)

InterpolatorKey = namedtuple("InterpolatorKey", ["name", "path", "path_config_key", "plugin"])

DEFAULT_ORDER = ["local-matrix", "plugins", "remote-matrix", "system-matrix", "mir", "other"]


class Interpolator(metaclass=ABCMeta):
    name = None
    path_config_key = None
    enabled = True

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        pass


class LazyInterpolator:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.lock = threading.Lock()
        self._interpolator = None
        self._exception = None

    @property
    def interpolator(self):
        if self._interpolator is None:
            with self.lock:
                try:
                    LOG.debug(f"Making interpolator object name={self.name}")
                    self._interpolator = MAKER(self.name, *self.args, **self.kwargs)
                    LOG.debug(f"Created interpolator object {self._interpolator}")
                except Exception as e:
                    LOG.exception(e)
                    self._exception = e
                    raise
        return self._interpolator

    def interpolate(self, *args, **kwargs):
        return self.interpolator.interpolate(*args, **kwargs)

    def __getattr__(self, name):
        if self._exception is not None:
            raise self._exception(name)
        assert name != "interpolate"
        return getattr(self.interpolator, name)


class InterpolatorLoader:
    kind = "interpolator"

    def load_module(self, module):
        return import_module(module, package=__name__).interpolator

    def load_entry(self, entry):
        entry = entry.load()
        if callable(entry):
            return entry
        return entry.interpolator

    def load_remote(self, name):
        return None


class InterpolatorMaker:
    INTERPOLATORS = {}

    def __init__(self):
        self.INTERPOLATORS = self._builtins()

    def __call__(self, name, *args, **kwargs):
        loader = InterpolatorLoader()

        if name in self.INTERPOLATORS:
            klass = self.INTERPOLATORS[name]
        else:
            from earthkit.regrid.utils.plugins import find_plugin

            # klass = find_plugin(os.path.dirname(__file__), name, loader)
            klass = find_plugin([], name, loader)
            self.INTERPOLATORS[name] = klass

        interpolator = klass(*args, **kwargs)

        if getattr(interpolator, "name", None) is None:
            interpolator.name = name

        return interpolator

    def plugin_names(self):
        """Return the list of plugin names."""
        from earthkit.regrid.utils.plugins import load_plugins

        return list(load_plugins("interpolator").keys())

    def _builtins(self):
        """Scan for built-in interpolator classes."""
        r = {}
        here = os.path.dirname(__file__)
        for path in sorted(os.listdir(here)):
            if path[0] in ("_", "."):
                continue

            if path.endswith(".py") or os.path.isdir(os.path.join(here, path)):
                name, _ = os.path.splitext(path)
                try:
                    module = import_module(f".{name}", package=__name__)
                    if hasattr(module, "interpolator"):
                        w = getattr(module, "interpolator")
                        if isinstance(w, dict):
                            for k, v in w.items():
                                r[k] = v
                        else:
                            r[name] = w
                except Exception:
                    LOG.exception("Error loading interpolator %s", name)

        LOG.debug(f"built-in interpolator classes: {r}")
        return r


MAKER = InterpolatorMaker()


class InterpolatorListCache:
    def __init__(self):
        self._cache = {}

    def get(self, order, names):
        def _copy(x):
            if x is None:
                return None
            return tuple(x)

        cache_key = (_copy(order), _copy(names))
        if cache_key in self._cache:
            return self._cache[cache_key]

    def add(self, order, names, value):
        def _copy(x):
            if x is None:
                return None
            return tuple(x)

        cache_key = (_copy(order), _copy(names))
        self._cache[cache_key] = value

    def clear(self):
        self._cache.clear()


class InterpolatorManager:
    INTERPOLATORS = {}

    def __init__(self, *args, **kwargs):
        self.order = []
        self._cache = InterpolatorListCache()
        self.lock = threading.Lock()
        self.update()

    def update(self):
        with self.lock:
            LOG.debug("Update interpolators")
            if not self.INTERPOLATORS:
                self._init_interpolators()
            else:
                self._update_interpolators()

            self.order = self._to_list(CONFIG.get("interpolator-order", None), keep_none=True)
            LOG.debug(f"interpolator order: {self.order}")

    def interpolators(self, interpolator=None):
        """Filter and reorder interpolators based on the order and names."""
        with self.lock:
            names = self._to_list(interpolator, keep_none=True)

            if r := self._cache.get(self.order, names):
                return r

            if isinstance(names, str):
                if v := self._single(names):
                    return [v]

            r = []
            if names:
                _order = list(names)
            else:
                _order = self.order or DEFAULT_ORDER

            # print("names", names)
            # print("order", _order)
            # print("self", self.INTERPOLATORS.keys())

            collected = {}
            for name in _order:
                # print("name", name)
                for key, p in self.INTERPOLATORS.items():
                    # print(" key", key)
                    if key not in collected:
                        # if p.enabled:
                        found = False
                        if key.name == name:
                            # print("  (bt) -> p", p)
                            found = True
                        elif name == "plugins":
                            if key.plugin:
                                # print("  (pl) -> p", p)
                                found = True
                        elif name == "other":
                            if not key.plugin:
                                # print("  (ot) -> p", p)
                                found = True

                        if found:
                            collected[key] = p
                            break

            LOG.debug(f" collected: {collected}")

            r = list(collected.values())

            self._cache.add(self.order, names, r)

            return r

    def _single(self, name):
        """Must be called within a lock"""
        for k, v in self.INTERPOLATORS.items():
            if k.name == name and k.path is None:
                return v

    def _to_list(self, value, keep_none=False):
        if value is None:
            if keep_none:
                return None
            return []
        if isinstance(value, str):
            lst = value.split(",")
        elif isinstance(value, list):
            lst = [*value]
        else:
            lst = list(value)

        lst = [x.strip() for x in lst if x.strip()]
        if lst and lst[0] == "":
            lst = []

        return lst

    def _config_paths(self, key):
        dirs = CONFIG.get(key, [])
        dirs = self._to_list(dirs, keep_none=False)
        for d in dirs:
            if not d:
                raise ValueError(f"Empty path in config option {key}={CONFIG.get(key, [])}")
        return dirs

    def _init_interpolators(self):
        """Must be called within a lock"""
        LOG.debug("Initial registration of interpolators:")
        self.INTERPOLATORS = {}
        for name, v in MAKER.INTERPOLATORS.items():
            # interpolators with a path
            if v.path_config_key is not None:
                for d in self._config_paths(v.path_config_key):
                    key = InterpolatorKey(name, d, v.path_config_key, False)
                    LOG.debug(f" add: {key}")
                    self.INTERPOLATORS[key] = LazyInterpolator(name, d)
            # single interpolators
            else:
                key = InterpolatorKey(name, None, None, False)
                LOG.debug(f" add: {key}")
                self.INTERPOLATORS[key] = LazyInterpolator(name)

        # plugins
        for name in MAKER.plugin_names():
            key = InterpolatorKey(name, None, None, True)
            if key not in self.INTERPOLATORS:
                LOG.debug(" add:", key)
                self.INTERPOLATORS[key] = LazyInterpolator(name, plugin=True)

        assert self.INTERPOLATORS

    def _update_interpolators(self):
        """Must be called within a lock"""
        LOG.debug("Adjustment to config update:")
        # existing interpolators with a path
        changed = False
        for key in list(self.INTERPOLATORS.keys()):
            if key in self.INTERPOLATORS:
                if key.path_config_key is not None:
                    dirs = self._config_paths(key.path_config_key)
                    # add new paths
                    for d in dirs:
                        key = InterpolatorKey(name, d, key.path_config_key, False)
                        if key not in self.INTERPOLATORS:
                            LOG.debug(f" add: {key}")
                            self.INTERPOLATORS[key] = LazyInterpolator(name, d)
                            changed = True
                    # remove paths not used anymore
                    for k in list(self.INTERPOLATORS.keys()):
                        if k.name == key.name and k.path not in dirs:
                            LOG.debug(f" remove: {k}")
                            del self.INTERPOLATORS[k]
                            changed = True

        # new interpolators with a path
        for name, v in MAKER.INTERPOLATORS.items():
            if v.path_config_key is not None and not any(k.name == name for k in self.INTERPOLATORS):
                for d in self._config_paths(v.path_config_key):
                    key = InterpolatorKey(name, d, v.path_config_key, False)
                    LOG.debug(f" add: {key}")
                    self.INTERPOLATORS[key] = LazyInterpolator(name, d)
                    changed = True

        if changed:
            self._cache.clear()


MANAGER = InterpolatorManager()

CONFIG.on_change(MANAGER.update)

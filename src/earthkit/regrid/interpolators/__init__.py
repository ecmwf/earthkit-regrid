# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import threading
from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple

from earthkit.regrid.utils.config import CONFIG

ItemKey = namedtuple("ItemKey", ["name", "path"])


DEFAULT_ORDER = ["local-matrix", "plugins", "remote-matrix", "system-matrix", "mir"]
BUILT_IN_INTERPOLATORS = {"local-matrix", "remote-matrix", "system-matrix", "mir"}
SINGLE_INTERPOLATORS = {"system-matrix", "mir"}


class Interpolator(metaclass=ABCMeta):
    enabled = True

    @abstractmethod
    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        pass


def select(order, names, interpolators):
    """Filter and reorder interpolators based on the order and names."""
    if isinstance(names, str):
        if names in SINGLE_INTERPOLATORS:
            return [p for k, p in interpolators.items() if k.name == names]

    r = []
    if names:
        _order = list(names)
    else:
        _order = order or DEFAULT_ORDER

    print("names", names)
    print("order", _order)

    for m in _order:
        print("m", m)
        for k, p in interpolators.items():
            print(" k", k)
            if p.enabled and k.name == m or (m == "plugins" and k.name not in BUILT_IN_INTERPOLATORS):
                print("  -> p", p)
                r.append(p)

    return r


class InterpolatorManager:
    INTERPOLATORS = {}

    def __init__(self, *args, policy="all", **kwargs):
        self.order = []
        self.lock = threading.Lock()
        self.update()

    def update(self):
        with self.lock:
            self.INTERPOLATORS.clear()
            self.INTERPOLATORS.update(self._local())
            self.INTERPOLATORS.update(self._remote())
            self.INTERPOLATORS.update(self._mir())

            from earthkit.regrid.utils.config import CONFIG

            self.order = CONFIG.get("interpolators", []) or []

    def interpolators(self, interpolator=None):
        with self.lock:
            return select(self.order, interpolator, self.INTERPOLATORS)

    def _local(self):
        from earthkit.regrid.utils.config import CONFIG

        from .matrix import LocalMatrixInterpolator

        dirs = CONFIG.get("local-matrix-directories", [])
        if dirs is None:
            dirs = []
        if isinstance(dirs, str):
            dirs = [dirs]

        r = {}
        for d in dirs:
            r[ItemKey("local-matrix", d)] = LocalMatrixInterpolator(d)
        return r

    def _remote(self):
        from earthkit.regrid.utils.config import CONFIG

        from .matrix import RemoteMatrixInterpolator
        from .matrix import SystemRemoteMatrixInterpolator

        dirs = CONFIG.get("remote-matrix-directories", [])
        if dirs is None:
            dirs = []
        if isinstance(dirs, str):
            dirs = [dirs]

        r = {}
        for d in dirs:
            r[ItemKey("remote-matrix", d)] = RemoteMatrixInterpolator(d)

        r[ItemKey("system-matrix", None)] = SystemRemoteMatrixInterpolator()

        return r

    def _mir(self):
        from .mir import MirInterpolator

        return {ItemKey("mir", None): MirInterpolator()}


MANAGER = InterpolatorManager()

# def add_matrix_source(path):
#     global DB_LIST
#     for item in DB_LIST[1:]:
#         if item.matrix_source() == path:
#             return item
#     db = MatrixDb.from_path(path)
#     DB_LIST.append(db)s
#     return db


# def find(*args, matrix_source=None, **kwargs):
#     if matrix_source is None:
#         return SYS_DB.find(*args, **kwargs)
#     else:
#         db = add_matrix_source(matrix_source)
#         return db.find(*args, **kwargs)


# class Backend(metaclass=ABCMeta):
#     @abstractmethod
#     def interpolate(self, values, in_grid, out_grid, method, **kwargs):
#         pass


# class BackendLoader:
#     kind = "backend"

#     def load_module(self, module):
#         return import_module(module, package=__name__).backend

#     def load_entry(self, entry):
#         entry = entry.load()
#         if callable(entry):
#             return entry
#         return entry.backend

#     def load_remote(self, name):
#         return None


# class BackendMaker:
#     BACKENDS = {}

#     def __init__(self):
#         # Preregister the most important backends
#         from .mir import MirBackend
#         from .matrix import LocalMatrixBackend
#         from .matrix import RemoteMatrixBackend

#         self.BACKENDS["mir"] = MirBackend
#         self.BACKENDS["local"] = LocalMatrixBackend
#         self.BACKENDS["remote"] = RemoteMatrixBackend

#     def __call__(self, name, *args, **kwargs):
#         loader = BackendLoader()

#         if name in self.BACKENDS:
#             klass = self.BACKENDS[name]
#         else:
#             klass = find_plugin(os.path.dirname(__file__), name, loader)
#             self.BACKENDS[name] = klass

#         backend = klass(*args, **kwargs)

#         if getattr(backend, "name", None) is None:
#             backend.name = name

#         return backend

#     def __getattr__(self, name):
#         return self(name.replace("_", "-"))


# get_backend = BackendMaker()

CONFIG.on_change(MANAGER.update)

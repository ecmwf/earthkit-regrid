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

BackendKey = namedtuple("BackendKey", ["name", "path"])


DEFAULT_ORDER = ["local-matrix", "plugins", "remote-matrix", "system-matrix", "mir"]
BUILT_IN_BACKENDS = {"local-matrix", "remote-matrix", "system-matrix", "mir"}
SINGLE_BACKENDS = {"system-matrix", "mir"}


class Backend(metaclass=ABCMeta):
    enabled = True

    @abstractmethod
    def interpolate(self, values, in_grid, out_grid, method, **kwargs):
        pass


def select(order, names, backends):
    """Filter backends based on the order and names."""
    if isinstance(names, str):
        if names in SINGLE_BACKENDS:
            return [b for k, b in backends.items() if k.name == names]

    r = []
    if names:
        _order = list(names)
    else:
        _order = order or DEFAULT_ORDER

    print("names", names)
    print("order", _order)

    for m in _order:
        print("m", m)
        for k, b in backends.items():
            print(" k", k)
            if b.enabled and k.name == m or (m == "plugins" and k.name not in BUILT_IN_BACKENDS):
                print("  -> b", b)
                r.append(b)

    return r


# class BackendOrder:
#     DEFAULT_ORDER = ["local-matrix", "plugins", "remote-matrix", "system-matrix", "mir"]
#     BUILT_IN = {"local-matrix", "remote-matrix", "system-matrix", "mir"}
#     UNIQUE = {"system-matrix", "mir"}

#     def select(self, order, names, backends):
#         if isinstance(names, str):
#             if names in self.UNIQUE:
#                 return [b for k, b in backends.items() if k.name == names]

#         r = []
#         if names:
#             _order = list(names)
#         else:
#             _order = order or self.DEFAULT_ORDER

#         print("names", names)
#         print("order", _order)

#         for m in _order:
#             print("m", m)
#             for k, b in backends.items():
#                 print(" k", k)
#                 if k.name == m or (m == "plugins" and k.name not in self.BUILT_IN):
#                     print("  -> b", b)
#                     r.append(b)

#         return r


# BACKEND_ORDER = BackendOrder()


class BackendManager:
    BACKENDS = {}

    def __init__(self, *args, policy="all", **kwargs):
        self.order = []
        # self._has_settings = False
        self.lock = threading.Lock()
        # self.update(*args, **kwargs)

        # # initialise the backend list
        # self.BACKENDS.update(self.local())
        # self.BACKENDS.update(self.remote())
        # self.BACKENDS.update(self.mir())
        self.update()

        print("BACKENDS", self.BACKENDS)

    def update(self):
        with self.lock:
            self.BACKENDS.clear()
            self.BACKENDS.update(self._local())
            self.BACKENDS.update(self._remote())
            self.BACKENDS.update(self._mir())

            from earthkit.regrid.utils.config import CONFIG

            self.order = CONFIG.get("backend-order", []) or []

    def backends(self, backend=None):
        with self.lock:
            return select(self.order, backend, self.BACKENDS)

    def _local(self):
        from earthkit.regrid.utils.config import CONFIG

        from .matrix import LocalMatrixBackend

        dirs = CONFIG.get("local-matrix-directories", [])
        if dirs is None:
            dirs = []
        if isinstance(dirs, str):
            dirs = [dirs]

        r = {}
        for d in dirs:
            r[BackendKey("local-matrix", d)] = LocalMatrixBackend(d)
        return r

    def _remote(self):
        from earthkit.regrid.utils.config import CONFIG

        from .matrix import RemoteMatrixBackend
        from .matrix import SystemRemoteMatrixBackend

        dirs = CONFIG.get("remote-matrix-directories", [])
        if dirs is None:
            dirs = []
        if isinstance(dirs, str):
            dirs = [dirs]

        r = {}
        for d in dirs:
            r[BackendKey("remote-matrix", d)] = RemoteMatrixBackend(d)

        r[BackendKey("system-matrix", None)] = SystemRemoteMatrixBackend()

        return r

    def _mir(self):
        from .mir import MirBackend

        return {BackendKey("mir", None): MirBackend()}


MANAGER = BackendManager()

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

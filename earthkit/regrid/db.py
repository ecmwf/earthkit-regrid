# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging
import os
from abc import ABCMeta, abstractmethod

from scipy.sparse import load_npz

from earthkit.regrid.gridspec import GridSpec
from earthkit.regrid.utils import no_progress_bar
from earthkit.regrid.utils.download import download_and_cache

LOG = logging.getLogger(__name__)

_SYSTEM_URL = "https://get.ecmwf.int/repository/earthkit/regrid/matrices"
_INDEX_FILENAME = "index.json"


class MatrixAccessor(metaclass=ABCMeta):
    @abstractmethod
    def path(self):
        pass

    @abstractmethod
    def is_local(self):
        pass

    @abstractmethod
    def index_path(self):
        pass

    @abstractmethod
    def matrix_path(self, name):
        pass


class UrlAccessor(MatrixAccessor):
    def __init__(self, url):
        self._url = url

    def path(self):
        return self._url

    def is_local(self):
        False

    def index_path(self):
        # checking the out of date status does not work for this file,
        # so we have to force the download using Force=True
        try:
            url = os.path.join(self._url, _INDEX_FILENAME)
            path = download_and_cache(
                url,
                owner="url",
                verify=True,
                force=True,
                chunk_size=1024 * 1024,
                http_headers=None,
                update_if_out_of_date=True,
                progress_bar=no_progress_bar,
                maximum_retries=5,
                retry_after=10,
            )
        except Exception:
            LOG.error(f"Could not download index file={url}")
            raise

        return path

    def matrix_path(self, name):
        try:
            url = os.path.join(self._url, name)
            path = download_and_cache(
                url,
                owner="url",
                verify=True,
                force=None,
                chunk_size=1024 * 1024,
                http_headers=None,
                update_if_out_of_date=False,
                maximum_retries=5,
                retry_after=10,
            )
        except Exception:
            LOG.error(f"Could not download matrix file={url}")
            raise

        return path


class LocalAccessor(MatrixAccessor):
    def __init__(self, path):
        self._path = path

    def path(self):
        return self._path

    def is_local(self):
        True

    def index_path(self):
        return os.path.join(self._path, _INDEX_FILENAME)

    def matrix_path(self, name):
        return os.path.join(self._path, name)


class SystemAccessor(UrlAccessor):
    def __init__(self):
        super().__init__(_SYSTEM_URL)


# @contextmanager
# def _use_local_index(path):
#     """Context manager for testing only. Allow using local index
#     file and matrices.
#     """
#     DB.clear_index()
#     DB.accessor = LocalAccessor(path)
#     try:
#         yield None
#     finally:
#         DB.clear_index()
#         DB.accessor = UrlAccessor(_URL)


class MatrixDb:
    def __init__(self, accessor):
        self._index = None
        self._accessor = accessor

    @property
    def index(self):
        if self._index is None:
            self._load_index()
        return self._index

    def _load_index(self):
        self._index = {}
        path = self._accessor.index_path()

        with open(path, "r") as f:
            index = json.load(f)
            for name, entry in index.items():
                # it is possible that the inventory is already updated with new
                # a gridspecs type, but a given earthkit-regrid version is not
                # yet supporting it. In this case loading the index should not crash.
                try:
                    in_gs = GridSpec.from_dict(entry["input"])
                    out_gs = GridSpec.from_dict(entry["output"])
                    raw = entry
                    entry = dict(**entry)
                    entry["input"] = in_gs
                    entry["output"] = out_gs
                    entry["_raw"] = raw
                    # print(f"{in_gs=}")
                    # print(f"{out_gs=}")
                    self._index[name] = entry
                except Exception:
                    pass

    def _clear_index(self):
        """For testing only"""
        self._index = None

    def find(
        self,
        gridspec_in,
        gridspec_out,
        matrix_version=None,
        **kwargs,
        # download_retries=0,
        # download_timeout=30,
        # download_retry_after=10,
    ):
        entry = self.find_entry(gridspec_in, gridspec_out)

        if entry is not None:
            matrix_version = self._matrix_version(entry, matrix_version)
            z = self.load_matrix(entry["name"], matrix_version)
            return z, entry["output"]["shape"]
        return None, None

    def find_entry(self, gridspec_in, gridspec_out):
        gridspec_in = GridSpec.from_dict(gridspec_in)
        gridspec_out = GridSpec.from_dict(gridspec_out)

        if gridspec_in is None or gridspec_out is None:
            return None

        for _, entry in self.index.items():
            if gridspec_in == entry["input"] and gridspec_out == entry["output"]:
                return entry

        return None

    def load_matrix(self, name, version):
        path = self._matrix_path(name, version)
        z = load_npz(path)
        return z

    def _matrix_filename(self, name, version):
        return f"{name}-{version}.npz"

    def _matrix_path(self, name, version):
        return self._accessor.matrix_path(self._matrix_filename(name, version))

    def _matrix_version(self, entry, version):
        versions = entry["versions"]
        if version is not None:
            if version not in versions:
                raise ValueError(f"Unsupported matrix_version={version}")
            return version
        else:
            return sorted(versions)[0]

    def copy_matrix_file(self, entry, out_dir, exist_ok=False, dry_run=False):
        import shutil

        version = self._matrix_version(entry, None)
        matrix_filename = self._matrix_filename(entry["name"], version)
        src_file = self._matrix_path(entry["name"], version)
        target_file = os.path.join(out_dir, matrix_filename)

        if not exist_ok and os.path.exists(target_file):
            if not dry_run:
                raise FileExistsError(f"target file already exists! {target_file}")
            else:
                LOG.warn("target file already exists! {target_file}")

        if not dry_run:
            shutil.copyfile(src_file, target_file)

        return matrix_filename

    def index_file_path(self):
        return self._accessor.index_path()

    def matrix_source(self):
        return self._accessor.path()

    @staticmethod
    def from_path(path):
        return MatrixDb(LocalAccessor(path))


SYS_DB = MatrixDb(SystemAccessor())
DB_LIST = [SYS_DB]


def add_matrix_source(path):
    global DB_LIST
    for item in DB_LIST[1:]:
        if item.matrix_source() == path:
            return item
    db = MatrixDb.from_path(path)
    DB_LIST.append(db)
    return db


def find(gridspec_in, gridspec_out, matrix_source=None, **kwargs):
    if matrix_source is None:
        return SYS_DB.find(gridspec_in, gridspec_out, **kwargs)
    else:
        db = add_matrix_source(matrix_source)
        return db.find(gridspec_in, gridspec_out, **kwargs)

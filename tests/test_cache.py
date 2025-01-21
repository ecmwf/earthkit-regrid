#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os

import pytest

from earthkit.regrid import cache
from earthkit.regrid import config
from earthkit.regrid.utils.caching import cache_file
from earthkit.regrid.utils.temporary import temp_directory


def _make_zeros_cache_file(force=False, **kwargs):
    def _generate_file(target, size=1024 * 1024, chunk_size=1024 * 1024, **kwargs):
        chunk_size = min(chunk_size, size)
        zeros = bytes(chunk_size)

        with open(target, "wb") as f:
            while size > 0:
                bufsize = min(size, chunk_size)
                f.write(zeros[:bufsize])
                size -= bufsize

    def _generate(target, args):
        return _generate_file(target, **args)

    path = cache_file(
        "cache-test",
        _generate,
        kwargs,
        hash_extra="zeros",
        extension=".zeros",
        force=force,
    )

    return path


def check_cache_files(dir_path, managed=True):
    def touch(target, args):
        assert args["foo"] in (1, 2)
        with open(target, "w"):
            pass

    path1 = cache_file(
        "test_cache",
        touch,
        {"foo": 1},
        extension=".test",
    )

    path2 = cache_file(
        "test_cache",
        touch,
        {"foo": 2},
        extension=".test",
    )

    assert os.path.exists(path1)
    assert os.path.exists(path2)
    assert os.path.dirname(path1) == dir_path
    assert os.path.dirname(path1) == dir_path
    assert path1 != path2

    if managed:
        cnt = 0
        for f in cache.entries():
            if f["owner"] == "test_cache":
                cnt += 1

        assert cnt == 2


@pytest.mark.cache
def test_cache_1():
    with config.temporary():
        config.set("maximum-cache-disk-usage", "99%")
        cache.purge(matcher=lambda e: ["owner"] == "test_cache")
        check_cache_files(config.get("user-cache-directory"))


# # 1GB ram disk on MacOS (blocks of 512 bytes)
# # diskutil erasevolume HFS+ "RAMDisk" `hdiutil attach -nomount ram://2097152`
# @pytest.mark.skipif(not os.path.exists("/Volumes/RAMDisk"), reason="No RAM disk")
# def test_cache_4():
#     with config.temporary():
#         config.set("cache-directory", "/Volumes/RAMDisk/earthkit_data")
#         config.set("maximum-cache-disk-usage", "90%")
#         for n in range(10):
#             from_source("dummy-source", "zeros", size=100 * 1024 * 1024, n=n)


def test_cache_policy():
    with temp_directory() as user_dir:
        # cache = user dir
        with config.temporary():
            config.set({"cache-policy": "user", "user-cache-directory": user_dir})
            assert config.get("cache-policy") == "user"
            assert config.get("user-cache-directory") == user_dir
            assert cache.policy.managed() is True
            cache_dir = cache.policy.directory()
            assert cache_dir == user_dir
            assert os.path.exists(cache_dir)
            check_cache_files(cache_dir)

            # cache = temporary with auto generated path
            with config.temporary({"cache-policy": "temporary", "temporary-cache-directory-root": None}):
                assert config.get("cache-policy") == "temporary"
                assert config.get("temporary-cache-directory-root") is None
                assert cache.policy.managed() is True
                cache_dir = cache.policy.directory()
                assert os.path.exists(cache_dir)
                check_cache_files(cache_dir)

            # cache = user dir (again)
            assert config.get("cache-policy") == "user"
            assert config.get("user-cache-directory") == user_dir
            assert cache.policy.managed() is True
            cache_dir = cache.policy.directory()
            assert cache_dir == user_dir
            assert os.path.exists(cache_dir)
            check_cache_files(cache_dir)

            # cache = temporary with user defined root path
            with temp_directory() as root_dir:
                with config.temporary(
                    {
                        "cache-policy": "temporary",
                        "temporary-cache-directory-root": root_dir,
                    }
                ):
                    assert config.get("cache-policy") == "temporary"
                    assert config.get("temporary-cache-directory-root") == root_dir
                    assert cache.policy.managed() is True
                    cache_dir = cache.policy.directory()
                    assert os.path.exists(cache_dir)
                    os.path.dirname(cache_dir) == root_dir
                    check_cache_files(cache_dir)

            # cache = off
            with config.temporary("cache-policy", "off"):
                assert config.get("cache-policy") == "off"
                assert config.get("user-cache-directory") == user_dir
                assert cache.policy.managed() is False

                cache_dir = cache.policy.directory()
                assert os.path.exists(cache_dir)
                check_cache_files(cache_dir, managed=False)

            # cache = user dir (again)
            assert config.get("cache-policy") == "user"
            assert config.get("user-cache-directory") == user_dir
            assert cache.policy.managed() is True
            cache_dir = cache.policy.directory()
            assert cache_dir == user_dir
            assert os.path.exists(cache_dir)
            check_cache_files(cache_dir)


@pytest.mark.parametrize("policy", ["user", "temporary"])
def test_cache_management(policy):
    with temp_directory() as tmp_dir_path:
        with config.temporary():
            if policy == "user":
                config.set({"cache-policy": "user", "user-cache-directory": tmp_dir_path})
                assert cache.directory() == tmp_dir_path
            elif policy == "temporary":
                config.set(
                    {
                        "cache-policy": "temporary",
                        "temporary-cache-directory-root": tmp_dir_path,
                    }
                )
                assert os.path.dirname(cache.directory()) == tmp_dir_path
            else:
                assert False

            data_size = 10 * 1024

            # create 3 files existing only in the cache
            r = []
            for n in range(3):
                r.append(_make_zeros_cache_file(size=data_size, n=n))

            for path in r:
                assert os.path.exists(path)
                assert os.path.dirname(path) == cache.directory()

            # check cache contents
            num, size = cache.summary_dump_database()
            assert num == 3
            assert size == 3 * data_size
            assert len(cache.entries()) == 3

            for i, x in enumerate(cache.entries()):
                assert x["size"] == data_size
                assert x["owner"] == "cache-test"
                assert x["args"] == {"size": data_size, "n": i}
                latest_path = x["path"]

            # limit cache size so that only one file should remain
            config.set({"maximum-cache-size": "12K", "maximum-cache-disk-usage": None})

            num, size = cache.summary_dump_database()
            assert num == 1
            assert size == data_size
            assert len(cache.entries()) == 1
            for x in cache.entries():
                assert x["size"] == data_size
                assert x["owner"] == "cache-test"
                assert x["args"] == {"size": data_size, "n": 2}
                x["path"] == latest_path
                break

            # purge the cache
            r = None
            cache.purge()
            num, size = cache.summary_dump_database()
            assert num == 0
            assert size == 0
            assert len(cache.entries()) == 0


@pytest.mark.cache
def test_cache_force():
    import time

    def _force_true(args, path, owner_data):
        time.sleep(0.001)
        return True

    def _force_false(args, path, owner_data):
        time.sleep(0.001)
        return False

    data_size = 10 * 1024
    path = _make_zeros_cache_file(size=data_size, n=0)
    st = os.stat(path)
    m_time_ref = st.st_mtime_ns

    path1 = _make_zeros_cache_file(size=data_size, n=0)
    assert path1 == path
    st = os.stat(path1)
    m_time = st.st_mtime_ns
    assert m_time == m_time_ref

    path2 = _make_zeros_cache_file(force=_force_false, size=data_size, n=0)
    assert path2 == path
    st = os.stat(path2)
    m_time = st.st_mtime_ns
    assert m_time == m_time_ref

    path3 = _make_zeros_cache_file(force=_force_true, size=data_size, n=0)
    assert path3 == path
    st = os.stat(path3)
    m_time = st.st_mtime_ns
    assert m_time != m_time_ref
    m_time_ref = m_time

    path4 = _make_zeros_cache_file(size=data_size, n=0)
    assert path4 == path
    st = os.stat(path4)
    m_time = st.st_mtime_ns
    assert m_time == m_time_ref

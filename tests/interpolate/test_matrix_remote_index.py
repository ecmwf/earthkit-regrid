# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
import time

import numpy as np
import pytest

from earthkit.regrid import interpolate


@pytest.mark.download
@pytest.mark.tmp_cache
def test_remote_index_handling():
    from earthkit.regrid.backends.db import SYS_DB

    method = "linear"

    db = SYS_DB

    # we need to reset the db to ensure to simulate a fresh start
    db._reset()

    # initial state
    # the index file should be downloaded into the local cache if it is not yet there
    assert not db._accessor.checked_remote()
    path_ori = db._accessor.index_path()
    st = os.stat(path_ori)
    m_time_ref = st.st_mtime_ns

    # this should use the index file in the local cache
    v_in = np.ones(5248)
    v_res = interpolate(v_in, {"grid": "O32"}, {"grid": [10, 10]}, method=method)
    assert v_res.shape == (19, 36), 1
    assert db._accessor.index_path() == path_ori
    st = os.stat(path_ori)
    m_time = st.st_mtime_ns
    assert m_time == m_time_ref, (m_time, m_time_ref)

    # this should trigger a check between the local and remote index file sha and
    # download the remote index file if they are different
    with pytest.raises(ValueError):
        interpolate(v_in, {"grid": "O32"}, {"grid": [1000, 10000]}, method=method)

    assert db._accessor.checked_remote()

    # forcefully download the index file
    path = db._accessor.index_path()
    st = os.stat(path)
    m_time_ref = st.st_mtime_ns
    time.sleep(0.001)
    db._accessor.reload(force=True)
    assert db._accessor.checked_remote()
    path = db._accessor.index_path()
    st = os.stat(path)
    m_time = st.st_mtime_ns
    assert m_time > m_time_ref, (m_time, m_time_ref)

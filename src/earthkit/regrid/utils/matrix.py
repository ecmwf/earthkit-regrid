# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


import logging

LOG = logging.getLogger(__name__)


def numpy_memory_size(m):
    # see: https://stackoverflow.com/questions/11173019/determining-the-byte-size-of-a-scipy-sparse-matrix
    return m.data.nbytes + m.indptr.nbytes + m.indices.nbytes


def torch_memory_size(m):
    indices_bytes = m.indices().element_size() * m.indices().nelement()
    values_bytes = m.values().element_size() * m.values().nelement()
    return indices_bytes + values_bytes


def matrix_memory_size(m):

    for method in [numpy_memory_size, torch_memory_size]:
        try:
            return method(m)
        except Exception as e:
            LOG.info("Failed to get matrix memory size with %s: %s", method.__name__, e)

    return 0

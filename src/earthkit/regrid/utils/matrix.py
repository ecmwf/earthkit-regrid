# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def matrix_memory_size(m):
    # see: https://stackoverflow.com/questions/11173019/determining-the-byte-size-of-a-scipy-sparse-matrix
    try:
        # TODO: This works for bsr, csc and csr matrices but not for other types.
        return m.data.nbytes + m.indptr.nbytes + m.indices.nbytes

    except Exception as e:
        print(e)
        return 0

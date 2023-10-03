import numpy as np
from scipy.sparse import csr_array, save_npz

from .stream import Stream


def dtype_uint(little_endian, size):
    order = "<" if little_endian else ">"
    return np.dtype({4: np.uint32}[size]).newbyteorder(order)


def dtype_float(little_endian, size):
    order = "<" if little_endian else ">"
    return np.dtype({4: np.float32, 8: np.float64}[size]).newbyteorder(order)


def mir_cached_matrix_to_array(path):
    with open(path, "rb") as f:
        s = Stream(f)
        rows = s.read_unsigned_long()  # rows
        cols = s.read_unsigned_long()  # cols
        s.read_unsigned_long()  # non-zeros, ignored

        little_endian = s.read_int() != 0  # little_endian
        index_item_size = s.read_unsigned_long()  # sizeof(index)
        scalar_item_size = s.read_unsigned_long()  # sizeof(scalar)
        s.read_unsigned_long()  # sizeof(size), ignored

        outer = s.read_large_blob()  # outer
        inner = s.read_large_blob()  # inner
        data = s.read_large_blob()  # data

        outer = np.frombuffer(
            outer,
            dtype=dtype_uint(little_endian, index_item_size),
        )

        inner = np.frombuffer(
            inner,
            dtype=dtype_uint(little_endian, index_item_size),
        )

        data = np.frombuffer(
            data,
            dtype=dtype_float(little_endian, scalar_item_size),
        )

        return csr_array((data, inner, outer), shape=(rows, cols))


def mir_cached_matrix_to_file(path, target):
    if not target.endswith(".npz"):
        raise ValueError("target must end with .npz")

    z = mir_cached_matrix_to_array(path)
    save_npz(target, z)

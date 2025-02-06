# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import re


def bytes(n):
    """>>> bytes(4096)
    '4 KiB'
    >>> bytes(4000)
    '3.9 KiB'
    """
    if n < 0:
        sign = "-"
        n -= 0
    else:
        sign = ""

    u = ["", " KiB", " MiB", " GiB", " TiB", " PiB", " EiB", " ZiB", " YiB"]
    i = 0
    while n >= 1024:
        n /= 1024.0
        i += 1
    return "%s%g%s" % (sign, int(n * 10 + 0.5) / 10.0, u[i])


def string_distance(s, t):
    import numpy as np

    m = len(s)
    n = len(t)
    d = np.zeros((m + 1, n + 1), dtype=int)

    one = int(1)
    zero = int(0)

    d[:, 0] = np.arange(m + 1)
    d[0, :] = np.arange(n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = zero if s[i - 1] == t[j - 1] else one
            d[i, j] = min(
                d[i - 1, j] + one,
                d[i, j - 1] + one,
                d[i - 1, j - 1] + cost,
            )

    return d[m, n]


def did_you_mean(word, vocabulary):
    distance, best = min((string_distance(word, w), w) for w in vocabulary)  # noqa F841
    # if distance < min(len(word), len(best)):
    return best


def list_to_human(lst, conjunction="and"):
    if not lst:
        return "??"

    if len(lst) > 2:
        lst = [", ".join(lst[:-1]), lst[-1]]

    return f" {conjunction} ".join(lst)


def as_number(value, name, units, none_ok):
    if value is None and none_ok:
        return None

    value = str(value)
    # TODO: support floats
    m = re.search(r"^\s*(\d+)\s*([%\w]+)?\s*$", value)
    if m is None:
        raise ValueError(f"{name}: invalid number/unit {value}")
    value = int(m.group(1))
    if m.group(2) is None:
        return value
    unit = m.group(2)[0]
    if unit not in units:
        valid = ", ".join(units.keys())
        raise ValueError(f"{name}: invalid unit '{unit}', valid values are {valid}")
    return value * units[unit]


def as_seconds(value, name=None, none_ok=False):
    units = dict(s=1, m=60, h=3600, d=86400, w=86400 * 7)
    return as_number(value, name, units, none_ok)


def as_percent(value, name=None, none_ok=False):
    units = {"%": 1}
    return as_number(value, name, units, none_ok)


def as_bytes(value, name=None, none_ok=False):
    units = {}
    n = 1
    for u in "KMGTP":
        n *= 1024
        units[u] = n
        units[u.lower()] = n

    return as_number(value, name, units, none_ok)

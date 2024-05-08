# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import hashlib
import json


def make_sha(data):
    m = hashlib.sha256()
    if isinstance(data, str):
        m.update(data.encode("utf-8"))
    else:
        m.update(json.dumps(data, sort_keys=True).encode("utf-8"))
    return m.hexdigest()

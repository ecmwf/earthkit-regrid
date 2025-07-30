# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from .handler import DataHandler

LOG = logging.getLogger(__name__)


class GribMessageDataHandler(DataHandler):
    @staticmethod
    def match(values):
        if isinstance(values, bytes):
            return True
        else:
            from io import BytesIO

            # TODO: add further checks to see if the object is a GRIB message
            if isinstance(values, BytesIO):
                return True
        return False

    def regrid(self, values, **kwargs):
        backend = self.backend_from_kwargs(kwargs)
        # backend = self.get_backend(kwargs.pop("backend"), matrix_source=kwargs.pop("matrix_source", None))
        if hasattr(backend, "regrid_grib"):
            if not isinstance(values, bytes):
                from io import BytesIO

                if isinstance(values, BytesIO):
                    values = values.getvalue()

            kwargs.pop("in_grid", None)
            return backend.regrid_grib(values, **kwargs)
        else:
            raise ValueError(f"regrid() does not support GRIB message input for {backend=}!")


handler = GribMessageDataHandler

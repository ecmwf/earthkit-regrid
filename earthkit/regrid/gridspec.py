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

FULL_GLOBE = 360.0
FULL_GLOBE_EPS = 1e-8
DEGREE_EPS = 1e-8


def same_coord(x, y):
    return abs(x - y) < DEGREE_EPS


class GridSpec(dict):
    DEFAULTS = {
        "i_scans_negatively": 0,
        "j_points_consecutive": 0,
        "j_scans_positively": 0,
    }
    DEFAULT_AREA = [90, 0, -90, 360]
    COMPARE_KEYS = {
        "type",
        "grid",
        "i_scans_negatively",
        "j_points_consecutive",
        "j_scans_positively",
    }

    def __init__(self, gs):
        self._global_ew = None
        self._global_ns = None
        super().__init__(gs)

    @staticmethod
    def from_dict(d):
        gs = dict(GridSpec.DEFAULTS)
        gs.update(d)
        gs["type"] = GridSpec._infer_spec_type(gs)
        t = gridspecs.get(gs["type"], None)
        if t is None:
            t = UnsupportedGridSpec
        return t(gs)

    @staticmethod
    def _infer_spec_type(spec):
        spec_type = spec.get("type", None)
        # when no type specified the grid must be regular_ll or gaussian
        if spec_type is None:
            grid = spec["grid"]
            # regular_ll: the grid is in the form of [dx, dy]
            if isinstance(grid, list) and len(grid) == 2:
                spec_type = "regular_ll"
            # gaussian: the grid=N as a str or int
            elif isinstance(grid, (str, int)):
                spec_type = GridSpec._infer_gaussian_type(grid)

        # if spec_type is None:
        #     raise ValueError(f"Could not determine type of gridspec={spec}")

        return spec_type

    @staticmethod
    def _infer_gaussian_type(grid):
        """Determine gridspec type for Gaussian grids"""
        grid_type = ""
        if isinstance(grid, str) and len(grid) > 0:
            try:
                if grid[0] == "F":
                    grid_type = "regular_gg"
                elif grid[0] in ["N", "O"]:
                    grid_type = "reduced_gg"
                else:
                    grid_type = "regular_gg"
                    _ = int(grid)
            except Exception:
                # raise ValueError(f"Invalid Gaussian grid description str={grid}")
                pass
        elif isinstance(grid, int):
            grid_type = "regular_gg"
        else:
            pass
            # raise ValueError(f"Invalid Gaussian grid description={grid}")

        return grid_type

    def __eq__(self, o):
        # print(f"__eq__ self={self} o={o}")
        if self.get("type", "") != o.get("type", ""):
            return False

        for k in self.COMPARE_KEYS:
            if self[k] != o[k]:
                return False

        if "shape" in self and "shape" in o:
            if self["shape"] != o["shape"]:
                return False
        return True

    @staticmethod
    def same_area(area1, area2):
        if len(area1) == len(area2):
            return all(same_coord(v1, v2) for v1, v2 in zip(area1, area2))
        return False

    def has_default_area(self):
        return self.same_area(self["area"], self.DEFAULT_AREA)

    @staticmethod
    def normalise_lon(lon, minimum):
        while lon < minimum:
            lon += FULL_GLOBE
        while lon >= minimum + FULL_GLOBE:
            lon -= FULL_GLOBE
        return lon

    def is_global(self):
        return self.is_global_ew() and self.is_global_ns()

    def is_global_ew(self):
        if self._global_ew is not None:
            return self._global_ew
        else:
            raise NotADirectoryError

    def is_global_ns(self):
        if self._global_ns is not None:
            return self._global_ns
        else:
            raise NotADirectoryError


class LLGridSpec(GridSpec):
    def __init__(self, gs):
        super().__init__(gs)

        self.setdefault("area", self.DEFAULT_AREA)
        if self.get("global", 0) or self.has_default_area():
            self._global_ew = True
            self._global_ns = True

    def __eq__(self, o):
        if not super().__eq__(o):
            return False

        if self.same_area(self["area"], o["area"]):
            return True

        # sanity check: north and south must be the same
        if not same_coord(self.north, o.north) or not same_coord(self.south, o.south):
            return False

        # west-east
        if self.is_global_ew() and o.is_global_ew():
            west = self.normalise_lon(self.west, 0)
            west_o = self.normalise_lon(o.west, 0)
            if same_coord(west, west_o):
                return True

        # TODO: add code for non global grids
        return False

    @property
    def west(self):
        return self["area"][1]

    @property
    def east(self):
        return self["area"][3]

    @property
    def north(self):
        return self["area"][0]

    @property
    def south(self):
        return self["area"][2]

    @property
    def dx(self):
        return abs(self["grid"][0])

    def is_global_ew(self):
        if self._global_ew is None:
            west = self.normalise_lon(self.west, 0)
            east = self.normalise_lon(self.east, 0)
            self._global_ew = False
            if east < west:
                east += FULL_GLOBE
            if abs(east - west) < FULL_GLOBE_EPS:
                self._global_ew = True
            elif abs(east - west - FULL_GLOBE) < FULL_GLOBE_EPS:
                self._global_ew = True
            elif abs(FULL_GLOBE - (east - west) - self.dx) < FULL_GLOBE_EPS:
                self._global_ew = True
        return self._global_ew


class ReducedGGGridSpec(GridSpec):
    def __init__(self, gs):
        super().__init__(gs)

        self.setdefault("area", self.DEFAULT_AREA)
        if self.get("global", 0) or self.has_default_area():
            self._global_ew = True
            self._global_ns = True

        self._octahedral = None
        self._N = None

    def __eq__(self, o):
        if not super().__eq__(o):
            return False

        if self.same_area(self["area"], o["area"]):
            return True

        # check if west the same fro global grids
        if self.is_global() and o.is_global():
            west = self.normalise_lon(self.west, 0)
            west_o = self.normalise_lon(o.west, 0)
            if same_coord(west, west_o):
                return True

        # TODO: add code for non global grids
        return False

    @property
    def west(self):
        return self["area"][1]

    @property
    def east(self):
        return self["area"][3]

    @property
    def dx(self):
        if self.octahedral:
            return FULL_GLOBE / (4 * self.N + 16)
        else:
            return FULL_GLOBE / (4 * self.N)

    def is_global_ew(self):
        if self._global_ew is None:
            west = self.normalise_lon(self.west, 0)
            east = self.normalise_lon(self.east, 0)
            self._global_ew = False
            if east < west:
                east += FULL_GLOBE
            if abs(east - west) < FULL_GLOBE_EPS:
                self._global_ew = True
            elif abs(east - west - FULL_GLOBE) < FULL_GLOBE_EPS:
                self._global_ew = True
            elif abs(FULL_GLOBE - (east - west) - self.dx) < FULL_GLOBE_EPS:
                self._global_ew = True
        return self._global_ew

    def is_global_ns(self):
        if self._global_ns is None:
            self._global_ns = True
        return self._global_ns

    def _inspect_grid(self):
        if self._N is None or self._octahedral is None:
            N = self["grid"]
            octahedral = self.get("octahedral", 0)
            if isinstance(N, str):
                try:
                    if N[0] == "N":
                        N = int(N[1:])
                        octahedral = 0
                    elif N[0] == "O":
                        N = int(N[1:])
                        octahedral = 1
                    else:
                        N = int(N)
                except Exception:
                    raise ValueError(f"Invalid N={N}")
            elif not isinstance(N, int):
                raise ValueError(f"Invalid N={N}")
            if N < 1 or N > 1000000:
                raise ValueError(f"Invalid N={N}")
            self._N = N
            self._octahedral = octahedral

    @property
    def N(self):
        if self._N is None:
            self._inspect_grid()
        return self._N

    @property
    def octahedral(self):
        if self._octahedral is None:
            self._inspect_grid()
        return self._octahedral


class UnsupportedGridSpec(GridSpec):
    pass


gridspecs = {"regular_ll": LLGridSpec, "reduced_gg": ReducedGGGridSpec}

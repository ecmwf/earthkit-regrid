# (C) Copyright 2025- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from collections.abc import Iterable

import numpy as np

from . import Backend


def _resolution(shape, bounds, outer=True):
    # Based on: rioxarray.rioxarray.XRasterBase.resolution
    ny, nx = shape
    left, bottom, right, top = bounds
    dx = (right - left) / (nx - (0 if outer else 1))
    dy = (bottom - top) / (ny - (0 if outer else 1))
    return dx, dy


def _as_outer_bounds(bounds, shape):
    # Based on: rioxarray.rioxarray.XRasterBase._unordered_bounds
    dx, dy = _resolution(shape, bounds, outer=False)
    left, bottom, right, top = bounds
    return (
        left - 0.5 * dx,
        bottom + 0.5 * dy,
        right + 0.5 * dx,
        top - 0.5 * dy,
    )


def _has_rotation(affine):
    # Based on: rioxarray.rioxarray._affine_has_rotation
    return affine.b == affine.d != 0


class CRSAffineGridSpec:
    """Affine transformation mapping into a coordinate reference system."""

    # TODO: serialisation

    def __init__(self, crs, transform, shape):
        self.crs = crs
        self.transform = transform
        self.shape = shape  # array order (y, x)

    @classmethod
    def from_affine(cls, crs, affine, shape):
        """Grid fom a CRS, affine projection and shape.

        Parameters
        ----------
        crs : rasterio.crs.CRS
            Coordinate reference system.
        affine : affine.Affine
            Affine transformation matrix mapping array coordinates (indices)
            to CRS coordinates.
        shape : tuple[int, int]
            Number of grid points in y and x directions (array order).
        """
        return cls(crs, affine, shape)

    @classmethod
    def from_shape(cls, crs, bounds, shape):
        """Grid from a CRS, bounding box and shape.

        Parameters
        ----------
        crs : rasterio.crs.CRS
            Coordinate reference system.
        bounds : tuple[number, number, number, number]
            Bounding coordinates of the grid in CRS coordinates. Order is
            left, bottom, right, top. References grid boxes, grid points are
            generated at the center of the boxes.
        shape : tuple[int, int]
            Number of grid points in y and x directions (array order).
        """
        from affine import Affine

        left, _, _, top = bounds  # reference corner
        dx, dy = _resolution(shape, bounds, outer=True)
        affine = Affine.translation(left, top) * Affine.scale(dx, dy)
        return cls(crs, affine, shape)

    @classmethod
    def from_resolution(cls, crs, bounds, resolution):
        """Grid from a CRS, bounding box and target resolution.

        The returned grid will map to the given bounds exactly by adjusting
        the resolution to match the requirements of a regular grid with an
        integer number of grid points in each dimension.

        Parameters
        ----------
        crs : rasterio.crs.CRS
            Coordinate reference system.
        bounds : tuple[number, number, number, number]
            Bounding coordinates of the grid in CRS coordinates. Order is
            left, bottom, right, top. References grid boxes, grid points are
            generated at the center of the boxes.
        resolution : tuple[number, number] | number
            Grid spacing in x and y direction (coordinate order).
        """
        left, bottom, right, top = bounds
        if isinstance(resolution, Iterable):
            dx, dy = resolution
        else:
            dx = resolution
            dy = resolution
        nx = int(abs((right - left) / dx))
        ny = int(abs((top - bottom) / dy))
        return cls.from_shape(crs, bounds, (ny, nx))

    @classmethod
    def from_regular_coords(cls, crs, x, y):
        """Grid from a CRS and sequences of CRS coordinates.

        Coordinates must form a regular grid.

        Parameters
        ----------
        crs : rasterio.crs.CRS
            Coordinate reference system.
        x : sequence
            CRS coordinates of the grid points (=grid box centers) in the
            x direction.
        y : sequence
            CRS coordinates of the grid points (=grid box centers) in the
            y direction.
        """
        shape = (len(y), len(x))
        # Assumption: grid point coordinates at center of cells
        bounds = _as_outer_bounds((x[0], y[-1], x[-1], y[0]), shape)
        return cls.from_shape(crs, bounds, shape)

    @classmethod
    def from_rioxarray(cls, da):
        """Reproduce the grid of a rioxarray-compatible dataarray"""
        return cls(da.rio.crs, da.rio.transform(), da.rio.shape)

    @property
    def nx(self):
        """Number of grid points in x direction."""
        return self.shape[1]

    @property
    def ny(self):
        """Number of grid points in y direction."""
        return self.shape[0]

    @property
    def resolution(self):
        """Grid spacing in x and y direction (coordinate order)."""
        # Based on: rioxarray.rioxarray._resolution
        # Preserve sign if transform doesn't rotate
        if not _has_rotation(self.transform):
            return self.transform.a, self.transform.e  # dx, dy
        return (
            np.sqrt(self.transform.a**2 + self.transform.d**2),  # dx
            np.sqrt(self.transform.b**2 + self.transform.e**2),  # dy
        )

    @property
    def bounds(self):
        """CRS coordinates of bounding box (left, bottom, top, right).

        Outer coordinates, including all grid boxes, with grid points at the
        center of the grid boxes.
        """
        # Based on: rioxarray.rioxarray.XRasterBase.bounds
        dx, dy = self.resolution
        xs = [self.transform.c, self.transform.c + dx * self.nx]
        ys = [self.transform.f, self.transform.f + dy * self.ny]
        return min(xs), min(ys), max(xs), max(ys)

    @property
    def xy_coords(self):
        """CRS coordinates of all grid points."""
        gridx = np.arange(self.nx) + 0.5
        gridy = np.arange(self.ny) + 0.5
        return self.transform * np.meshgrid(gridx, gridy)

    def reproject(self, crs, *, shape=None, resolution=None):
        """Default grid resulting from reprojection with rasterio.

        Requires rasterio.warp.calculate_default_transform.

        Parameters
        ----------
        crs : rasterio.crs.CRS
            Target CRS for the reprojection.
        shape : None | tuple[int, int], optional
            Number of output grid points in y and x directions (array order).
            Cannot be used together with resolution.
        resolution : None | tuple[]
            Grid spacing of output grid in x and y directions (coordinate
            order). Cannot be used together with shape.
        """
        from rasterio.warp import calculate_default_transform

        assert shape is None or resolution is None, "shape and resolution are mutually exclusive"
        kwargs = {}
        if shape is not None:
            kwargs["dst_height"], kwargs["dst_width"] = shape
        if resolution is not None:
            kwargs["resolution"] = resolution

        transform, nx, ny = calculate_default_transform(
            self.crs, crs, self.nx, self.ny, *self.bounds, **kwargs
        )
        return type(self)(crs, transform, (ny, nx))


def to_rasterio_kwargs(gs, nodata, prefix=""):
    return {f"{prefix}crs": gs.crs, f"{prefix}transform": gs.transform, f"{prefix}nodata": nodata}


class RasterioBackend(Backend):
    """Regridding with rasterio.warp.reproject."""

    name = "rasterio"

    def regrid(self, values, in_grid, out_grid, interpolation=None, nodata=None):
        """Regrid with rasterio.warp.reproject.

        Parameters
        ----------
        values : numpy.ndarray
            Input values. Last axes must correspond to y and x dimensions.
        in_grid : GridSpec
            Grid specification for input values.
        out_grid : GridSpec
            Target grid specification.
        interpolation : None | str
            Resampling method. Choose from available names in rasterio.enums.Resampling.
            The default resampling scheme of rasterio is nearest.
        nodata : None | number
            Nodata value for source and target values.

        Returns
        -------
        numpy.ndarray
            Regridded values.
        """
        from rasterio.enums import Resampling
        from rasterio.warp import reproject

        assert isinstance(in_grid, CRSAffineGridSpec)
        # Convenience offered by rasterio: determine transform and shape
        # of output grid based only on input grid and an output CRS.
        # TODO: (how to) return the output GridSpec?
        if not isinstance(out_grid, CRSAffineGridSpec):
            out_grid = in_grid.reproject(out_grid)

        assert in_grid.shape == values.shape[-2:], "in_grid does not match shape of values"

        reproject_kwargs = {
            **to_rasterio_kwargs(in_grid, nodata, prefix="src_"),
            **to_rasterio_kwargs(out_grid, nodata, prefix="dst_"),
        }

        if interpolation is not None:
            # Alias to accomodate regrid default
            if interpolation == "linear":
                interpolation = "bilinear"
            reproject_kwargs["resampling"] = Resampling[interpolation]

        # Flatten leading dimensions and restore after reprojection
        # (rasterio only handles 2- and 3-dimensional arrays)
        extra_shape = values.shape[:-2]
        flat_size = np.prod(extra_shape, dtype=int)
        values = values.reshape((flat_size, *in_grid.shape[-2:]))
        regridded = np.empty((flat_size, *out_grid.shape), dtype=values.dtype)
        reproject(source=values, destination=regridded, **reproject_kwargs)
        return regridded.reshape((*extra_shape, *out_grid.shape))


backend = RasterioBackend

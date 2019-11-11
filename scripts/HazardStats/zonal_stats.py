"""
This file holds a modified version of `gen_zonal_stats` adapted
from the `python-rasterstats` package.

Chiefly, it caches shapefile geometries in memory to avoid
repeated loading of data, which takes a long time.

WARNING: Memory limits will likely be hit if processing directories with
         large number of shapefiles. 

Original licence details included below:


Copyright (c) 2013 Matthew Perry
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

* Neither the name of the software nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import absolute_import
from __future__ import division

from affine import Affine
from shapely.geometry import shape
import numpy as np
import numpy.distutils.system_info as sysinfo
import warnings

from rasterstats.io import read_features, Raster
from rasterstats.utils import (rasterize_geom, get_percentile, check_stats,
                    remap_categories, key_assoc_val, boxify_points)


def zonal_stats(*args, **kwargs):
    """The primary zonal statistics entry point.
    All arguments are passed directly to ``gen_zonal_stats``.
    See its docstring for details.
    The only difference is that ``zonal_stats`` will
    return a list rather than a generator."""
    return list(gen_zonal_stats(*args, **kwargs))

def gen_zonal_stats(
        vectors, raster,
        layer=0,
        band=1,
        nodata=None,
        affine=None,
        stats=None,
        all_touched=False,
        categorical=False,
        category_map=None,
        add_stats=None,
        zone_func=None,
        raster_out=False,
        prefix=None,
        geojson_out=False, 
        shp_cache={},
        geom_cache={},
        **kwargs):
    """Zonal statistics of raster values aggregated to vector geometries.
    Parameters
    ----------
    vectors: path to an vector source or geo-like python objects
    raster: ndarray or path to a GDAL raster source
        If ndarray is passed, the ``affine`` kwarg is required.
    layer: int or string, optional
        If `vectors` is a path to an fiona source,
        specify the vector layer to use either by name or number.
        defaults to 0
    band: int, optional
        If `raster` is a GDAL source, the band number to use (counting from 1).
        defaults to 1.
    nodata: float, optional
        If `raster` is a GDAL source, this value overrides any NODATA value
        specified in the file's metadata.
        If `None`, the file's metadata's NODATA value (if any) will be used.
        defaults to `None`.
    affine: Affine instance
        required only for ndarrays, otherwise it is read from src
    stats:  list of str, or space-delimited str, optional
        Which statistics to calculate for each zone.
        All possible choices are listed in ``utils.VALID_STATS``.
        defaults to ``DEFAULT_STATS``, a subset of these.
    all_touched: bool, optional
        Whether to include every raster cell touched by a geometry, or only
        those having a center point within the polygon.
        defaults to `False`
    categorical: bool, optional
    category_map: dict
        A dictionary mapping raster values to human-readable categorical names.
        Only applies when categorical is True
    add_stats: dict
        with names and functions of additional stats to compute, optional
    zone_func: callable
        function to apply to zone ndarray prior to computing stats
    raster_out: boolean
        Include the masked numpy array for each feature?, optional
        Each feature dictionary will have the following additional keys:
        mini_raster_array: The clipped and masked numpy array
        mini_raster_affine: Affine transformation
        mini_raster_nodata: NoData Value
    prefix: string
        add a prefix to the keys (default: None)
    geojson_out: boolean
        Return list of GeoJSON-like features (default: False)
        Original feature geometry and properties will be retained
        with zonal stats appended as additional properties.
        Use with `prefix` to ensure unique and meaningful property names.
        
    Returns
    -------
    generator of dicts (if geojson_out is False)
        Each item corresponds to a single vector feature and
        contains keys for each of the specified stats.
    generator of geojson features (if geojson_out is True)
        GeoJSON-like Feature as python dict
    """
    stats, run_count = check_stats(stats, categorical)

    # Handle 1.0 deprecations
    # transform = kwargs.get('transform')
    # if transform:
    #     warnings.warn("GDAL-style transforms will disappear in 1.0. "
    #                   "Use affine=Affine.from_gdal(*transform) instead",
    #                   DeprecationWarning)
    #     if not affine:
    #         affine = Affine.from_gdal(*transform)

    # cp = kwargs.get('copy_properties')
    # if cp:
    #     warnings.warn("Use `geojson_out` to preserve feature properties",
    #                   DeprecationWarning)

    # band_num = kwargs.get('band_num')
    # if band_num:
    #     warnings.warn("Use `band` to specify band number", DeprecationWarning)
    #     band = band_num

    with Raster(raster, affine, nodata, band) as rast:

        if (id(vectors), layer) in shp_cache:
            features_iter = shp_cache[(id(vectors), layer)]
        else:
            features_iter = list(read_features(vectors, layer))
            shp_cache[(id(vectors), layer)] = features_iter
        # End if

        for feat in features_iter:
            if id(feat) in geom_cache:
                (geom, geom_bounds) = geom_cache[id(feat)]
            else:
                geom = shape(feat['geometry'])

                if 'Point' in geom.type:
                    geom = boxify_points(geom, rast)

                geom_bounds = tuple(geom.bounds)

                geom_cache[id(feat)] = (geom, geom_bounds)

            fsrc = rast.read(bounds=geom_bounds)

            # rasterized geometry
            rv_array = rasterize_geom(geom, like=fsrc, all_touched=all_touched)

            # nodata mask
            isnodata = (fsrc.array == fsrc.nodata)

            # add nan mask (if necessary)
            has_nan = (
                np.issubdtype(fsrc.array.dtype, np.floating)
                and np.isnan(fsrc.array.min()))
            if has_nan:
                isnodata = (isnodata | np.isnan(fsrc.array))

            # Mask the source data array
            # mask everything that is not a valid value or not within our geom
            masked = np.ma.MaskedArray(
                fsrc.array,
                mask=(isnodata | ~rv_array))

            # If we're on 64 bit platform and the array is an integer type
            # make sure we cast to 64 bit to avoid overflow.
            # workaround for https://github.com/numpy/numpy/issues/8433
            if sysinfo.platform_bits == 64 and \
                    masked.dtype != np.int64 and \
                    issubclass(masked.dtype.type, np.integer):
                masked = masked.astype(np.int64)

            # execute zone_func on masked zone ndarray
            if zone_func is not None:
                if not callable(zone_func):
                    raise TypeError(('zone_func must be a callable '
                                     'which accepts function a '
                                     'single `zone_array` arg.'))
                zone_func(masked)

            if masked.compressed().size == 0:
                # nothing here, fill with None and move on
                feature_stats = dict([(stat, None) for stat in stats])
                if 'count' in stats:  # special case, zero makes sense here
                    feature_stats['count'] = 0
            else:
                if run_count:
                    keys, counts = np.unique(masked.compressed(), return_counts=True)
                    try:
                        pixel_count = dict(zip([k.item() for k in keys],
                                               [c.item() for c in counts]))
                    except AttributeError:
                        pixel_count = dict(zip([np.asscalar(k) for k in keys],
                                               [np.asscalar(c) for c in counts]))

                if categorical:
                    feature_stats = dict(pixel_count)
                    if category_map:
                        feature_stats = remap_categories(category_map, feature_stats)
                else:
                    feature_stats = {}

                if 'min' in stats:
                    feature_stats['min'] = float(masked.min())
                if 'max' in stats:
                    feature_stats['max'] = float(masked.max())
                if 'mean' in stats:
                    feature_stats['mean'] = float(masked.mean())
                if 'count' in stats:
                    feature_stats['count'] = int(masked.count())
                # optional
                if 'sum' in stats:
                    feature_stats['sum'] = float(masked.sum())
                if 'std' in stats:
                    feature_stats['std'] = float(masked.std())
                if 'median' in stats:
                    feature_stats['median'] = float(np.median(masked.compressed()))
                if 'majority' in stats:
                    feature_stats['majority'] = float(key_assoc_val(pixel_count, max))
                if 'minority' in stats:
                    feature_stats['minority'] = float(key_assoc_val(pixel_count, min))
                if 'unique' in stats:
                    feature_stats['unique'] = len(list(pixel_count.keys()))
                if 'range' in stats:
                    try:
                        rmin = feature_stats['min']
                    except KeyError:
                        rmin = float(masked.min())
                    try:
                        rmax = feature_stats['max']
                    except KeyError:
                        rmax = float(masked.max())
                    feature_stats['range'] = rmax - rmin

                for pctile in [s for s in stats if s.startswith('percentile_')]:
                    q = get_percentile(pctile)
                    pctarr = masked.compressed()
                    feature_stats[pctile] = np.percentile(pctarr, q)

            if 'nodata' in stats or 'nan' in stats:
                featmasked = np.ma.MaskedArray(fsrc.array, mask=(~rv_array))

                if 'nodata' in stats:
                    feature_stats['nodata'] = float((featmasked == fsrc.nodata).sum())
                if 'nan' in stats:
                    feature_stats['nan'] = float(np.isnan(featmasked).sum()) if has_nan else 0

            if add_stats is not None:
                for stat_name, stat_func in add_stats.items():
                    try:
                        feature_stats[stat_name] = stat_func(masked, feat['properties'])
                    except TypeError:
                        # backwards compatible with single-argument function
                        feature_stats[stat_name] = stat_func(masked)

            if raster_out:
                feature_stats['mini_raster_array'] = masked
                feature_stats['mini_raster_affine'] = fsrc.affine
                feature_stats['mini_raster_nodata'] = fsrc.nodata

            if prefix is not None:
                prefixed_feature_stats = {}
                for key, val in feature_stats.items():
                    newkey = "{}{}".format(prefix, key)
                    prefixed_feature_stats[newkey] = val
                feature_stats = prefixed_feature_stats

            if geojson_out:
                for key, val in feature_stats.items():
                    if 'properties' not in feat:
                        feat['properties'] = {}
                    feat['properties'][key] = val
                yield feat
            else:
                yield feature_stats
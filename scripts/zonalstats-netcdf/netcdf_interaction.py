import os

import rasterio
from rasterio.mask import mask

import numpy as np
import fiona

import pandas as pd


def apply_operation(src_nc, src_shape, feature_identifier='NOME_REG',
                    op="nanmean", output_result=True, verbose=False):

    """
    :param op: str, Operation to apply as found in numpy library. Defaults to nanmean
    """

    with fiona.open(src_shape) as shp:

        features = [f['geometry'] for f in shp]
        feat_names = [f['properties'][feature_identifier]
                      .replace(' ', '_')
                      .replace('/', '_')
                      .encode('ascii', 'ignore') for f in shp]

        regions = zip(feat_names, features)

        res = {}
        for region in regions:
            if verbose:
                print("Processing ", region[0])

            with rasterio.open(src_nc) as nc_data:
                img, transform = mask(nc_data, [region[1]], nodata=np.nan)
                meta = nc_data.meta.copy()
            # End with

            bands, height, width = img.shape
            meta.update({
                "height": height,
                "width": width,
                "transform": transform
            })

            operation = getattr(np, op)

            res[region[0]] = res.get(region[0], {})

            res[region[0]][op] = operation(img)
            res[region[0]]['raster'] = img

            # rasterio.plot.show(out_image[0])
        # End for
    # End with

    region_means = pd.DataFrame()
    region_means.index.name = 'region'

    for region, vars in res.iteritems():
        region_means.loc[region, op] = res[region][op]

    if output_result:
        region_means.to_csv("result_{}.csv".format(op))

    return res
# End apply_operation()


if __name__ is '__main__':
    """
    Example of how to use the apply_operation function.
    """

    nc_file = "TOT_PREC_bc_monthly2021-2050_box-rnn.nc"
    shp_file = "IT_reg.shp"
    folder = 'netcdf_interaction'

    result = apply_operation(os.path.join(folder, nc_file),
                             os.path.join(folder, shp_file),
                             output_result=True,
                             verbose=True)

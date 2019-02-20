import os
from netcdf_interaction import apply_operation

nc_file = "TOT_PREC_bc_monthly2021-2050_box-rnn.nc"
shp_file = "IT_reg.shp"
folder = 'netcdf_interaction'

result = apply_operation(os.path.join(folder, nc_file),
                         os.path.join(folder, shp_file),
                         output_result=True,
                         verbose=True)

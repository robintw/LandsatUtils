import gdal,gdalconst
import numpy as np
#"E:/_Datastore/LandsatCDR/SotonNewForest/LEDAPS.bsq"
#"E:/_Datastore/LandsatCDR/SotonNewForest/WaterMask.bsq"

def mask_all_bands(image_filename, mask_filename, output_filename, mask_value_to_delete=255, nodata=-9999):
	im = gdal.Open(image_filename)
	drv = gdal.GetDriverByName("GTiff")
	new_im = drv.CreateCopy(output_filename, im)

	mask = gdal.Open(mask_filename)
	mask_band = mask.GetRasterBand(1).ReadAsArray()

	for i in range(1,im.RasterCount+1):
		band = new_im.GetRasterBand(i)

		band_data = band.ReadAsArray()
		band_data[mask_band == mask_value_to_delete] = nodata
		band.WriteArray(band_data)

		del band


	del mask_band
	del mask
	del new_im
	del drv
import gdal,gdalconst
import numpy as np
import pandas as pd

def image_to_pandas(filename, no_data=9999):
	"""Takes an image given by the filename and get the first three bands
	into a pandas DataFrame."""
	im = gdal.Open(filename)
	blue = im.GetRasterBand(1).ReadAsArray()
	green = im.GetRasterBand(2).ReadAsArray()
	red = im.GetRasterBand(3).ReadAsArray()

	df = pd.DataFrame({'B1':blue.ravel().astype(float), 'B2':green.ravel().astype(float), 'B3':red.ravel().astype(float)})
	df[df == no_data] = np.nan
	df = df.dropna()
	df = df / 10000.0

	return df
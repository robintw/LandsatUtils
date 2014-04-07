import numpy as np
from Py6S import *
from get_radiance_clean_or_aot import *
import gdal,gdalconst
from scipy.interpolate import interp1d
import pandas as pd

def create_simple_lut():
	refls = np.arange(0, 1.0, 0.01)

	B1 = []
	B2 = []
	B3 = []
	B4 = []
	B5 = []
	B7 = []

	s = SixS()
	s.aero_profile = AeroProfile.PredefinedType(AeroProfile.NoAerosols)
	#s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
	s.altitudes.set_sensor_satellite_level()
	s.altitudes.set_target_sea_level()

	for refl in refls:
		print refl
		B1.append(process_band(s, PredefinedWavelengths.LANDSAT_ETM_B1, refl))
		B2.append(process_band(s, PredefinedWavelengths.LANDSAT_ETM_B2, refl))
		B3.append(process_band(s, PredefinedWavelengths.LANDSAT_ETM_B3, refl))
		B4.append(process_band(s, PredefinedWavelengths.LANDSAT_ETM_B4, refl))
		B5.append(process_band(s, PredefinedWavelengths.LANDSAT_ETM_B5, refl))
		B7.append(process_band(s, PredefinedWavelengths.LANDSAT_ETM_B7, refl))

	B1 = np.array(B1)
	B2 = np.array(B2)
	B3 = np.array(B3)
	B4 = np.array(B4)
	B5 = np.array(B5)
	B7 = np.array(B7)

	return (refls, B1, B2, B3, B4, B5, B7)

def create_lut_interpolators():
	refls, B1, B2, B3, B4, B5, B7 = create_simple_lut()

	interp = {'B1': interp1d(refls, B1, bounds_error=False),
			  'B2': interp1d(refls, B2, bounds_error=False),
			  'B3': interp1d(refls, B3, bounds_error=False),
			  'B4': interp1d(refls, B4, bounds_error=False),
			  'B5': interp1d(refls, B5, bounds_error=False),
			  'B7': interp1d(refls, B7, bounds_error=False),}


	return interp

def run_lut_on_image(lut, filename):
	# LUT should be the 4 element tuple returned by create_simple_lut
	refls, blue, green, red = lut

	# Get interpolation functions
	fblue = interp1d(refls, blue, bounds_error=False)
	fgreen = interp1d(refls, green, bounds_error=False)
	fred = interp1d(refls, red, bounds_error=False)

	# Read in image
	im = gdal.Open(filename)

	b = im.GetRasterBand(1).ReadAsArray() / 10000.0
	g = im.GetRasterBand(2).ReadAsArray() / 10000.0
	r = im.GetRasterBand(3).ReadAsArray() / 10000.0

	Lblue = fblue(b)
	Lgreen = fgreen(g)
	Lred = fred(r)


	del b
	del g
	del r
	del im

	return pd.DataFrame(data={'B1R':Lblue.ravel(), 'B2R':Lgreen.ravel(), 'B3R':Lred.ravel()})
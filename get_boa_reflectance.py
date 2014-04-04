import sys
sys.path.append(r"C:\Dropbox\Dropbox\_PhD\_Code\PythonLibs")

from LandsatUtils import parse_metadata
from Py6S import *
import numpy as np
import dateutil
from VanHOzone import get_ozone_conc
from scipy.interpolate import interp1d

class BOAReflectance:

	def __init__(self, metadata_fname):
		self.metadata = parse_metadata(metadata_fname)

	def _process_band(self, s, radiance, wavelength):
		s.wavelength = Wavelength(wavelength)
		s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(radiance)
		s.run()
		return s.outputs.atmos_corrected_reflectance_lambertian

	def create_lut(self):
		s = SixS()

		str_timestamp = self.metadata['PRODUCT_METADATA']['DATE_ACQUIRED'] + " " + self.metadata['PRODUCT_METADATA']['SCENE_CENTER_TIME']
		timestamp = dateutil.parser.parse(str_timestamp)

		lat = float(self.metadata['PRODUCT_METADATA']['CORNER_UL_LAT_PRODUCT'])
		lon = float(self.metadata['PRODUCT_METADATA']['CORNER_UL_LON_PRODUCT'])

		ozone = get_ozone_conc([lat], [lon], timestamp)
		# Assume no water content - won't affect visible bands anyway
		PWC = 0
		s.atmos_profile = AtmosProfile.UserWaterAndOzone(PWC, ozone/1000)

		s.geometry = Geometry.Landsat_TM()
		s.geometry.latitude = lat
		s.geometry.longitude = lon

		# Set day, month and gmt_decimal_hour here from timestamp
		s.geometry.day = timestamp.day
		s.geometry.month = timestamp.month
		s.geometry.gmt_decimal_hour = timestamp.hour + (timestamp.minute / 60.0)

		s.altitudes.set_sensor_satellite_level()
		# ASSUMPTION: Setting altitude to sea level, even though that isn't necessarily correct everywhere
		s.altitudes.set_target_sea_level()

		# Set to have no aerosols
		s.aero_profile = AeroProfile.PredefinedType(AeroProfile.NoAerosols)
		s.altitudes.set_sensor_satellite_level()
		s.altitudes.set_target_sea_level()

		radiances = np.arange(0, 300, 10)

		B1 = []
		B2 = []
		B3 = []
		B4 = []
		B5 = []
		B7 = []

		if self.metadata['PRODUCT_METADATA']['SENSOR_ID'].replace("\"", "") == 'TM':
			print "Running as Landsat 5"
			bands = [PredefinedWavelengths.LANDSAT_TM_B1,
					PredefinedWavelengths.LANDSAT_TM_B2,
					PredefinedWavelengths.LANDSAT_TM_B3,
					PredefinedWavelengths.LANDSAT_TM_B4,
					PredefinedWavelengths.LANDSAT_TM_B5,
					PredefinedWavelengths.LANDSAT_TM_B7]
		else:
			print "Running as Landsat 7"
			bands = [PredefinedWavelengths.LANDSAT_ETM_B1,
					PredefinedWavelengths.LANDSAT_ETM_B2,
					PredefinedWavelengths.LANDSAT_ETM_B3,
					PredefinedWavelengths.LANDSAT_ETM_B4,
					PredefinedWavelengths.LANDSAT_ETM_B5,
					PredefinedWavelengths.LANDSAT_ETM_B7]

		for rad in radiances:
			print rad
			B1.append(self._process_band(s, rad, bands[0]))
			B2.append(self._process_band(s, rad, bands[1]))
			B3.append(self._process_band(s, rad, bands[2]))
			B4.append(self._process_band(s, rad, bands[3]))
			B5.append(self._process_band(s, rad, bands[4]))
			B7.append(self._process_band(s, rad, bands[5]))

		B1 = np.array(B1)
		B2 = np.array(B2)
		B3 = np.array(B3)
		B4 = np.array(B4)
		B5 = np.array(B5)
		B7 = np.array(B7)

		self.lut = [None,
		            interp1d(radiances, B1, bounds_error=False),
		            interp1d(radiances, B2, bounds_error=False),
		            interp1d(radiances, B3, bounds_error=False),
		            interp1d(radiances, B4, bounds_error=False),
		            interp1d(radiances, B5, bounds_error=False),
		            interp1d(radiances, B7, bounds_error=False)]

		print "Created LUT"

	def correct_band(self, arr, band):
		return self.lut[band](arr)
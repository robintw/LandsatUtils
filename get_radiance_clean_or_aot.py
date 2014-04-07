import pandas as pd
from Py6S import *

def process_band(s, band, refl):
	s.ground_reflectance = GroundReflectance.HomogeneousLambertian(refl)
	s.wavelength = Wavelength(band)
	s.run()

	return s.outputs.apparent_radiance

def get_radiance_no_aerosols(stations):
	s = SixS()
	s.aero_profile = AeroProfile.PredefinedType(AeroProfile.NoAerosols)
	#s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
	s.altitudes.set_sensor_satellite_level()
	s.altitudes.set_target_sea_level()

	stations['B1R'] = None
	stations['B2R'] = None
	stations['B3R'] = None
	stations['B4R'] = None

	for i in stations.index:
		# For each band
		# Process the band through Py6S - setting GroundRefl.HL and get radiance result
		# Put radiance result in correct place in dataframe

		stations.ix[i, 'B1R'] = process_band(s, PredefinedWavelengths.LANDSAT_TM_B1, stations.B1[i])
		stations.ix[i, 'B2R'] = process_band(s, PredefinedWavelengths.LANDSAT_TM_B2, stations.B2[i])
		stations.ix[i, 'B3R'] = process_band(s, PredefinedWavelengths.LANDSAT_TM_B3, stations.B3[i])
		stations.ix[i, 'B4R'] = process_band(s, PredefinedWavelengths.LANDSAT_TM_B4, stations.B4[i])

def run_aots_pandas(series):
	s = SixS()
	s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Maritime)
	s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
	s.altitudes.set_sensor_satellite_level()
	s.altitudes.set_target_sea_level()

	blue = []
	green = []
	red = []

	for aot in [0.1, 0.2, 0.3, 0.4, 0.5, 1.0]:
		s.aot550 = aot

		blue.append(process_band(s, PredefinedWavelengths.LANDSAT_TM_B1, series['B1']))

		green.append(process_band(s, PredefinedWavelengths.LANDSAT_TM_B2, series['B2']))

		red.append(process_band(s, PredefinedWavelengths.LANDSAT_TM_B3, series['B3']))

	return pd.DataFrame({'B1':blue, 'B2':green, 'B3':red})
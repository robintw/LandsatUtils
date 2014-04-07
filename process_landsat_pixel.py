from Py6S import *
import os
from path import path
from read_landsat_image import *
import dateutil
import aeronet_new
from atmosprofile_dicts import *
import pandas as pd
import numpy as np

def setup_sixs_object(aot, aeronet_file, PWC, ozone, lat, lon, elev, timestamp):
	s = SixS()

	try:
		temp = timestamp.day
	except:
		timestamp = dateutil.parser.parse(timestamp)

	# import AERONET aerosol profile here
	s = aeronet_new.import_aeronet_data(s, aeronet_file, str(timestamp))

	s.atmos_profile = AtmosProfile.UserWaterAndOzone(PWC, ozone/1000)
	s.aot550 = aot

	# s.geometry = Geometry.Landsat_TM()
	# s.geometry.latitude = lat
	# s.geometry.longitude = lon
	
	# # Set day, month and gmt_decimal_hour here from timestamp
	# s.geometry.day = timestamp.day
	# s.geometry.month = timestamp.month
	# s.geometry.gmt_decimal_hour = timestamp.hour + (timestamp.minute / 60.0)

	s.geometry = Geometry.User()
	s.geometry.from_time_and_location(lat, lon, timestamp.strftime("%H:%M"), 0, 0)

	s.altitudes.set_sensor_satellite_level()
	s.altitudes.set_target_custom_altitude(elev / 1000.0)

	return s

def process_landsat_pixel(s, radiance, band):
	"""Runs data for a given Landsat pixel (all bands) through Py6S to do an atmospheric correction.

	It does this as accurately as possible, using an AERONET-inversion-based aerosol profile,
	an atmospheric profile from PWC and ozone (modelled using the van Heuklon model), and the
	correct geometry for the Landsat observation.

	Return value: a list of atmospherically-corrected reflectances for the given pixel.
	"""
	
	s.wavelength = Wavelength(eval("PredefinedWavelengths.LANDSAT_ETM_%s" % band))
	s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(radiance)

	s.run()
	print s.write_input_file()
	print s.outputs.values
	print s.outputs.atmos_corrected_reflectance_lambertian
	return s.outputs.atmos_corrected_reflectance_lambertian

def myround(x):
    res = float(x) / 10.0
    return int(res) * 10

def correct_all_pixels(stations):
	stations['B1'] = np.nan
	stations['B2'] = np.nan
	stations['B3'] = np.nan
	stations['B4'] = np.nan
	stations['B5'] = np.nan
	stations['B7'] = np.nan


	for i in stations.index:
		print "Processing Station: %s" % stations.name[i]
		try:
			aeronet_name = "920801_130302_%s.dubovik" % stations.name[i]
			aeronet_path = basepath / "AllAeronet" / "INV" / "DUBOV" / "ALL_POINTS" / aeronet_name

			s = setup_sixs_object(stations.AOT[i],
						aeronet_path, stations.PWC[i], stations.ozone[i],
						stations.lat[i], stations.lon[i], stations.elev[i], stations.chosenTime[i])
			for band in ['B1','B2','B3','B4','B5', 'B7']:
				print "Processing %s" % band


				reflectance = process_landsat_pixel(s, stations.ix[i, "raw"+band], band)

				stations.ix[i, band] = reflectance
		except ValueError:
			print "ValueError for %s" % stations.name[i]
			continue
		except KeyboardInterrupt:
			raise
		except Exception, e:
			print "Other Exception: %s" % str(e)
			continue
		except:
			print "Other exception!"
			continue



	return stations
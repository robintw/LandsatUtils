import os
from path import path
from read_landsat_image import *
import dateutil
import pandas as pd
import numpy as np

def get_all_landsat_pixels(stations, n):
	"""Gets the original raw radiances from each Landsat pixel, using the list of stations.

	The n parameter is used to select how many pixels around each AERONET site
	we want to extract: n = 3 gives a 3 x 3 square, and thus 9 pixels.
	"""
	# Subset stations down to only those that have all of the information
	stations = stations.dropna()

	to_join = []

	# Create n1, n3, n5 etc columns ready for data frame
	# (depending on current n - goes down to 1)
	ns = range(n-2, 0, -2)
	n_flags = {}

	for current_n in ns:
		arr = np.zeros((n,n))
		offset = (n - current_n) / 2
		arr[offset:n-offset, offset:n-offset] = 1
		n_flags["n%d" % current_n] = arr.flatten()

	# For each row in stations:
	for i in stations.index:
		# Check all of the required files exist (Landsat, AERONET inversion etc)
		aeronet_name = "920801_130302_%s.dubovik" % stations.name[i]
		aeronet_path = basepath / "AllAeronet" / "INV" / "DUBOV" / "ALL_POINTS" / aeronet_name


		# if os.path.exists(landsat_path) == False or os.path.exists(aeronet_path) == False:
		if os.path.exists(aeronet_path) == False:
			print "Files not found for %s" % stations.name[i]
			continue
		else:
			print "Files found for %s" % stations.name[i]

		# Generate lat and lon arrays
		inds =  np.arange(n)-(n/2)
		lat_offsets = inds * (30/111111.)
		lon_offsets = inds * (30/(111111. * np.cos(np.radians(stations.lat[i]))))

		lats, lons = np.meshgrid(lat_offsets, lon_offsets)

		lats = (stations.lat[i] + lats).flatten()
		lons = (stations.lon[i] + lons).flatten()

		# offset_lat = 30.0/111111
  #     offset_lon = 30/(111111 * Math.cos(Math.radians(clat)))

		try:
			# Get Landsat pixel radiances
			# This gives a list of radiances:
			# Outer list is bands (1-5)
			# Inner list is pixels (eg 9 for n=3)
			radiances = read_landsat_image(stations.sceneID[i], stations.lat[i], stations.lon[i], n)

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

		data = data={'name': stations.name[i],
								# 'lon': stations.lon[i],
								# 'lat': stations.lat[i],
								'lon': lons,
								'lat': lats,
								'elev': stations.elev[i],
								'path': stations.path[i],
								'row': stations.row[i],
								'sceneID': stations.sceneID[i],
								'AOT': stations.AOT[i],
								'PWC': stations.PWC[i],
								'chosenTime': stations.chosenTime[i],
								'ozone': stations.ozone[i],
								'solarZenith': stations.solarZenith[i],
								'solarAzimuth': stations.solarAzimuth[i],
								'rawB1':radiances[0],
								'rawB2':radiances[1],
								'rawB3':radiances[2],
								'rawB4':radiances[3],
								'rawB5':radiances[4],
								'rawB7':radiances[5],
								}
		data.update(n_flags)

		df = pd.DataFrame(data)
		to_join.append(df)

		result = pd.concat(to_join)

		result.index = np.arange(len(result))

	return result
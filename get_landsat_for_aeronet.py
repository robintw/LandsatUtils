import pandas as pd
import sqlite3
import dateutil
import numpy as np

from get_wrs import *

conv = ConvertToWRS()

import sqlite3
conn = sqlite3.connect("./TM_Metadata.sqlite.s3db")
conn.row_factory = sqlite3.Row

def get_path_and_row(s):
	"""Get the WRS path and row for the lat/lon in the given series (a row of the dataframe)"""	
	global conv
	res = conv.get_wrs(s['lat'], s['lon'])
	print res
	if len(res) == 0:
		return None
	else:
		return pd.Series({'path':res[0]['path'], 'row':res[0]['row']})

def get_stations(filename):
	"""Get the original stations list from the file from the AERONET website."""
	df = pd.read_csv(filename, header=None, names=['name', 'lon', 'lat', 'elev'], skiprows=2)

	return df

def read_aeronet(filename):
	"""Read a given AERONET AOT data file, and return it as a dataframe."""
	aeronet = pd.read_csv(filename, skiprows=4, parse_dates=[[0,1]], na_values=["N/A"])
	aeronet.index = aeronet['Date(dd-mm-yy)_Time(hh-mm-ss)']
	an = aeronet.dropna(axis=1, how='all')
	an = an.sort_index()
	return an

def get_landsat_metadata(path, row, date_str):
	"""Find all of the Landsat images acquired within +/- 6 months of the
	specified date, given the path and row location."""
	global conn

	cur = conn.cursor()

	cur.execute("SELECT * FROM images WHERE path=%d AND row=%d "
		"AND acquisitionDate > date('%s','-6 month') AND acquisitionDate < date('%s','+6 month')"
		"ORDER BY cloudCoverFull ASC;" % (path, row, date_str, date_str))

	res = cur.fetchall()

	return (map(dict, res))

def parse_aot_col(s):
    if "AOT_" not in s:
        return 9999999
    else:
        wv = int(s[4:])
        return abs(wv-550)

def get_aot(s):
	new_s = s.copy()
	new_s = new_s.dropna()

	l = list(new_s.index)
	res = map(parse_aot_col, l)

	a = np.array(res)


	aot = new_s[a.argmin()]

	if np.isnan(aot):
		import pdb; pdb.set_trace()

	return aot

def insert_landsat_details(stations, date_str, min_time_diff):
	"""Insert all of the details of Landsat-AERONET coincidences (within the min_time_diff, normally
	15 minutes) into the dataframe."""
	stations['sceneID'] = None
	stations['AOT'] = None
	stations['PWC'] = None
	stations['chosenTime'] = None
	for i in stations.index:
		try:
			aeronet = read_aeronet("E:/_Datastore/LandsatAERONET/AllAERONET/AOT/LEV20/ALL_POINTS/920801_130223_%s.lev20" % stations.ix[i]['name'])
			aeronet['times'] = aeronet.index
			images = get_landsat_metadata(stations.ix[i]['path'], stations.ix[i]['row'], date_str)

			if len(images) == 0:
				continue

			for image in images:
				aot = None
				image_id = None
				image_time = dateutil.parser.parse(image['acquisitionDate'] + " " + image['sceneTime'])
				


				diff = pd.Series(np.abs(aeronet.times - image_time)).astype('timedelta64[ns]')
				min_diff = diff.min() / 6e+10
				if min_diff < min_time_diff:
					# Less than 10 minutes between AERONET measurement and Landast overpass
					i_to_use = diff.argmin()
					s = aeronet.ix[i_to_use]
					image_id = image['sceneID']

					aot = get_aot(s)
					try:
						pwc = s['Water(cm)']
					except:
						pwc = None
					break

			if image_id is not None:
				print "%s: Found with min_diff: %d" % (stations.ix[i]['name'], min_diff)
				stations.ix[i,'AOT'] = aot
				stations.ix[i,'PWC'] = pwc
				stations.ix[i,'sceneID'] = image_id
				stations.ix[i,'chosenTime'] = image_time
			else:
				print "%s: No suitable images found (%d images overall)." % (stations.ix[i]['name'], len(images))
				stations.ix[i,'AOT'] = None
				stations.ix[i,'sceneID'] = None
				stations.ix[i,'chosenTime'] = None
				stations.ix[i,'PWC'] = None
			
			
		except IOError:
			print "WARNING: IOError raised for station."
			continue
		except ValueError:
			print "WARNING: ValueError raised for station."
			continue
		except KeyboardInterrupt:
			raise
		except:
			print "WARNING: Other error raised for this station."

	return stations
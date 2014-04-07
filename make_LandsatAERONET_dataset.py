from get_landsat_for_aeronet import *
from process_landsat_pixel import *
from vanHOzone import *
from get_land_cover import *
from get_radiance_clean_or_aot import *
from cloud_screen import *
from get_landsat_view_angle import *
from get_solar_angles import *
from get_all_landsat_pixels import *
from create_simple_lut import *

# This assumes that the Landsat metadata has been imported into the
# TM_Metadata.sqlite.s3db file first. Currently that is done manually,
# using the data from http://landsat.usgs.gov/metadatalist.php

# We are getting a 3 x 3 pixel window around each AERONET site
n = 9


# Get the list of AERONET stations from 2009
stations = get_stations("aeronet_locations_2002_lev15.txt")

# Get the path and row locations for each lat/lon
paths_and_rows = stations.apply(get_path_and_row, axis=1)
stations = pd.merge(stations, paths_and_rows, left_index=True, right_index=True)

# Find the details (AOT, PWC, sceneID and chosenTime) for the
# times when a Landsat image and an AERONET measurement are within
# 15 minutes of each other.
# Look throughout the whole of 2009 (+/- 6 months from 1st July 2009)
stations = insert_landsat_details(stations, "2009-07-01", 15)

# Subset to just the stations that have all of the data
stations = stations.dropna()

# Make sure the chosenTime field is a string
stations['chosenTime'] = stations.chosenTime.astype('str')

# Get ozone concentrations from the van Heuklon model for each station
stations['ozone'] = get_ozone_conc(stations.lat, stations.lon, stations.chosenTime)

# Get the solar angles (azimuth and zenith) for each site
stations['solarZenith'] = stations.apply(get_zen, axis=1)
stations['solarAzimuth'] = stations.apply(get_az, axis=1)

# Get all of the pixels from the images, taking into account the window size (n)
all_pixels = get_all_landsat_pixels(stations, n)

# Correct all of these pixels using Py6S
corrected_pixels = correct_all_pixels(all_pixels)

# Get the NLCD data for all of the pixels that have it
grouped = corrected_pixels.groupby('name')
corrected_pixels = grouped.apply(get_land_cover_for_stations,
	colname="NLCD",
	lcmap_filename=r"E:\_Datastore\LandCover\US_NLCD\nlcd2006_landcover_4-20-11_se5.img",
	n=n)

# Get the view angles (azimuth and zenith) for each site
grouped = corrected_pixels.groupby('name')
corrected_pixels = grouped.apply(insert_view_angles, n=n)

# Get the radiance for each site in a clean atmosphere
interp = create_lut_interpolators()

corrected_pixels['B1R'] = interp['B1'](corrected_pixels.B1)
corrected_pixels['B2R'] = interp['B2'](corrected_pixels.B2)
corrected_pixels['B3R'] = interp['B3'](corrected_pixels.B3)
corrected_pixels['B4R'] = interp['B4'](corrected_pixels.B4)
corrected_pixels['B5R'] = interp['B5'](corrected_pixels.B5)
corrected_pixels['B7R'] = interp['B7'](corrected_pixels.B7)


# Remove all sites which don't have full data available for them
# This includes some sites which have Band X radiance results
# which are NaN because the corrected reflectance was < 0 or > 1.
res = corrected_pixels.dropna(subset=['B1', 'viewZenith', 'B1R', 'B2R', 'B3R', 'B4R', 'B5R', 'B7R'])


# Some of the NLCD values are 0, which are for areas which are inside the NLCD image but outside
# the NLCD land cover region (the coterminuous USA) - so these need setting to missing data
res['NLCD'] = res['NLCD'].astype(float)
res['NLCD'][res.NLCD == 0] = np.nan


# Remove all sites that don't have the full n x n window (eg. because part of the window was cloudy,
# had invalid data, or extended off the edge of the image)
def nothing_if_not_full(x, n):
    if len(x) != n*n:
        return None
    else:
        return x

g = res.groupby('name')        
res = g.apply(nothing_if_not_full, n)

g = res.groupby('name')        

res.to_csv("LandsatAeronet_L7_LongTimeSeries_n9_beforeManualLC.txt")
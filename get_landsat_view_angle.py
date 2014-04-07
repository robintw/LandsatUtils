import gdal,gdalconst
import numpy as np
import pandas as pd
import os
from path import path
import osr
import gdal


# Calculates view angles for each pixel in Landsat image
# using procedure used for Web-Enabled Landsat Data products
# described at http://globalmonitoring.sdstate.edu/projects/weld/WELD_ATBD.pdf

wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""


def to_tiff(arr, filename, orig_image=None):
	driver = gdal.GetDriverByName("GTiff")
	datatype = gdalconst.GDT_Float32

	out_image = driver.Create(filename, arr.shape[1], arr.shape[0], 1, datatype)


	if orig_image is not None:
		out_image.SetGeoTransform(orig_image.GetGeoTransform())
		out_image.SetProjection(orig_image.GetProjection())


	out_band = out_image.GetRasterBand(1)
	out_band.WriteArray(arr, 0, 0)
	out_band.FlushCache()
	del out_band
	del out_image

def create_landsat_view_angle_images(filename):
	in_image = gdal.Open(filename)
	band = in_image.GetRasterBand(1).ReadAsArray()

	x,y = np.where(band > 0)

	br = (x[x.argmax()],y[x.argmax()])
	bl = (x[x.argmin()],y[x.argmin()])
	tr = (x[y.argmax()],y[y.argmax()])
	tl = (x[y.argmin()],y[y.argmin()])

	df = pd.DataFrame(np.array([br, bl, tr, tl]))
	df = df.sort(columns=0)
	df.index = np.arange(len(df))

	top_center = (df.ix[0]+df.ix[1])/2

	bottom_center = (df.ix[2]+df.ix[3])/2


	x1 = df.ix[0][1]
	y1 = df.ix[0][0]

	x2 = df.ix[1][1]
	y2 = df.ix[1][0]


	scan = np.zeros(band.shape)
	scan[:] = np.nan

	p_sat_x = np.zeros(band.shape)
	p_sat_x[:] = np.nan

	p_sat_y = np.zeros(band.shape)
	p_sat_y[:] = np.nan

	view_azimuth = np.zeros(band.shape)
	view_azimuth[:] = np.nan

	# Get indices of the array
	ys, xs = np.indices(band.shape)

	ys = ys.astype(float)
	xs = xs.astype(float)

	xs[band == 0] = np.nan
	ys[band == 0] = np.nan

	# Create the formula of the top line in ax + by + c = 0
	a = y1 - y2
	b = x2 - x1
	c = (x1 * y2) - (x2 * y1)


	# Calculate the distance to the top line
	# d = abs(a*y + b*x + c) / np.sqrt(a**2 + b**2)
	# scan[x,y] = d
	# scan = np.floor_divide(scan, 16)


	d = abs(a*xs + b*ys + c) / np.sqrt(a**2 + b**2)
	scan = d
	scan = np.floor_divide(scan, 16)

	satellite_locations = []

	for i in range(375):
	    print i
	    satellite_location = (1 - (i/374.)) * top_center + (i/374.)*bottom_center
	    satellite_location = satellite_location + (10.4*30)
	    satellite_locations.append(satellite_location)
	    p_sat_x[scan == i] = satellite_location[1]
	    p_sat_y[scan == i] = satellite_location[0]

	#to_tiff(p_sat_y, "p_sat_y.tif")
	#to_tiff(p_sat_x, "p_sat_x.tif")


	view_azimuth = np.degrees(np.arctan((xs - p_sat_x)/(ys - p_sat_y)))

	#view_azimuth[view_azimuth < 0] = np.abs(view_azimuth[view_azimuth < 0]) + 180
	to_tiff(view_azimuth, os.path.split(filename)[0] + "/view_azimuth.tif", in_image)

	dist = np.sqrt((xs - p_sat_x)**2 + (ys - p_sat_y)**2)

	view_zenith = np.degrees(np.arctan(dist / 23850))
	to_tiff(view_zenith, os.path.split(filename)[0] + "/view_zenith.tif", in_image)

	in_image = None
	del in_image

def create_view_angle_images(stations):
	for i in stations.index:
		sceneID = stations.sceneID[i]
		basepath = path(r"E:\_Datastore\LandsatAERONET")

		filename = basepath / sceneID / sceneID + "_B4.TIF"
		print filename

		create_landsat_view_angle_images(filename)

def get_image_data(lat, lon, filename, n):
	im = gdal.Open(filename)

	if im is None:
		return np.nan

	t = im.GetGeoTransform()

	suc, tinv = gdal.InvGeoTransform(t)

	image_cs = osr.SpatialReference()
	image_cs.ImportFromWkt(im.GetProjectionRef())

	ll_cs = osr.SpatialReference()

	ll_cs.ImportFromWkt(wgs84_wkt)

	ll_to_image = osr.CoordinateTransformation(ll_cs, image_cs)

	im_band = im.GetRasterBand(1)

	im_geo_x, im_geo_y, elev = ll_to_image.TransformPoint(lon, lat)
	x, y = gdal.ApplyGeoTransform(tinv, im_geo_x, im_geo_y)

	# print "Lat = %f, Lon = %f" % (lat, lon)
	# print "GeoX = %f, GeoY = %f" % (im_geo_x, im_geo_y)
	# print "X = %d, Y = %d" % (x, y) 
	# print "Rounded X = %d, Rounded Y = %d" % (int(round(x)), int(round(y)))
	# print "Xdim = %d, Ydim = %d" % (im.RasterXSize, im.RasterYSize)

	# lc_class = im_band.ReadAsArray(int(round(x)), int(round(y)), 1, 1)

	lc_classes = im_band.ReadAsArray(int(x - int(n)/2), int(y - int(n)/2), n, n)

	del im_band
	del im

	return lc_classes

def insert_view_angles(stations, n):
	sceneID = stations.sceneID[stations.index[0]]
	basepath = path(r"E:\_Datastore\LandsatAERONET")

	vz_filename = basepath / sceneID / "view_zenith.tif"
	va_filename = basepath / sceneID / "view_azimuth.tif"
	print vz_filename


	lat = stations.lat[stations.index[0]]
	lon = stations.lon[stations.index[0]]

	vz = get_image_data(lat, lon, vz_filename, n)

	if vz is None or np.any(np.isnan(vz)):
		stations['viewZenith'] = np.nan
	else:
		stations['viewZenith'] = vz.flatten()


	va = get_image_data(lat, lon, va_filename, n)

	if va is None or np.any(np.isnan(vz)):
		stations['viewAzimuth'] = np.nan
	else:
		stations['viewAzimuth'] = va.flatten()
	
	return stations
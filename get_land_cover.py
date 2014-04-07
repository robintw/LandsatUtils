import gdal, gdalconst
from path import path
import osr
import numpy as np
import pandas as pd

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

def get_land_cover_for_stations(stations, colname, lcmap_filename, n):
	im = gdal.Open(lcmap_filename)

	t = im.GetGeoTransform()

	suc, tinv = gdal.InvGeoTransform(t)

	image_cs = osr.SpatialReference()
	image_cs.ImportFromWkt(im.GetProjectionRef())

	ll_cs = osr.SpatialReference()

	ll_cs.ImportFromWkt(wgs84_wkt)

	ll_to_image = osr.CoordinateTransformation(ll_cs, image_cs)

	im_band = im.GetRasterBand(1)

	lat = stations.lat[stations.index[0]]
	lon = stations.lon[stations.index[0]]

	im_geo_x, im_geo_y, elev = ll_to_image.TransformPoint(lon, lat)
	x, y = gdal.ApplyGeoTransform(tinv, im_geo_x, im_geo_y)

	# print "Lat = %f, Lon = %f" % (lat, lon)
	# print "GeoX = %f, GeoY = %f" % (im_geo_x, im_geo_y)
	# print "X = %d, Y = %d" % (x, y) 
	# print "Rounded X = %d, Rounded Y = %d" % (int(round(x)), int(round(y)))
	# print "Xdim = %d, Ydim = %d" % (im.RasterXSize, im.RasterYSize)

	# lc_class = im_band.ReadAsArray(int(round(x)), int(round(y)), 1, 1)

	lc_classes = im_band.ReadAsArray(int(x - int(n)/2), int(y - int(n)/2), n, n)

	if lc_classes is None:
		stations[colname] = None
	else:
		stations[colname] = lc_classes.flatten()

	del im_band
	del im

	return stations
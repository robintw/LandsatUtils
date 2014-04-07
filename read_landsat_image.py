import gdal, gdalconst
from path import path
import osr

basepath = path(r"E:\_Datastore\LandsatAERONET")

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

def split_and_get_details(line):
	if "VCID" in line:
		return 6, None
	split = [x.strip() for x in line.split("=")]
	band = int(split[0][-1])
	factor = float(split[1])

	return band, factor


def get_radiance_scaling(filename):
	"""Get the radiance multiplicative and additive scale factors
	from the given Landsat _MLT.txt filename."""
	with open(filename, 'r') as f:
		lines = f.readlines()

	radiance_mult = [None] * 8
	radiance_add = [None] * 8

	mult_lines = [x for x in lines if "RADIANCE_MULT" in x]
	add_lines = [x for x in lines if "RADIANCE_ADD" in x]

	for mult_line, add_line in zip(mult_lines, add_lines):
		mult_band, mult_factor = split_and_get_details(mult_line)
		radiance_mult[mult_band - 1] = mult_factor

		add_band, add_factor = split_and_get_details(add_line)
		radiance_add[add_band - 1] = add_factor

	print radiance_mult, radiance_add
	return radiance_mult, radiance_add

def read_landsat_image(sceneID, lat, lon, n):
	"""Gets the radiance of pixels within a N x N square centred on the given latitude
	and longitude, from the Landsat image with the given sceneID

	Converts from DN to radiance using the scale factors in the associated _MLT.txt file.

	Deals with whatever projection the Landsat image is in, and maps it to WGS84 to deal with 
	the latitude and longitude location.

	Returns a list of lists, with the outer list corresponding to the individual pixels
	(eg. 9 elements for n = 3), and the inner list being radiances for the first
	5 Landsat bands.
	"""

	basefilename = basepath / sceneID / sceneID

	results = []

	radiance_mult, radiance_add = get_radiance_scaling(basefilename + "_MTL.txt")

	# Get the geotransform etc from Band 1 of the image
	im = gdal.Open(basefilename + "_B1.TIF")

	t = im.GetGeoTransform()

	suc, tinv = gdal.InvGeoTransform(t)

	image_cs = osr.SpatialReference()
	image_cs.ImportFromWkt(im.GetProjectionRef())

	ll_cs = osr.SpatialReference()

	ll_cs.ImportFromWkt(wgs84_wkt)

	ll_to_image = osr.CoordinateTransformation(ll_cs, image_cs)

	im_geo_x, im_geo_y, elev = ll_to_image.TransformPoint(lon, lat)

	# x and y are now the pixel location of the central pixel in our window
	x, y = gdal.ApplyGeoTransform(tinv, im_geo_x, im_geo_y)

	x = int(round(x))
	y = int(round(y))

	#print "Lat = %f, Lon = %f" % (lat, lon)
	#print "GeoX = %f, GeoY = %f" % (im_geo_x, im_geo_y)
	#print "X = %d, Y = %d" % (x, y) 
	#print "Rounded X = %d, Rounded Y = %d" % (int(round(x)), int(round(y)))
	#print "Xdim = %d, Ydim = %d" % (im.RasterXSize, im.RasterYSize)


	for band in [1,2,3,4,5,7]:
		im = gdal.Open(basefilename + "_B" + str(band) + ".TIF")

		im_band = im.GetRasterBand(1)


		dns = im_band.ReadAsArray(x - int(n)/2, y - int(n)/2, n, n).flatten()
		radiance = (radiance_mult[band-1] * dns) + radiance_add[band-1]

		radiance = list(radiance)

		# if dn is None:
		# 	raise IOError("DN is None!")


		results.append(radiance)

	return results
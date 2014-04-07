import gdal, gdalconst
import numpy as np
import scipy.stats.mstats
from matplotlib.pyplot import *
import osr

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

def linear(inputArray, scale_min=None, scale_max=None):
    """Performs linear scaling of the input numpy array.

    @type inputArray: numpy array
    @param inputArray: image data array
    @type scale_min: float
    @param scale_min: minimum data value
    @type scale_max: float
    @param scale_max: maximum data value
    @rtype: numpy array
    @return: image data array

    """     
    imageData=np.array(inputArray, copy=True)

    if scale_min == None:
        scale_min = imageData.min()
    if scale_max == None:
        scale_max = imageData.max()

    imageData = imageData.clip(min=scale_min, max=scale_max)
    imageData = (imageData -scale_min) / (scale_max - scale_min)
    indices = np.where(imageData < 0)
    imageData[indices] = 0.0
    indices = np.where(imageData > 1)
    imageData[indices] = 1.0

    return imageData

def linear_2perc(array):
    """Scale an array using a linear 2% scaling"""
    quantiles = scipy.stats.mstats.mquantiles(array, prob=[0.02, 0.98])
    my_min, my_max = list(quantiles)
    return linear(array, scale_min=my_min, scale_max=my_max)

def get_band(sceneID, band, center_lon, center_lat, dim_x=200, dim_y=200):
    """Get a subset of a band given a sceneID (to find the filename),
    band number (1-4), lat and lon to centre the image on, and a size (200x200
    by default).
    """

    filename = "E:\_Datastore\LandsatAERONET\%s\%s_B%d.TIF" % (sceneID, sceneID, band)
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)

    t = ds.GetGeoTransform()

    suc, tinv = gdal.InvGeoTransform(t)

    image_cs = osr.SpatialReference()
    image_cs.ImportFromWkt(ds.GetProjectionRef())

    ll_cs = osr.SpatialReference()

    ll_cs.ImportFromWkt(wgs84_wkt)

    ll_to_image = osr.CoordinateTransformation(ll_cs, image_cs)

    im_geo_x, im_geo_y, elev = ll_to_image.TransformPoint(center_lon, center_lat)


    center_x, center_y = gdal.ApplyGeoTransform(tinv, im_geo_x, im_geo_y)



    x = center_x - (dim_x / 2)
    y = center_y - (dim_y / 2)
    # x = np.clip(center_x - (dim_x / 2), 0, ds.RasterXSize)
    # y = np.clip(center_y - (dim_y / 2), 0, ds.RasterXSize)

    # x = int(round(x))
    # y = int(round(y))

    #dn = im_band.ReadAsArray(int(round(x)), int(round(y)), 1, 1)
    res = band.ReadAsArray(int(round(x)),int(round(y)),dim_x,dim_y)

    return res

def combine_bands(blue, green, red):
    """Combine Blue, Green and Red bands as arrays into an image."""
    img = np.zeros( (blue.shape[0], blue.shape[1], 3), dtype=float)
    img[:,:,0] = red
    img[:,:,1] = green
    img[:,:,2] = blue

    return img

def show_rgb(sceneID, lat, lon, name):
    """Shows a RGB satellite image composite given a sceneID,
    a lat/lon to center it on, and a name to use as the title."""
    B1 = get_band(sceneID, 1, lon, lat, dim_x=50, dim_y=50)
    B2 = get_band(sceneID, 2, lon, lat, dim_x=50, dim_y=50)
    B3 = get_band(sceneID, 3, lon, lat, dim_x=50, dim_y=50)

    sB1 = linear_2perc(B1)
    sB2 = linear_2perc(B2)
    sB3 = linear_2perc(B3)

    img = combine_bands(sB1, sB2, sB3)

    
    clf()
    imshow(img, aspect='equal')
    vlines(25, 0, 50, color='red')
    hlines(25, 0, 50, color='red')
    xticks([])
    yticks([])
    title(name)
    tight_layout()


def show_rgb_and_spectrum(sceneID, lat, lon, name, reflectances):
    """Shows a RGB satellite image composite given a sceneID,
    a lat/lon to center it on, and a name to use as the title,
    plus a plot of reflectances for each band."""
    B1 = get_band(sceneID, 1, lon, lat)
    B2 = get_band(sceneID, 2, lon, lat)
    B3 = get_band(sceneID, 3, lon, lat)

    sB1 = linear_2perc(B1)
    sB2 = linear_2perc(B2)
    sB3 = linear_2perc(B3)

    img = combine_bands(sB1, sB2, sB3)

    band_centers = [0.485, 0.56, 0.66, 0.83, 1.65]



    #reflectances = [row['B1'],row['B2'],row['B3'],row['B4'],row['B5']]

    clf()
    subplot(121)
    imshow(img, aspect='equal')
    vlines(25, 0, 50, color='red')
    hlines(25, 0, 50, color='red')
    xticks([])
    yticks([])
    title(name)
    subplot(122)
    plot(band_centers, reflectances)
    tight_layout()

def show_rgb_from_series(s):
    """Shows a RGB image from a series extracted from a pandas dataframe."""    
    show_rgb(s['sceneID'], s['lat'], s['lon'], s['name'])


def show_rgb_and_spectrum_from_series(s):
    print s
    # Calculate X and Y locations from lat and lon
    refl = [s['B1'],s['B2'],s['B3'],s['B4'],s['B5']]
    band_centers = [0.485, 0.56, 0.66, 0.83, 1.65]

    print refl
    figure(1)
    clf()
    plot(band_centers, refl)

    figure(2)
    clf()
    show_rgb(s['sceneID'], s['lat'], s['lon'], s['name'])
    #show_rgb_and_spectrum(s['sceneID'], s['lat'], s['lon'], s['name'], refl)


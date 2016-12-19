import os
import rasterio
from shapely.geometry import Point, MultiPoint
from pyproj import transform, Proj
import re
from subprocess import call


def clip_images(directory, points, dist):

    buffer_dist = dist

    files = os.listdir(directory)
    regex = re.compile('.tif$', re.IGNORECASE)
    files = [os.path.join(directory, f) for f in files if regex.search(f)]

    from_crs = Proj({'init': 'epsg:4326'})

    with rasterio.open(files[0]) as src:
        dest_crs = Proj(src.crs)

    # points = ['57.232,-2.971']
    points = [x.split(',') for x in points]
    points = [[float(x), float(y)] for y, x in points]
    points = [transform(from_crs, dest_crs, x, y) for x, y in points]

    if len(points) > 1:
        points = MultiPoint(points)
        boundary = points.bounds
        points = [[boundary[0], boundary[1]], [boundary[2], boundary[3]]]
    else:
        points = Point(points[0][0], points[0][1])
        area = points.buffer(buffer_dist)
        boundary = area.bounds
        points = [[boundary[0], boundary[1]], [boundary[2], boundary[3]]]

    [[ulx, lry], [lrx, uly]] = points

    for image in files:
        output_image_new = image + '.tmp'

        command_new = 'gdalwarp -overwrite -of GTiff '\
                      '-te %s %s %s %s %s %s' % (ulx, lry, lrx, uly,
                                                 image,
                                                 output_image_new)

        return_code = call(command_new, shell=True)

        os.remove(image)
        os.rename(output_image_new, image)

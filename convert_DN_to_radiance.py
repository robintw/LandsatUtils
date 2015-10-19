import gdal
import gdalconst
import os
import fnmatch
from parse_metadata import parse_metadata
import logging


def recursive_file_search(path, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


def get_radiance_scaling(filename):
    metadata = parse_metadata(filename)

    radiance_mult = [metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_1'],
                     metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_2'],
                     metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_3'],
                     metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_4'],
                     metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_5'],
                     #metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_6_VCID_2'],
                     metadata['RADIOMETRIC_RESCALING']['RADIANCE_MULT_BAND_7']]

    radiance_add = [metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_1'],
                    metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_2'],
                    metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_3'],
                    metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_4'],
                    metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_5'],
                    #metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_6_VCID_2'],
                    metadata['RADIOMETRIC_RESCALING']['RADIANCE_ADD_BAND_7']]

    return map(float, radiance_mult), map(float, radiance_add)


def create_radiance_image(rootname, outputname):
    mtl_filename = rootname + "_MTL.txt"
    radiance_mult, radiance_add = get_radiance_scaling(mtl_filename)

    drv = gdal.GetDriverByName('GTiff')

    band1 = gdal.Open(rootname + "_B1.tif")

    output_image = drv.Create(outputname,
                              band1.RasterXSize, band1.RasterYSize,
                              6,
                              gdalconst.GDT_Float32)
    output_image.SetGeoTransform(band1.GetGeoTransform())
    output_image.SetProjection(band1.GetProjection())

    del band1

    for new_index, file_index in zip([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 7]):
        logging.info("Processing band %d", file_index)
        filename = rootname + "_B%d.tif" % file_index

        im = gdal.Open(filename)

        values = im.GetRasterBand(1).ReadAsArray()

        new_band = output_image.GetRasterBand(new_index)
        logging.debug("Band %d. Mult = %f. Add = %f", file_index,
                      radiance_mult[new_index - 1], radiance_add[new_index - 1])
        new_array = (radiance_mult[new_index - 1] * values) + radiance_add[new_index - 1]
        new_band.WriteArray(new_array)

        del im

    del output_image


def create_all_radiance_images():
    files = recursive_file_search("E:\_Datastore\LandsatCDR", r"*_B1.tif")

    for f in files:
        rootname = f[0:-7]

        create_radiance_image(rootname, rootname + "_Radiance.tif")

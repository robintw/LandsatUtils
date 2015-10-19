import gdal
import gdalconst
import os
from parse_metadata import parse_metadata
import logging

logging.basicConfig(level=logging.DEBUG)


def get_radiance_scaling(filename):
    """Gets scaling factors to convert from DN to radiance for *all*
    Landsat bands (including thermal bands), from the given MTL file.

    Returns a tuple containg two items: a list of multiplication factors,
    and a list of addition values.
    """
    metadata = parse_metadata(filename)

    spacecraft_id = metadata['PRODUCT_METADATA']['SPACECRAFT_ID']

    rad_scaling = metadata['RADIOMETRIC_RESCALING']

    if '8' in spacecraft_id:
        # Landsat 8
        logging.info('Getting radiance scaling factors for Landsat 8')

        radiance_mult = [rad_scaling['RADIANCE_MULT_BAND_1'],
                         rad_scaling['RADIANCE_MULT_BAND_2'],
                         rad_scaling['RADIANCE_MULT_BAND_3'],
                         rad_scaling['RADIANCE_MULT_BAND_4'],
                         rad_scaling['RADIANCE_MULT_BAND_5'],
                         rad_scaling['RADIANCE_MULT_BAND_6'],
                         rad_scaling['RADIANCE_MULT_BAND_7'],
                         rad_scaling['RADIANCE_MULT_BAND_8'],
                         rad_scaling['RADIANCE_MULT_BAND_9'],
                         rad_scaling['RADIANCE_MULT_BAND_10'],
                         rad_scaling['RADIANCE_MULT_BAND_11']
                         ]

        radiance_add = [rad_scaling['RADIANCE_ADD_BAND_1'],
                        rad_scaling['RADIANCE_ADD_BAND_2'],
                        rad_scaling['RADIANCE_ADD_BAND_3'],
                        rad_scaling['RADIANCE_ADD_BAND_4'],
                        rad_scaling['RADIANCE_ADD_BAND_5'],
                        rad_scaling['RADIANCE_ADD_BAND_6'],
                        rad_scaling['RADIANCE_ADD_BAND_7'],
                        rad_scaling['RADIANCE_ADD_BAND_8'],
                        rad_scaling['RADIANCE_ADD_BAND_9'],
                        rad_scaling['RADIANCE_ADD_BAND_10'],
                        rad_scaling['RADIANCE_ADD_BAND_11']
                        ]
    elif '7' in spacecraft_id:
        # Landsat 7
        logging.info('Getting radiance scaling factors for Landsat 7')

        radiance_mult = [rad_scaling['RADIANCE_MULT_BAND_1'],
                         rad_scaling['RADIANCE_MULT_BAND_2'],
                         rad_scaling['RADIANCE_MULT_BAND_3'],
                         rad_scaling['RADIANCE_MULT_BAND_4'],
                         rad_scaling['RADIANCE_MULT_BAND_5'],
                         rad_scaling['RADIANCE_MULT_BAND_6_VCID_1'],
                         rad_scaling['RADIANCE_MULT_BAND_7'],
                         rad_scaling['RADIANCE_MULT_BAND_8']
                         ]

        radiance_add = [rad_scaling['RADIANCE_ADD_BAND_1'],
                        rad_scaling['RADIANCE_ADD_BAND_2'],
                        rad_scaling['RADIANCE_ADD_BAND_3'],
                        rad_scaling['RADIANCE_ADD_BAND_4'],
                        rad_scaling['RADIANCE_ADD_BAND_5'],
                        rad_scaling['RADIANCE_ADD_BAND_6_VCID_1'],
                        rad_scaling['RADIANCE_ADD_BAND_7'],
                        rad_scaling['RADIANCE_ADD_BAND_8']
                        ]
    elif '5' in spacecraft_id:
        # Landsat 5
        logging.info('Getting radiance scaling factors for Landsat 5')

        radiance_mult = [rad_scaling['RADIANCE_MULT_BAND_1'],
                         rad_scaling['RADIANCE_MULT_BAND_2'],
                         rad_scaling['RADIANCE_MULT_BAND_3'],
                         rad_scaling['RADIANCE_MULT_BAND_4'],
                         rad_scaling['RADIANCE_MULT_BAND_5'],
                         rad_scaling['RADIANCE_MULT_BAND_6'],
                         rad_scaling['RADIANCE_MULT_BAND_7'],
                         ]

        radiance_add = [rad_scaling['RADIANCE_ADD_BAND_1'],
                        rad_scaling['RADIANCE_ADD_BAND_2'],
                        rad_scaling['RADIANCE_ADD_BAND_3'],
                        rad_scaling['RADIANCE_ADD_BAND_4'],
                        rad_scaling['RADIANCE_ADD_BAND_5'],
                        rad_scaling['RADIANCE_ADD_BAND_6'],
                        rad_scaling['RADIANCE_ADD_BAND_7'],
                        ]
    else:
        # Unsupported Landsat version
        raise ValueError('Unsupported Landsat satellite')

    return map(float, radiance_mult), map(float, radiance_add)


def create_radiance_image(rootname, outputname):
    mtl_filename = rootname + "_MTL.txt"

    # Get the radiance scaling factors
    radiance_mult, radiance_add = get_radiance_scaling(mtl_filename)

    drv = gdal.GetDriverByName('GTiff')

    band1 = gdal.Open(rootname + "_B1.tif")

    # Configure the output image
    output_image = drv.Create(outputname,
                              band1.RasterXSize, band1.RasterYSize,
                              len(radiance_mult),  # Number of bands
                              gdalconst.GDT_Float32)
    output_image.SetGeoTransform(band1.GetGeoTransform())
    output_image.SetProjection(band1.GetProjection())

    del band1

    for band_index, scaling_factors in enumerate(zip(radiance_mult, radiance_add), start=1):
        # Extract the scaling factors
        scaling_mult, scaling_add = scaling_factors

        filename = rootname + "_B%d.tif" % band_index
        if not os.path.exists(filename) and band_index == 6:
            # We're dealing with Landsat 5 or 7 with the silly VCID names
            filename = rootname + "_B6_VCID_1.TIF"

        logging.info("Processing band %d, filename %s", band_index, filename)

        # Get the data from the file for this band
        im = gdal.Open(filename)
        values = im.GetRasterBand(1).ReadAsArray()

        if values.shape != (output_image.RasterYSize,
                            output_image.RasterXSize):
            logging.debug('Unmatching sizes for band %d,'
                          'panchromatic or low-res SWIR band', band_index)
            continue

        new_band = output_image.GetRasterBand(band_index)
        logging.debug("Band %d. Mult = %f. Add = %f", band_index,
                      scaling_mult, scaling_add)
        # Actually do the scaling
        new_array = (scaling_mult * values) + scaling_add

        # Write out to the image
        new_band.WriteArray(new_array)

        del im

    del output_image

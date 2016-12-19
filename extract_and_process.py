import tarfile
import os
from glob import glob
from subprocess import call
import re
from shutil import copytree

from .convert_DN_to_radiance import create_radiance_image
from .mask import mask_all_bands
from .tweak_images import tweak_rename
from .clip_images import clip_images

import logging


def extract_and_process_uncorrected(uncorrected_fname, path=None,
                                    output_name="Uncorrected_Merged.tif",
                                    clip_coords=None, clip_val=None):

    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    regex = re.compile('.tar.+', re.IGNORECASE)
    if path is None:
        path = regex.sub('', uncorrected_fname)

    logging.info("Processing image with scene ID = %s to %s",
                 regex.sub('', os.path.basename(uncorrected_fname)),
                 path)

    # Keep track of what the current working directory is, and change to the
    # path where we want to put the files
    prev_working_dir = os.getcwd()
    if not os.path.exists(path):
        os.mkdir(path)
        os.chdir(path)
        # Extract the uncorrected .tar.gz file
        tar = tarfile.open(uncorrected_fname)
        logging.info("Extracting %s", uncorrected_fname)
        tar.extractall(path)
        logging.info("Extraction complete.")

    os.chdir(path)

    rootname = regex.sub('', os.path.basename(uncorrected_fname))

    if len(os.listdir(path)[0].split('_')) > 2:
        tweak_rename(rootname, path)

    if clip_coords:
        logging.info('Clipping images')
        i = 1
        while True:
            if os.path.exists(path + '_clipped%d' % i):
                i += 1
                continue
            else:
                new_path = path + '_clipped%d' % i
                copytree(path, new_path)
                break
        clip_images(new_path, clip_coords, clip_val)

    logging.info("Merging uncorrected images")
    # Create a merged radiance image from the raw DN tif files
    create_radiance_image(os.path.join(path, rootname),
                          os.path.join(path, output_name))

    os.chdir(prev_working_dir)


def extract_and_process(ledaps_fname, uncorrected_fname, path):
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    regex = re.compile('.tar.+', re.IGNORECASE)

    logging.info("Processing image with scene ID = %s to %s",
                 regex.sub('', os.path.basename(uncorrected_fname)),
                 path)

    # Keep track of what the current working directory is, and change to the
    # path where we want to put the files
    prev_working_dir = os.getcwd()
    os.chdir(path)

    # Extract the LEDAPS .tar.gz file
    tar = tarfile.open(ledaps_fname)
    logging.info("Extracting %s", ledaps_fname)
    tar.extractall(path)

    # Extract the uncorrected .tar.gz file
    tar = tarfile.open(uncorrected_fname)
    logging.info("Extracting %s", uncorrected_fname)
    tar.extractall(path)
    logging.info("Extraction complete.")

    rootname = regex.sub('', os.path.basename(uncorrected_fname)),

    logging.info("Merging uncorrected images")
    # Create a merged radiance image from the raw DN tif files
    create_radiance_image(os.path.join(path, rootname),
                          os.path.join(path, "Uncorrected_Merged.tif"))

    logging.info("Extracting masks from LEDAPS file")
    # Extract the masks from the LEDAPS lndsr*.hdf file
    basename = os.path.basename(uncorrected_fname)
    lndsr_file = os.path.join(path, "lndsr." + regex.sub('.hdf', basename))
    command = "C:\\OSGeo4W\\bin\\gdal_translate.exe -of GTiff HDF4_EOS:EOS_GRID:\"%s\":Grid:land_water_QA %s" % (lndsr_file,
                            os.path.join(path, "WaterMask.tif"))
    logging.debug("Running command: %s", command)
    logging.debug("Return code is %d", call(command))
    command = "C:\\OSGeo4W\\bin\\gdal_translate.exe -of GTiff HDF4_EOS:EOS_GRID:\"%s\":Grid:cloud_QA %s" % (lndsr_file, os.path.join(path, "CloudMask.tif"))
    logging.debug("Running command: %s", command)
    logging.debug("Return code is %d", call(command))


    logging.info("Masking uncorrected image")
    # Mask the merged uncorrected radiance image
    mask_all_bands(os.path.join(path, "Uncorrected_Merged.tif"),
                   os.path.join(path, "WaterMask.tif"),
                   os.path.join(path, "Uncorrected_Mask1.tif"))
    mask_all_bands(os.path.join(path, "Uncorrected_Mask1.tif"),
                   os.path.join(path, "CloudMask.tif"),
                   os.path.join(path, "Uncorrected_Final.tif"))

    logging.info("Merging LEDAPS bands")
    command = "C:\\OSGeo4W\\bin\\gdal_translate.exe -sds %s output.tif" % lndsr_file
    logging.debug("Running command: %s", command)
    logging.debug("Return code is %d", call(command))

    command = "python \"c:\\Program Files\\GDAL\\gdal_merge.py\" -o LEDAPS_merged.tif -of GTiff -separate output.tif1 output.tif2 output.tif3 output.tif4 output.tif5 output.tif6"
    logging.debug("Running command: %s", command)
    logging.debug("Return code is %d", call(command))

    logging.info("Masking LEDAPS image")
    # Mask the merged LEDAPS image
    mask_all_bands(os.path.join(path, "LEDAPS_merged.tif"),
                   os.path.join(path, "WaterMask.tif"),
                   os.path.join(path, "LEDAPS_Mask1.tif"))

    mask_all_bands(os.path.join(path, "LEDAPS_Mask1.tif"),
                   os.path.join(path, "CloudMask.tif"),
                   os.path.join(path, "LEDAPS_Final.tif"))

    # Change back to the previous directory
    os.chdir(prev_working_dir)

    # Delete all temporary files
    logging.info("Removing temporary files")
    all_files = glob(os.path.join(path, "*.*"))
    for f in all_files:
        if "Final" not in f and "Water" not in f and "Cloud" not in f:
            logging.debug("Removing %s", f)
            os.remove(f)

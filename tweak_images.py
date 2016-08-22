import logging
import os
import fileinput
import sys
from .parse_metadata import parse_metadata


def fixMTL(filename, rad_scaling):
    try:
        id_ = filename.split('/')[-2]
    except:
        id_ = filename.split('\\')[-2]  # Fix for Windows
    to_replace = {
        'ACQUISITION_DATE': 'DATE_ACQUIRED',
        'Landsat7': 'LANDSAT_7',
        'ETM+': 'ETM',
        'SCENE_CENTER_SCAN_TIME': 'SCENE_CENTER_TIME',
        'PRODUCT_UL_CORNER_LAT': 'CORNER_UL_LAT_PRODUCT',
        'PRODUCT_UL_CORNER_LON': 'CORNER_UL_LON_PRODUCT',
        'STARTING_ROW': 'WRS_ROW'
    }

    for idx, l in enumerate(fileinput.input(filename, inplace=True)):
        if idx == 0:
            for k, v in rad_scaling.items():
                sys.stdout.write('%s = %s\n' % (k, v))
        repl = False
        if 'GROUP = METADATA_FILE_INFO' in l:
            sys.stdout.write(l)
            sys.stdout.write('    LANDSAT_SCENE_ID = "%s"\n' % id_)
            continue
        if 'SUN_ELEVATION' in l:
            x = l
            continue
        if 'END_GROUP' in l:
            sys.stdout.write(l)
            try:
                sys.stdout.write('  GROUP = IMAGE_ATTRIBUTES\n' + x)
                sys.stdout.write('  END_GROUP = IMAGE_ATTRIBUTES\n')
                del x
                continue
            except:
                continue
        for k, v in to_replace.items():
            if k in l:
                sys.stdout.write(l.replace(k, v))
                repl = True
        if not repl:
            sys.stdout.write(l)


def generate_rad_scaling(filename):
    metadata = parse_metadata(filename)

    spacecraft_id = metadata['PRODUCT_METADATA']['SPACECRAFT_ID']

    min_max_radiance = metadata['MIN_MAX_RADIANCE']
    min_max_pixel_value = metadata['MIN_MAX_PIXEL_VALUE']

    if '7' in spacecraft_id:
        # Landsat 7
        logging.info('Generating radiance scaling factors for Landsat 7')

        band_names = ['BAND' + str(x) for x in [1, 2, 3, 4, 5, 61, 62, 7, 8]]

        scaling_mult_all = []
        scaling_add_all = []
        for b in band_names:
            l_max = float(min_max_radiance['LMAX_' + b])
            l_min = float(min_max_radiance['LMIN_' + b])
            qcal_max = float(min_max_pixel_value['QCALMAX_' + b])
            qcal_min = float(min_max_pixel_value['QCALMIN_' + b])

            scaling_mult = (l_max - l_min) / (qcal_max - qcal_min)
            scaling_add = l_min - scaling_mult * qcal_min
            scaling_mult_all.append(scaling_mult)
            scaling_add_all.append(scaling_add)

        band_names = [1, 2, 3, 4, 5, '6_VCID_1', '6_VCID_2', 7, 8]
        rad_scaling = {'RADIANCE_MULT_BAND_%s' % x: y for x, y in zip(band_names, scaling_mult_all)}
        rad_scaling.update({'RADIANCE_ADD_BAND_%s' % x: y for x, y in zip(band_names, scaling_add_all)})
    else:
        # Unsupported Landsat version
        raise ValueError('Unsupported Landsat satellite')

    return rad_scaling


def tweak_rename(rootname, path):
    logging.info("Renaming images")
    sc_id = rootname[:3]
    if '7' in sc_id:
        band_names = ['B%s' % x for x in [10, 20, 30, 40, 50, 61, 62, 70, 80]] + ['GCP', 'MTL']
        new_names = [rootname + '_B%s.TIF' % x for x in [1, 2, 3, 4, 5, '6_VCID_1', '6_VCID_2', 7, 8]] +\
            [rootname + '_%s.txt' % x for x in ['GCP', 'MTL']]
        names = {b: n for b, n in zip(band_names, new_names)}
        for f in os.listdir(path):
            try:
                test = [x in f for x in band_names]
                idx = test.index(True)
                old_name = os.path.join(path, f)
                new_name = os.path.join(path, names[band_names[idx]])
                os.rename(old_name, new_name)
            except:
                logging.info('Not renaming file: %s' % f)

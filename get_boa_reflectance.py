from LandsatUtils import parse_metadata
from Py6S import *
import numpy as np
import dateutil
from VanHOzone import get_ozone_conc
from scipy.interpolate import interp1d
from functools import wraps
import logging


class BOAReflectance:
    cache = {}

    def __init__(self, metadata_fname, scale=1):
        self.metadata_filename = metadata_fname
        self.metadata = parse_metadata(metadata_fname)
        self.scale = scale

    def _process_band(self, s, radiance, wavelength):
        s.wavelength = Wavelength(wavelength)
        s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromRadiance(radiance)

        s.run()
        return s.outputs.atmos_corrected_reflectance_lambertian

    def configure_sixs(self):
        s = SixS()

        str_timestamp = (self.metadata['PRODUCT_METADATA']['DATE_ACQUIRED'] +
                         " " +
                         self.metadata['PRODUCT_METADATA']['SCENE_CENTER_TIME'])
        timestamp = dateutil.parser.parse(str_timestamp)
        logging.debug("Timestamp: %s", str(timestamp))

        lat = float(self.metadata['PRODUCT_METADATA']['CORNER_UL_LAT_PRODUCT'])
        lon = float(self.metadata['PRODUCT_METADATA']['CORNER_UL_LON_PRODUCT'])
        logging.debug("Latitude %f, Longitude %f", lat, lon)

        ozone = get_ozone_conc([lat], [lon], timestamp)
        # Assume no water content - won't affect visible bands anyway
        PWC = 0

        logging.debug("Ozone: %f", ozone)
        s.atmos_profile = AtmosProfile.UserWaterAndOzone(PWC, ozone / 1000)

        s.geometry = Geometry.Landsat_TM()
        s.geometry.latitude = lat
        s.geometry.longitude = lon

        # Set day, month and gmt_decimal_hour here from timestamp
        s.geometry.day = timestamp.day
        s.geometry.month = timestamp.month
        s.geometry.gmt_decimal_hour = timestamp.hour + (timestamp.minute / 60.0)

        s.altitudes.set_sensor_satellite_level()

        # ASSUMPTION: Setting altitude to sea level, even though that isn't
        # necessarily correct everywhere
        s.altitudes.set_target_sea_level()

        # Set to have no aerosols
        s.aero_profile = AeroProfile.PredefinedType(AeroProfile.NoAerosols)
        s.altitudes.set_sensor_satellite_level()
        s.altitudes.set_target_sea_level()

        return s

    def get_bands_for_sensor(self):
        spacecraft_id = self.metadata['PRODUCT_METADATA']['SPACECRAFT_ID']
        if '8' in spacecraft_id:
            # Landsat 8
            logging.info('Getting bands for Landsat 8')
            bands = [PredefinedWavelengths.LANDSAT_OLI_B1,
                     PredefinedWavelengths.LANDSAT_OLI_B2,
                     PredefinedWavelengths.LANDSAT_OLI_B3,
                     PredefinedWavelengths.LANDSAT_OLI_B4,
                     PredefinedWavelengths.LANDSAT_OLI_B5,
                     PredefinedWavelengths.LANDSAT_OLI_B6,
                     PredefinedWavelengths.LANDSAT_OLI_B7,
                     None,  # Panchromatic so ignore
                     PredefinedWavelengths.LANDSAT_OLI_B9,
                     None,  # Thermal so ignore
                     None]  # Thermal so ignore
        elif '7' in spacecraft_id:
            # Landsat 7
            logging.info('Getting bands for Landsat 7')
            bands = [PredefinedWavelengths.LANDSAT_ETM_B1,
                     PredefinedWavelengths.LANDSAT_ETM_B2,
                     PredefinedWavelengths.LANDSAT_ETM_B3,
                     PredefinedWavelengths.LANDSAT_ETM_B4,
                     PredefinedWavelengths.LANDSAT_ETM_B5,
                     None,  # Thermal so ignore
                     PredefinedWavelengths.LANDSAT_ETM_B7,
                     None]  # Panchromatic so ignore
        elif '5' in spacecraft_id:
            # Landsat 5
            logging.info('Getting bands for Landsat 5')
            bands = [PredefinedWavelengths.LANDSAT_TM_B1,
                     PredefinedWavelengths.LANDSAT_TM_B2,
                     PredefinedWavelengths.LANDSAT_TM_B3,
                     PredefinedWavelengths.LANDSAT_TM_B4,
                     PredefinedWavelengths.LANDSAT_TM_B5,
                     None,  # Thermal so ignore
                     PredefinedWavelengths.LANDSAT_TM_B7]
        else:
            # Unsupported Landsat version
            raise ValueError('Unsupported Landsat satellite')

        return bands

    def create_lut(self):
        if self.metadata_filename in BOAReflectance.cache:
            self.lut = BOAReflectance.cache[self.metadata_filename]
            logging.info("Got BOAReflectance LUT from cache")
            return

        # Configure the 6S model ready to create the LUT
        s = self.configure_sixs()

        radiances = np.arange(0, 300, 10)

        bands = self.get_bands_for_sensor()

        band_radiance_results = [[] for band in bands]

        for rad in radiances:
            print rad
            for band_radiance_result, band in zip(band_radiance_results, bands):
                if band is None:
                    # We're ignoring this band for some reason
                    band_radiance_result = None
                    continue
                band_radiance_result.append(self._process_band(s, rad, band))

        band_radiance_results = [self._to_array_unless_none(x) for x in band_radiance_results]

        print("Bands len %d" % len(bands))
        print("band_rad_res len %d" % len(band_radiance_results))
        print("band_rad_res[0] len %d" % band_radiance_results[0].shape)
        print("radiances len %d" % len(radiances))

        #self.lut = map(lambda x: self._create_interp(radiances, x), band_radiance_results)
        self.lut = [self._create_interp(radiances, x) for x in band_radiance_results]
        self.lut.insert(0, None)  # Add a blank one at the start because GDAL bands index from 1

        BOAReflectance.cache[self.metadata_filename] = self.lut
        logging.debug("LUT creation finished")

    def _create_interp(self, radiances, band_radiance_result):
        if band_radiance_result is None:
            return None
        else:
            return interp1d(radiances * self.scale,
                            band_radiance_result,
                            bounds_error=False)

    def _to_array_unless_none(self, data):
        if data is None or len(data) == 0:
            return None
        else:
            return np.array(data)

    def correct_band(self, arr, band):
        if self.lut[band] is None:
            # No interpolation, so return NaNs
            new_arr = arr.copy()
            new_arr[:] = np.nan
            return new_arr
        else:
            return self.lut[band](arr)

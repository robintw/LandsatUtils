from .parse_metadata import parse_metadata
import numpy as np
import dateutil
from PySun.sun import Sun


class TOAReflectance:
    """Calculate TOA reflectance from a Landsat ETM+ radiance image."""

    def __init__(self, metadata_fname):
        self.metadata = parse_metadata(metadata_fname)

    def get_toa_reflectance(self, radiance, band):
        solar_z = 90 - float(self.metadata['IMAGE_ATTRIBUTES']['SUN_ELEVATION'])

        irr = [None, 1969.0, 1840.0, 1551.0, 1044.0, 228.7, 82.07, 1368.0]

        timestamp = dateutil.parser.parse(self.metadata['PRODUCT_METADATA']['DATE_ACQUIRED'])
        doy = timestamp.timetuple().tm_yday

        s = Sun()
        temp1, temp2, d = s.sunRADec(doy)

        top = np.pi * radiance * d
        bottom = irr[band] * np.cos(np.radians(solar_z))

        return top / bottom

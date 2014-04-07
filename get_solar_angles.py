import Pysolar
from dateutil.parser import parse

def get_zen(s):
    """Get solar zenith angles for the lats, lons and timestamp.

    Should be run using .apply(get_zen, axis=1) on a pandas DataFrame."""
    
    zen = Pysolar.GetAltitude(s['lat'], s['lon'], parse(s['chosenTime']))
    return 90.0 - zen

def get_az(s):
    """Get solar azimuth angles for the lats, lons and timestamp.

    Should be run using .apply(get_az, axis=1) on a pandas DataFrame."""
    az = Pysolar.GetAzimuth(s['lat'], s['lon'], parse(s['chosenTime']))

    if az < 0:
        az = abs(az) + 180
    else:
        az = abs(az - 180)

    return (az % 360)

# stations['solarZenith'] = stations.apply(get_zen, axis=1)
# stations['solarAzimuth'] = stations.apply(get_az, axis=1)
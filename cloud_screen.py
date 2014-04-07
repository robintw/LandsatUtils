from matplotlib.pyplot import *
from display_as_rgb import *

# Displays an image for an interactive cloud screen

def interactive_cloud_screen(bands):
    figure(figsize=(6,6))
    bands['cloudy'] = None
    for i in bands.index:
        show_rgb_from_series(bands.ix[i])
        show()
        res = raw_input("cloudy (No: Enter, Yes: Y)")
        if res.lower() == "y":
            bands.ix[i, 'cloudy'] = True
        else:
            bands.ix[i, 'cloudy'] = False

        filename = r"E:\_Datastore\LandsatAERONET\PNGs\%s.png" % bands.ix[i, 'name']
        savefig(filename)
        clf()

    close()
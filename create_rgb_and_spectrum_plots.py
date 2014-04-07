from matplotlib.pyplot import *
from display_as_rgb import *

def do_rgb_and_spectra(df):
    for i in df.index:
        show_rgb_and_spectrum_from_series(df.ix[i]) 
        show()
        t = raw_input("Press a key")
        # filename = r"E:\_Datastore\LandsatAERONET\RGB_Spectra_PNGs\%s.png" % df.ix[i, 'name']
        # savefig(filename)

    close()
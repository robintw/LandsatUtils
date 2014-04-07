import pandas as pd
import numpy as np

la = pd.read_csv("LandsatAERONET_2009_n9_All.txt")
nlcd = la.dropna()


print "Percentage match between manualLC and NLCD:"

print "%.2f" % (np.sum(nlcd.manualLC == nlcd.NLCD) / float(len(nlcd)) * 100)


print "Percentage match between manualLC_Broad and NLCD_Broad:"

print "%.2f" % (np.sum(nlcd.manualLC_Broad == nlcd.NLCD_Broad) / float(len(nlcd)) * 100)
import pandas as pd
import numpy as np

# Load in the manually classified data
res = pd.read_csv("LandsatAERONET_n9_manualLC.csv")

# This is the mapping from NLCD class values (LH side) to
# broad land cover classes:
# 1: "Water/Ice",
# 2: "Developed",
# 3: "Bare land",
# 4: "Veg"

NLCD_mapping = {
               11: 1,
               12: 1,
               21: 2,
               22: 2,
               23: 2,
               24: 2,
               31: 3,
               41: 4,
               42: 4,
               43: 4,
               51: 4,
               52: 4,
               71: 4,
               72: 4,
               73: 4,
               74: 4,
               81: 4,
               82: 4,
               90: 4,
               95: 4}

# Create the broad land cover classification - both of the manualLC
# and the original NLCD data
res['manualLC_Broad'] = res.manualLC.replace(NLCD_mapping)
res['NLCD_Broad'] = res.NLCD.replace(NLCD_mapping)

res.to_csv("LandsatAERONET_2009_n9_All.txt")
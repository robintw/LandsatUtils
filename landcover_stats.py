import pandas as pd

# Gross Land Cover classes
# 1: "Water/Ice",
# 2: "Developed",
# 3: "Bare land",
# 4: "Veg"

# CORINE_mapping = {
# 				0: None,
# 				1: 2,
# 				2: 2,
# 				3: 2,
# 				4: 2,
# 				5: 2,
# 				6: 2,
# 				7: 2,
# 				8: 2,
# 				9: 2,
# 				10: 4,
# 				11: 2,
# 				12: 4,
# 				13: 4,
# 				14: 4,
# 				15: 4,
# 				16: 4,
# 				17: 4,
# 				18: 4,
# 				19: 4,
# 				20: 4,
# 				21: 4,
# 				22: 4,
# 				23: 4,
# 				24: 4,
# 				25: 4,
# 				26: 4,
# 				27: 4,
# 				28: 4,
# 				29: 4,
# 				30: 3,
# 				31: 3,
# 				32: 4,
# 				33: 3,
# 				34: 1,
# 				35: 4,
# 				36: 4,
# 				37: 4,
# 				38: 1,
# 				39: 1,
# 				40: 1,
# 				41: 1,
# 				42: 1,
# 				43: 1,
# 				44: 1,
# 				48: None,
# 				49: None,
# 				50: None,
# 				255: None}


# CORINE_legend = {
# 				1: "Continuous urban fabric",
# 				2: "Discontinuous urban fabric",
# 				3: "Industrial or commercial units",
# 				4: "Road and rail networks and associated land",
# 				5: "Port areas",
# 				6: "Airports",
# 				7: "Mineral extraction sites",
# 				8: "Dump sites",
# 				9: "Construction sites",
# 				10: "Green urban areas",
# 				11: "Sport and leisure facilities",
# 				12: "Non-irrigated arable land",
# 				13: "Permanently irrigated land",
# 				14: "Rice fields",
# 				15: "Vineyards",
# 				16: "Fruit trees and berry plantations",
# 				17: "Olive groves",
# 				18: "Pastures",
# 				19: "Annual crops associated with permanent crops",
# 				20: "Complex cultivation patterns",
# 				21: "Land principally occupied by agriculture, with significant areas of natural vegetation",
# 				22: "Agro-forestry areas",
# 				23: "Broad-leaved forest",
# 				24: "Coniferous forest",
# 				25: "Mixed forest",
# 				26: "Natural grasslands",
# 				27: "Moors and heathland",
# 				28: "Sclerophyllous vegetation",
# 				29: "Transitional woodland-shrub",
# 				30: "Beaches, dunes, sands",
# 				31: "Bare rocks",
# 				32: "Sparsely vegetated areas",
# 				33: "Burnt areas",
# 				34: "Glaciers and perpetual snow",
# 				35: "Inland marshes",
# 				36: "Peat bogs",
# 				37: "Salt marshes",
# 				38: "Salines",
# 				39: "Intertidal flats",
# 				40: "Water courses",
# 				41: "Water bodies",
# 				42: "Coastal lagoons",
# 				43: "Estuaries",
# 				44: "Sea and ocean",
# 				48: "NODATA",
# 				49: "UNCLASSIFIED LAND SURFACE",
# 				50: "UNCLASSIFIED WATER BODIES",
# 				255: "UNCLASSIFIED"}

# NLCD_mapping = {
# 			   0: None,
# 			   11: 1,
# 			   12: 1,
# 			   21: 2,
# 			   22: 2,
# 			   23: 2,
# 			   24: 2,
# 			   31: 3,
# 			   41: 4,
# 			   42: 4,
# 			   43: 4,
# 			   51: 4,
# 			   52: 4,
# 			   71: 4,
# 			   72: 4,
# 			   73: 4,
# 			   74: 4,
# 			   81: 4,
# 			   82: 4,
# 			   90: 4,
# 			   95: 4}



# GlobCover_legend = {11:	"Post-flooding or irrigated croplands (or aquatic)",
# 					14:	"Rainfed croplands",
# 					20:	"Mosaic cropland (50-70%) / vegetation (grassland/shrubland/forest) (20-50%)",
# 					30:	"Mosaic vegetation (grassland/shrubland/forest) (50-70%) / cropland (20-50%)",
# 					40:	"Closed to open (>15%) broadleaved evergreen or semi-deciduous forest (>5m)",
# 					50:	"Closed (>40%) broadleaved deciduous forest (>5m)",
# 					60:	"Open (15-40%) broadleaved deciduous forest/woodland (>5m)",
# 					70:	"Closed (>40%) needleleaved evergreen forest (>5m)",
# 					90:	"Open (15-40%) needleleaved deciduous or evergreen forest (>5m)",
# 					100: "Closed to open (>15%) mixed broadleaved and needleleaved forest (>5m)",
# 					110: "Mosaic forest or shrubland (50-70%) / grassland (20-50%)",
# 					120: "Mosaic grassland (50-70%) / forest or shrubland (20-50%)",
# 					130: "Closed to open (>15%) (broadleaved or needleleaved, evergreen or deciduou,s) shrubland (<5m)",
# 					140: "Closed to open (>15%) herbaceous vegetation (grassland, savannas or lichens/mosses)",
# 					150: "Sparse (<15%) vegetation",
# 					160: "Closed to open (>15%) broadleaved forest regularly flooded (semi-permanently or temporarily) - Fresh or brackish water",
# 					170: "Closed (>40%) broadleaved forest or shrubland permanently flooded - Saline or brackish water",
# 					180: "Closed to open (>15%) grassland or woody vegetation on regularly flooded or waterlogged soil - Fresh, brackish or saline water",
# 					190: "Artificial surfaces and associated areas (Urban areas >50%)",
# 					200: "Bare areas",
# 					210: "Water bodies",
# 					220: "Permanent snow and ice",
# 					230: "No data (burnt areas, clouds)"}


NLCD_legend = {11: "Open Water",
			   12: "Perennial Ice/Snow",
			   21: "Developed, Open Space",
			   22: "Developed, Low Intensity",
			   23: "Developed, Medium Intensity",
			   24: "Developed, High Intensity",
			   31: "Barren Land (Rock/Sand/Clay)",
			   41: "Deciduous Forest",
			   42: "Evergreen Forst",
			   43: "Mixed Forest",
			   52: "Shrub/Scrub",
			   71: "Grassland/Herbaceous",
			   81: "Pasture/Hay",
			   82: "Cultivated Crops",
			   90: "Woody Wetlands",
			   95: "Emergent Herbaceous Wetlands"}

def get_percent(class_id, col):
	new_col = col.dropna()
	res = (new_col == class_id)

	return (res.sum() / float(len(new_col)))*100.0


def get_missing_classes(s):
	missing = s[s == 0].index

	for m in missing:
		print m


def calc_lc_stats(stations, colname, legend):
	col = stations[colname]

	perc = [get_percent(i, col) for i in legend.keys()]

	s = pd.Series(data=perc, index=legend.values())
	s = s.order(ascending=False)

	return s

la = pd.read_csv("LandsatAERONET_2009_n9_All.txt")

manualLC = calc_lc_stats(la, "manualLC", NLCD_legend)
NLCD = calc_lc_stats(la, "NLCD", NLCD_legend)

print "Manual Land Cover class statistics:"
print "-----------------------------------"
print manualLC
print ""
print ""
print "NLCD class statistics:"
print "----------------------"
print NLCD

print ""
print ""
print "Missing classes from Manual Land Cover:"
print "---------------------------------------"
get_missing_classes(manualLC)
print ""
print ""
print "Missing classes from NLCD:"
print "--------------------------"
get_missing_classes(NLCD)
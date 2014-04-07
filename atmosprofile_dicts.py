from Py6S import *

# Data from Table 2-2 in http://geol.hu/data/online_help/FLAASHParams.html

SAW = AtmosProfile.PredefinedType(AtmosProfile.SubarcticWinter)
SAS = AtmosProfile.PredefinedType(AtmosProfile.SubarcticSummer)
MLS = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
MLW = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeWinter)
T = AtmosProfile.PredefinedType(AtmosProfile.Tropical)

ap_JFMA = {80: SAW,
		 70: SAW,
		 60: MLW,
		 50: MLW,
		 40: SAS,
		 30: MLS,
		 20: T,
		 10: T,
		 0: T,
		 -10: T,
		 -20: T,
		 -30: MLS,
		 -40: SAS,
		 -50: SAS,
		 -60: MLW,
		 -70: MLW,
		 -80: MLW
}

ap_MJ = {80:SAW,
		 70: MLW,
		 60: MLW,
		 50: SAS,
		 40: SAS,
		 30: MLS,
		 20: T,
		 10: T,
		 0: T,
		 -10: T,
		 -20: T,
		 -30: MLS,
		 -40: SAS,
		 -50: SAS,
		 -60: MLW,
		 -70: MLW,
		 -80: MLW
}

ap_JA = {80:MLW,
		 70: MLW,
		 60: SAS,
		 50: SAS,
		 40: MLS,
		 30: T,
		 20: T,
		 10: T,
		 0: T,
		 -10: T,
		 -20: MLS,
		 -30: MLS,
		 -40: SAS,
		 -50: MLW,
		 -60: MLW,
		 -70: MLW,
		 -80: SAW
}

ap_SO = {80:MLW,
		 70: MLW,
		 60: SAS,
		 50: SAS,
		 40: MLS,
		 30: T,
		 20: T,
		 10: T,
		 0: T,
		 -10: T,
		 -20: MLS,
		 -30: MLS,
		 -40: SAS,
		 -50: MLW,
		 -60: MLW,
		 -70: MLW,
		 -80: MLW
}

ap_ND = {80:SAW,
		 70: SAW,
		 60: MLW,
		 50: SAS,
		 40: SAS,
		 30: MLS,
		 20: T,
		 10: T,
		 0: T,
		 -10: T,
		 -20: T,
		 -30: MLS,
		 -40: SAS,
		 -50: SAS,
		 -60: MLW,
		 -70: MLW,
		 -80: MLW
}


ap_dict = {1: ap_JFMA,
		   2: ap_JFMA,
		   3: ap_JFMA,
		   4: ap_JFMA,
		   5: ap_MJ,
		   6: ap_MJ,
		   7: ap_JA,
		   8: ap_JA,
		   9: ap_SO,
		   10: ap_SO,
		   11: ap_ND,
		   12: ap_ND
}

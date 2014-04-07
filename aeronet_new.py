import pandas as pd
import numpy as np
import dateutil
import warnings
from scipy.interpolate import interp1d
from Py6S import *


def to_iso_date(s):
	spl = s.split(":")
	spl.reverse()

	return "-".join(spl)

def to_timestamp(s):
	str_dt = s['Date(dd-mm-yyyy)'] + " " + s['Time(hh:mm:ss)']

	return pd.to_datetime(str_dt)

def get_aot(df):
	wvs = []
	inds = []

	for i,col in enumerate(df.columns):
		if "AOT_" in col:
			inds.append(i)

	inds.append(len(df.columns) - 1)
	inds = np.array(inds)

	# Remove the columns for AOT wavelengths with no data
	aot_df = df.ix[:,inds]
	aot_df = aot_df.dropna(axis=1, how='all')
	aot_df = aot_df.dropna(axis=0, how='any')


	wvs = []
	inds = []
	for i,col in enumerate(aot_df.columns):
		if "AOT_" in col:
			wvs.append(int(col.replace("AOT_", "")))
			inds.append(i)

	wvs = np.array(wvs)
	inds = np.array(inds)

	wv_diffs = np.abs(wvs - 550)

	aot_col_index = wv_diffs.argmin()

	if (wv_diffs[aot_col_index] > 70):
		warnings.warn("Using AOT measured more than 70nm away from 550nm as nothing closer available - could cause inaccurate results.")

	rowind = aot_df.timediffs.idxmin()

	aot = aot_df.ix[rowind, aot_col_index]

	return aot

def get_model_columns(df):
	refr_ind = []
	refi_ind = []
	wvs = []
	radii_ind = []
	radii = []

	for i,col in enumerate(df.columns):
		if "REFR" in col:
			refr_ind.append(i)
		elif "REFI" in col:
			refi_ind.append(i)
			wv = int(col.replace("REFI", "").replace("(", "").replace(")", ""))
			wvs.append(wv)
		else:
			try:
				rad = float(col)
			except:
				continue
			radii_ind.append(i)
			radii.append(rad)

	return refr_ind, refi_ind, wvs, radii_ind, radii

def import_aeronet_data(s, filename, time):
	# Load in the data from the file
	df = pd.read_csv(filename, skiprows=3, na_values=["N/A"])

	if df.shape[0] == 0:
		raise ValueError("No data in the AERONET file!")

	# Parse the dates/times properly and set them up as the index
	df['Date(dd-mm-yyyy)'] = df['Date(dd-mm-yyyy)'].apply(to_iso_date)
	df['timestamp'] = df.apply(to_timestamp, axis=1)
	df.index = pd.DatetimeIndex(df.timestamp)
	
	given_time = dateutil.parser.parse(time)

	df['timediffs'] = np.abs(df.timestamp - given_time)

	# Get the AOT data at the closest time that has AOT
	# (may be closer to the given_time than the closest
	# time that has full aerosol model information)
	aot = get_aot(df)
	#print "AOT = %f" % aot


	refr_ind, refi_ind, wvs, radii_ind, radii = get_model_columns(df)

	# Get the indices we're interested in from the main df
	inds = refr_ind + refi_ind + radii_ind + [len(df.columns)-1]

	# and put them into a smaller df for just the aerosol-model-related components
	model_df = df.ix[:, inds]
	# Get rid of rows which don't have a full set of data
	model_df = model_df.dropna(axis=0, how='any')

	if model_df.shape[0] == 0:
		raise ValueError("No non-NaN data for aerosol model available in AERONET file.")

	# And get the closest to the given time
	rowind = model_df.timediffs.idxmin()

	# Extract this row as a series
	ser = model_df.ix[rowind]
	# Get the new relevant indices for this smaller df
	refr_ind, refi_ind, wvs, radii_ind, radii = get_model_columns(model_df)

	wvs = np.array(wvs) / 1000.0

	# Interpolate both the real and imag parts of the refractive index
	# at the 6S wavelengths from the wavelengths given in the AERONET file
	sixs_wavelengths = [0.350, 0.400, 0.412, 0.443, 0.470, 0.488, 0.515, 0.550, 0.590, 0.633, 0.670, 0.694, 0.760,
          0.860, 1.240, 1.536, 1.650, 1.950, 2.250, 3.750]

	refr_values = ser[refr_ind]
	f_interp_real = interp1d(wvs, refr_values, bounds_error=False)
	final_refr = f_interp_real(sixs_wavelengths)
	final_refr = pd.Series(final_refr)
	final_refr = final_refr.fillna(method='pad')
	final_refr = final_refr.fillna(method='bfill')

	refi_values = ser[refi_ind]
	f_interp_imag = interp1d(wvs, refi_values, bounds_error=False)
	final_refi = f_interp_imag(sixs_wavelengths)
	final_refi = pd.Series(final_refi)
	final_refi = final_refi.fillna(method='pad')
	final_refi = final_refi.fillna(method='bfill')

	dvdlogr = ser[radii_ind]

	s.aot550 = aot
	s.aero_profile = AeroProfile.SunPhotometerDistribution(radii, dvdlogr, final_refr, final_refi)

	return s
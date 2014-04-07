import numpy as np
from dateutil.parser import parse
import math

def get_ozone_conc(lat, lon, timestamp):
	"""Returns the ozone contents in matm-cm for the given latitude/longitude
	and timestamp (provided as either a datetime object or a string in any sensible format
	- I strongly recommend using an ISO 8601 format of yyyy-mm-dd) according to van Heuklon's
	Ozone model.

	The model is described in Van Heuklon, T. K. (1979).
	Estimating atmospheric ozone for solar radiation models. Solar Energy, 22(1), 63-68.

	This function uses numpy functions, so you can pass arrays
	and it will return an array of results. Note: This does not
	yet support running for multiple dates, so you must only
	pass a single string for the date.
	"""
	# Set the Day of Year

	try:
		# Try and do list-based things with it
		# If it works then it is a list, so check length is correct
		# and process
		count = len(timestamp)
		if count == len(lat):
			try:
				E = [t.timetuple().tm_yday for t in timestamp]
				E = np.array(E)
			except:
				d = [parse(t) for t in timestamp]
				E = [dt.timetuple().tm_yday for dt in d]
				E = np.array(E)
		else:
			raise ValueError("Timestamp must be the same length as lat and lon")
	except:
		# It isn't a list, so just do it once
		try:
			# If this works then it is a datetime obj
			E = timestamp.timetuple().tm_yday
		except:
			# If not then a string, so parse it and set it
			d = parse(timestamp)
			E = d.timetuple().tm_yday

	# Set parameters which are the same for both
	# hemispheres
	D = 0.9865
	G = 20.0
	J = 235.0

	# Set to Northern Hemisphere values by default
	A = np.zeros(np.shape(lat)) + 150.0
	B = np.zeros(np.shape(lat)) + 1.28
	C = np.zeros(np.shape(lat)) + 40.0
	F = np.zeros(np.shape(lat)) - 30.0
	H = np.zeros(np.shape(lat)) + 3.0
	I = np.zeros(np.shape(lat))

	# Gives us a boolean array indicating
	# which indices are below the equator
	# which we can then use for indexing below
	southern = lat < 0

	A[southern] = 100.0
	B[southern] = 1.5
	C[southern] = 30.0
	F[southern] = 152.625
	H[southern] = 2.0
	I[southern] = -75.0

	# Set all northern I values to 20.0
	# (the northern indices are the inverse (~) of
	# the southern indices)
	I[~southern] = 20.0

	I[(~southern) & (lon <= 0)] = 0.0

	bracket = A + (C * np.sin(np.radians(D*(E+F))) + G * np.sin(np.radians(H*(lon + I))))

	sine_bit = np.sin(np.radians(B*lat))
	sine_bit = sine_bit**2

	result = J + (bracket * sine_bit)

	return result

def old_get_ozone_conc(lat, lon, timestamp):
	"""Returns the ozone contents in matm-cm for the given latitude/longitude
	and timestamp (provided as either a datetime object or a string in any sensible format
	- I strongly recommend using an ISO 8601 format of yyyy-mm-dd) according to van Heuklon's
	Ozone model.
	
	The model is described in Van Heuklon, T. K. (1979).
	Estimating atmospheric ozone for solar radiation models. Solar Energy, 22(1), 63-68.

	This function DOES NOT use numpy, so you can only give a single value for lat-lon etc.
	"""

	# Set the Day of Year
	try:
		# If this works then it is a datetime obj
		E = timestamp.timetuple().tm_yday
	except:
		# If not then a string, so parse it and set it
		d = parse(timestamp)
		E = d.timetuple().tm_yday

	# Set parameters which are the same for both
	# hemispheres
	D = 0.9865
	G = 20.0
	J = 235.0

	# Set parameters which are based on hemisphere
	if lat > 0:
		# Northern hemisphere
		A = 150.0
		B = 1.28
		C = 40.0
		F = -30.0
		H = 3.0
		if lon > 0:
			I = 20.0
		else:
			I = 0.0
	else:
		# Southern hemisphere
		A = 100.0
		B = 1.5
		C = 30.0
		F = 152.625
		H = 2.0
		I = -75.0

	bracket = A + (C * math.sin(math.radians(D*(E+F))) + G * math.sin(math.radians(H*(lon + I))))


	rad = math.radians(B*lat)
	sine_bit = math.sin(rad)
	sine_bit = sine_bit**2

	result = J + (bracket * sine_bit)

	return result
import pandas as pd
import webbrowser

def do_manual_lc(st):
	for i in st.index:
		url = """http://localhost:8080/landcover.html?lat=%f&lon=%f""" % (st.lat[i], st.lon[i])
		print url
		webbrowser.open(url)
		print "Now viewing site: %s at Lat: %f, Lon: %f" % (st.name[i], st.lat[i], st.lon[i])
		raw_input("Press enter to go to the next site")
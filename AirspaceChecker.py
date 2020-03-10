
try:
	import igc_lib
	import igc2geojson
except:
	from igc_lib import igc_lib
	from igc_lib import igc2geojson

import json
from collections import namedtuple

class AirspaceChecker:

	def __init__(self):
		self.geojsonAirspace = None
		self.igcFlight = None

	def __loadData(self):
		self.igcFlight = igc_lib.Flight.create_from_file("D:\\_Downloads\\igc\\2019_igc\\93NV6FF1.igc")

		with open("D:\\_Downloads\\airspace.geojson") as json_file:
			self.geojsonAirspace = json.loads(json_file.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			print(len(data.features))

	


	def run(self):
		self.__loadData()

		# Convert airspaces into polygons




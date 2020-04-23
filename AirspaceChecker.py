
try:
	import igc_lib
	import igc2geojson
except:
	from igc_lib import igc_lib
	from igc_lib import igc2geojson

import json
import copy
from collections import namedtuple
from shapely.geometry import MultiPoint
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.strtree import STRtree
import numpy as np

import pandas as pd
import geopandas as gpd
import geojson as gjson
import requests

from flHelper import *
import common
import restApiService

class AirspaceChecker:

	def __init__(self):
		self.geojsonAirspace = None
		self.igcFlight = None
		self.geojsonInfringedAirspace = None
		self.geojsonFlightTrack = None

	def __loadData(self):
		# Flight
		self.igcFlight = igc_lib.Flight.create_from_file("/Users/llauner/Downloads/igc/2020/03EV89C1.igc")

		# Airspace
		airsapceFilename = common.getAirspaceFullFilename()
		with open(airsapceFilename) as jsonFile:
			self.geojsonAirspace = json.loads(jsonFile.read(), object_hook=lambda d: gjson.Feature(**d))

	def __loadDataForNetcoupeFlight(self, flightId):
		self.igcFlight = restApiService.getNetcoupeFlight(flightId)

		# Airspace
		#self.__loadAirspace()
		self.__loadAirspaceFromUrl()
	
	def __loadDataForIgcFile(self, file):
		self.igcFlight = restApiService.getFlightFromIgcFile(file)

		# Airspace
		#self.__loadAirspace()
		self.__loadAirspaceFromUrl()

	def __loadAirspace(self):
		airsapceFilename = common.getAirspaceFullFilename()
		with open(airsapceFilename) as jsonFile:
			self.geojsonAirspace = json.loads(jsonFile.read(), object_hook=lambda d: gjson.Feature(**d))

	def __loadAirspaceFromUrl(self):
		r = requests.get(common.NETCOUPE_OPENAIR_AIRPSACE_URL)
		self.geojsonAirspace = json.loads(r.text, object_hook=lambda d: gjson.Feature(**d))

	def __findCrossedAirspaces(self):
		flightPoints = []
		for fix in self.igcFlight.fixes:
			flightPoints.append((fix.lon,fix.lat))
		trackPoints = MultiPoint(flightPoints)

		crossedAirspacesDict = {}

		for i,feature in enumerate(self.geojsonAirspace.features):
			coords = np.array(feature.geometry.coordinates[0])
			coords2=np.empty((len(coords),), dtype=object)
			coords2[:]=[tuple(i) for i in coords]

			polygon = Polygon(coords2.tolist())

			inside = trackPoints.intersects(polygon)
			if inside:
				crossedAirspacesDict[i] = polygon
				#print(f"Point crosses airspace (Horizontal only): {i} # {feature.properties.CLASS} # {feature.properties.NAME} # {feature.properties.CEILING} / {feature.properties.FLOOR}" )
				airspaceCeiling = stringToMeter(feature.properties.CEILING)
				airspaceFloor = stringToMeter(feature.properties.FLOOR)
		return crossedAirspacesDict

	def __analyseData(self, crossedAirspacesDict):
		# Fixes as Points
		flightPoints = []
		for fix in self.igcFlight.fixes:
			flightPoints.append(Point(fix.lon,fix.lat))


		# Build geoPandas structures
		crs = 'epsg:4326'
		regions = gpd.GeoSeries(list(crossedAirspacesDict.values()), crs=crs, index=list(crossedAirspacesDict.keys()))
		points = gpd.GeoSeries(flightPoints, crs=crs)

		# Browse through airspaces regions to find points inside the airspace (vertically)
		infringedAirspaceIndexes = []
		for i, region in enumerate(regions):
			res = points.within(region)
			if res.any():
				# Get fixes inside the airspace
				res = res[res==True]
				insideRegionPointIndexes = res.index.values
				fixesInsideRegion = np.take(self.igcFlight.fixes, insideRegionPointIndexes)
    
				# Get airsapce floor and ceiling
				airspaceIndex = regions.index[i]
				airspace = self.geojsonAirspace.features[airspaceIndex]
				airspaceCeiling = int(stringToMeter(airspace.properties.CEILING))
				airspaceFloor = int(stringToMeter(airspace.properties.FLOOR))
	
				# Get fixes vertically inside the airspace
				fixesInsideAirspace = np.array([x for x in fixesInsideRegion if x.gnss_alt>airspaceFloor and x.gnss_alt<=airspaceCeiling])

				if fixesInsideAirspace.any():
					infringedAirspaceIndexes.append(airspaceIndex)
					print(f"Point inside airspace: {airspaceIndex} # {airspace.properties.CLASS} # {airspace.properties.NAME} # {airspace.properties.CEILING} / {airspace.properties.FLOOR} = {airspaceCeiling}m / {airspaceFloor}m" )
					print(f"Fix 1 / {fixesInsideAirspace.size} : {fixesInsideAirspace[0]}")
		# Get the geojson list of ingringed airspaces only
		infringedFeatures = np.take(self.geojsonAirspace.features, infringedAirspaceIndexes).tolist()

		# Copy and re-create 
		self.geojsonInfringedAirspace = self.geojsonAirspace # Reusing the airspace as it won't be used after that: prevents a copy
		self.geojsonInfringedAirspace.features.clear()
		self.geojsonInfringedAirspace.features.extend(infringedFeatures)

		return self.geojsonInfringedAirspace

	def run(self):
		self.__loadData()
		crosssedAirspaces = self.__findCrossedAirspaces()
		self.__analyseData(crosssedAirspaces)
	
	def runForNetcoupeFlightId(self, flightId):
		self.__loadDataForNetcoupeFlight(flightId)
		crosssedAirspaces = self.__findCrossedAirspaces()
		self.__analyseData(crosssedAirspaces)

	def runForIgcFile(self, file):
		self.__loadDataForIgcFile(file)
		crosssedAirspaces = self.__findCrossedAirspaces()
		self.__analyseData(crosssedAirspaces)

if __name__ == '__main__':
    airspaceChecker = AirspaceChecker()
    airspaceChecker.run()



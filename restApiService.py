
from datetime import datetime, date, time, timedelta
from flask_restx import abort
import zipfile
import pathlib

from werkzeug.utils import secure_filename

import os
import sys
import ftpClient
import ftplib

import common

try:
	import igc_lib
	import igc2geojson
except:
	from igc_lib import igc_lib
	from igc_lib import igc2geojson

### Constants ###
ftp_server_name_igc = os.environ['FTP_SERVER_NAME_IGC'].strip()
ftp_login_igc = os.environ['FTP_LOGIN_IGC'].strip()
ftp_password_igc = os.environ['FTP_PASSWORD_IGC'].strip()

ftp_server_name_heatmap = os.environ['FTP_SERVER_NAME_HEATMAP'].strip()
ftp_login_heatmap = os.environ['FTP_LOGIN_HEATMAP'].strip()
ftp_password_heatmap = os.environ['FTP_PASSWORD_HEATMAP'].strip()

def getNetcoupeFlight(flightId):
	flight = None
	filename = flightId + ".zip"

	ftp_client_igc = ftpClient.get_ftp_client(ftp_server_name_igc, ftp_login_igc, ftp_password_igc)
	try:
		zip = ftpClient.get_file_from_ftp(ftp_client_igc, filename)
	except ftplib.error_perm:
		error_message = f"File not found ! : {filename}"
		print(error_message)
		common.json_abort(404, {'error': error_message}) 

	with zipfile.ZipFile(zip) as zip_file:
				flight = igc_lib.Flight.create_from_zipfile(zip_file)
    
	return flight

def getFlightAsGeojson(flight):
	flight_date = datetime.fromtimestamp(flight.date_timestamp).date()
	geoJsonTrack = igc2geojson.dump_track_to_feature_collection(flight)
	return geoJsonTrack

def getNetcoupeFlightAsGeojson(flightId):
	flight = getNetcoupeFlight(flightId)
	geoJsonTrack = getFlightAsGeojson(flight)
	return geoJsonTrack

def getFlightFromIgcFile(file):
	filename = secure_filename(file.filename)
	# File is OK
	flight = igc_lib.Flight.create_from_bytesio(file)
	return flight

def getGeojsonTrackFromIgcFile(file):
	# File is OK, start computation
	flight = getFlightFromIgcFile(file)

	if  flight.valid:
		flight_date = datetime.fromtimestamp(flight.date_timestamp).date()
		geoJsonTrack = igc2geojson.dump_track_to_feature_collection(flight)
		return geoJsonTrack
	else:
		return False

def getGeoJsonFileList():
	ftpClientHeatmap = ftpClient.get_ftp_client(ftp_server_name_heatmap, ftp_login_heatmap, ftp_password_heatmap)
	file_names = []
	files = ftpClientHeatmap.mlsd(path=common.GEOJSON_FOLDER)   # List files from FTP

	for file in files:
		name = file[0]
		suffix = pathlib.Path(name).suffix.replace('.','')
		if suffix == "json":
			file_names.append(name)
	return file_names
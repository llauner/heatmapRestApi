
from datetime import datetime, date, time, timedelta
import zipfile

from werkzeug.utils import secure_filename

import os
import sys
import ftpClient
import ftplib

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

def getNetcoupeFlight(flightId):
	flight = None
	filename = flightId + ".zip"

	ftp_client_igc = ftpClient.get_ftp_client(ftp_server_name_igc, ftp_login_igc, ftp_password_igc)
	try:
		zip = ftpClient.get_file_from_ftp(ftp_client_igc, filename)
	except ftplib.error_perm:
		error_message = f"File not found ! : {filename}"
		print(error_message)
		json_abort(404, {'error': error_message}) 

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
		return false
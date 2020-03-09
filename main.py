"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
# [START gae_python37_app]
try:
  import googleclouddebugger
  googleclouddebugger.enable()
except ImportError:
  pass

from flask import Flask, jsonify, request, send_file
from flask_restx import abort
from flask_cors import CORS
from werkzeug.utils import secure_filename

from datetime import datetime, date, time, timedelta
import zipfile

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


ALLOWED_EXTENSIONS = {'igc'}             # Upload allowed file extensions
STATIC_FOLDER = "static"

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__,
			static_url_path='', 
			static_folder='static')

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

### Constants ###
ftp_server_name_igc = os.environ['FTP_SERVER_NAME_IGC'].strip()
ftp_login_igc = os.environ['FTP_LOGIN_IGC'].strip()
ftp_password_igc = os.environ['FTP_PASSWORD_IGC'].strip()

def json_abort(status_code, data=None):
	if data is None:
		data = {}
	response = jsonify(data)
	response.status_code = status_code
	abort(response)


@app.route('/')
def hello():
	return jsonify(message= "heatmapRestApi")

@app.route("/netcoupe/<flightId>")
def get_netcoupe_flight_as_geojson(flightId):
	geoJsonTrack = None
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
				flight_date = datetime.fromtimestamp(flight.date_timestamp).date()
				geoJsonTrack = igc2geojson.dump_track_to_feature_collection(flight)

	return jsonify(geoJsonTrack)

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file/igc', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		json_abort(400, {'error': "file cannot be found in request"}) 

	file = request.files['file']

	# if user does not select file, browser also submit an empty part without filename
	if file.filename == '':
		json_abort(400, {'error': "No filename in request"}) 
		 
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		
		# File is OK, start computation
		flight = igc_lib.Flight.create_from_bytesio(file)

		if  flight.valid:
			flight_date = datetime.fromtimestamp(flight.date_timestamp).date()
			geoJsonTrack = igc2geojson.dump_track_to_feature_collection(flight)
			return jsonify(geoJsonTrack)
		else:
			json_abort(400, {'error': "The IGC file is not valid"}) 
	return

@app.route('/airspace/geojson/')
def GetAirspaceAsGeojson():
	try:
		filename = os.path.join(STATIC_FOLDER, "airspace.geojson")
		return send_file(filename, mimetype='application/json')
	except Exception as e:
		json_abort(500, {'error':str(e)}) 

@app.route('/airspace/zip')
def GetAirspaceAsZip():
	try:
		filename = os.path.join(STATIC_FOLDER, "airspace.zip")
		return send_file(filename, mimetype='application/zip')
	except Exception as e:
		json_abort(500, {'error':str(e)}) 



if __name__ == '__main__':
	# This is used when running locally only. When deploying to Google App
	# Engine, a webserver process such as Gunicorn will serve the app. This
	# can be configured by adding an `entrypoint` to app.yaml.
	import os
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '5555'))
	except ValueError:
		PORT = 5555
	app.run(HOST, '8080')
# [END gae_python37_app]
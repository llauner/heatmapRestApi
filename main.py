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

from datetime import datetime, date, time, timedelta
import zipfile

import os
import sys
import ftpClient
import ftplib
import restApiService

from AirspaceChecker import AirspaceChecker
import common

try:
	import igc_lib
	import igc2geojson
except:
	from igc_lib import igc_lib
	from igc_lib import igc2geojson


ALLOWED_EXTENSIONS = {'igc'}             # Upload allowed file extensions

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__,
			static_url_path='', 
			static_folder='static')

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

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
	geoJsonTrack = restApiService.getNetcoupeFlight(flightId)
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
		geoJsonTrack = restApiService.getGeojsonTrackFromIgcFile(file)
		if geoJsonTrack:
			return jsonify(geoJsonTrack)
		else:
			json_abort(400, {'error': "The IGC file is not valid"}) 
	return

@app.route('/airspace/geojson/')
def GetAirspaceAsGeojson():
	try:
		filename = common.getAirspaceFullFilename()
		return send_file(filename, mimetype='application/json')
	except Exception as e:
		json_abort(500, {'error':str(e)}) 

@app.route('/airspace/zip')
def GetAirspaceAsZip():
	try:
		filename = os.path.join(common.STATIC_FOLDER, "airspace.zip")
		return send_file(filename, mimetype='application/zip')
	except Exception as e:
		json_abort(500, {'error':str(e)}) 

@app.route('/airspace/test')
def GetAirspaceInfringement():
    airspaceChecker = AirspaceChecker()
    airspaceChecker.run()
    return jsonify(airspaceChecker.geojsonInfringedAirspace)
    
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
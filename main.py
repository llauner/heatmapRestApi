"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
# [START gae_python37_app]
# try:
# 	import googleclouddebugger
# 	googleclouddebugger.enable()
# except ImportError:
# 	pass

from flask import Flask, jsonify, request, send_file
from flask_restx import abort
from flask_cors import CORS
from flask.json import JSONEncoder
from flaskthreads import AppContextThread

from datetime import datetime, date, time, timedelta

import os
import sys
import restApiService

from AirspaceChecker import AirspaceChecker
import common

try:
	import igc_lib
	import igc2geojson
	import FtpHelper
	import RunMetadata as rmd
	from FtpHelper import FtpHelper
except:
	from igc_lib import igc_lib, FtpHelper
	from igc_lib import RunMetadata as rmd
	from igc_lib import igc2geojson

# ********** Custom Json encoder class **********
class CustomEncoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, rmd.RunMetadata):
			return o.to_json()
		return JSONEncoder.default(self, o)
# ***********************************************

IS_DEBUG = True if os.environ.get('DEBUG') is not None else False

ALLOWED_EXTENSIONS = {'igc'}             # Upload allowed file extensions
API_KEY_PARAMETER = 'x_api_key'
API_KEY_PARAMETER_HEADER = 'x-api-key'

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__,
			static_url_path='', 
			static_folder='static')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.json_encoder = CustomEncoder
cors = CORS(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@app.route('/')
def hello():
	return jsonify(message= "heatmapRestApi")

@app.route("/netcoupe/<flightId>")
def get_netcoupe_flight_as_geojson(flightId):
	geoJsonTrack = restApiService.getNetcoupeFlightAsGeojson(flightId)
	return jsonify(geoJsonTrack)

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def __checkFile():
	# check if the post request has the file part
	if 'file' not in request.files:
		common.json_abort(400, {'error': "file cannot be found in request"}) 

	file = request.files['file']

	# if user does not select file, browser also submit an empty part without filename
	if file.filename == '':
		common.json_abort(400, {'error': "No filename in request"})

	if not file or not allowed_file(file.filename):
		common.json_abort(400, {'error': "The IGC file is not valid"}) 

	return file
	
@app.route('/file/igc', methods=['POST'])
def upload_file():
	file = __checkFile()
	geoJsonTrack = restApiService.getGeojsonTrackFromIgcFile(file)
	if geoJsonTrack:
		return jsonify(geoJsonTrack)
	return

@app.route('/airspace/geojson/')
def GetAirspaceAsGeojson():
	try:
		filename = common.getAirspaceFullFilename()
		return send_file(filename, mimetype='application/json')
	except Exception as e:
		common.json_abort(500, {'error':str(e)}) 

@app.route('/airspace/zip')
def GetAirspaceAsZip():
	try:
		filename = os.path.join(common.STATIC_FOLDER, "airspace.zip")
		return send_file(filename, mimetype='application/zip')
	except Exception as e:
		common.json_abort(500, {'error':str(e)}) 

#@app.route('/json/files')
#def GetJsonFileList():
#	try:
#		fileList = restApiService.getGeoJsonFileList()
#		return jsonify(jsonFileList = fileList)
#	except Exception as e:
#		common.json_abort(500, {'error':str(e)})

def serialize(obj):
	"""JSON serializer for objects not serializable by default json code"""

	if isinstance(obj, rmd.RunMetadata):
		serial = obj.toJSON()
		return serial
	return obj.__dict__

	
# --------------------------------- Authorized functionalities ---------------------------------
def __checkAuthorization(submittedApiKey=None):
	apiKey = None
	# Check api-key in header
	if submittedApiKey:
		apiKey = submittedApiKey
	else:
		apiKey = request.headers.get(API_KEY_PARAMETER_HEADER)
	expectedApiKey = os.environ['API_KEY'].strip()
	
	if not apiKey:
		common.json_abort(401, {'error': f"Missing header: {API_KEY_PARAMETER_HEADER}"}) 
	elif not apiKey == expectedApiKey:
		common.json_abort(401, {'error': f"Invalid credentials !"}) 

@app.route('/auth', methods=['POST'])
def Authenticate():
	# Check params
	if not request.is_json:
		common.json_abort(401, {'error': "expecting json input"})
	params = request.get_json(force=True)
	apiKey = params.get(API_KEY_PARAMETER)
	if not apiKey:
		common.json_abort(400, {'error': f"Missing json value: {API_KEY_PARAMETER}"}) 
	# Check Authorization
	__checkAuthorization(apiKey)
	response = {'message': "Authentication success: api-key OK !"}
	return jsonify(response)

@app.route('/airspace/netcoupe/<flightId>')
def GetAirspaceInfringementForNetcoupe(flightId):
	__checkAuthorization() # Check api-key in header
	
	# Check airspace
	airspaceChecker = AirspaceChecker(IS_DEBUG)
	airspaceChecker.runForNetcoupeFlightId(flightId)
	
	# Build response
	response = airspaceChecker.geojsonInfringedAirspace
	return jsonify(response)

@app.route('/airspace/file/igc', methods=['POST'])
def GetAirspaceInfringementForIgcFile():
	__checkAuthorization() # Check api-key in header
	
	file = __checkFile()
	# Check airspace
	airspaceChecker = AirspaceChecker(IS_DEBUG)
	airspaceChecker.runForIgcFile(file)
	
	# Build response
	response = airspaceChecker.airspaceAnalysisResult
	return jsonify(response)
	

# ---------------------------------------------------------------------------------------------- 
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
	app.run(HOST, '8080', debug=IS_DEBUG)
# [END gae_python37_app]
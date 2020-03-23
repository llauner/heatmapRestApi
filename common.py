import os
from flask import Flask, jsonify, request, send_file
from flask_restx import abort

STATIC_FOLDER = "static"
AIRSPACE_FILENAME = "airspace.geojson"

def getAirspaceFullFilename():
    return os.path.join(STATIC_FOLDER, AIRSPACE_FILENAME)

def json_abort(status_code, data=None):
	if data is None:
		data = {}
	response = jsonify(data)
	response.status_code = status_code
	abort(response)
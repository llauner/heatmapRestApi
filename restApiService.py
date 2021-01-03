
from datetime import datetime, date, time, timedelta
from io import DEFAULT_BUFFER_SIZE
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

from StorageService import StorageService


def getNetcoupeFlight(flightId):
    flight = None
    filename = f"NetCoupe{datetime.now().year}_{flightId}.igc"
    filename_last_year = f"NetCoupe{datetime.now().year - 1}_{flightId}.igc"

    storageService = StorageService(None)
    bucket_name, fullFilePath = storageService.GetFileFullpathFromName(filename, filename_last_year)

    if (fullFilePath is None):
        common.json_abort(404, {'error': f"Cannot find flight: {flightId}"})

    file_as_bytesio = storageService.GetFileAsStringFromBucket(bucket_name, fullFilePath)

    flight = igc_lib.Flight.create_from_bytesio(file_as_bytesio)
    file_as_bytesio.close
    del file_as_bytesio

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

    if flight.valid:
        flight_date = datetime.fromtimestamp(flight.date_timestamp).date()
        geoJsonTrack = igc2geojson.dump_track_to_feature_collection(flight)
        return geoJsonTrack
    else:
        return False


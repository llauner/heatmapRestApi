import os

STATIC_FOLDER = "static"
AIRSPACE_FILENAME = "airspace.geojson"

def getAirspaceFullFilename():
    return os.path.join(STATIC_FOLDER, AIRSPACE_FILENAME)
import re

def feetToMeter(f):
    return f * 0.3048

def stringTofeet(altitude):
    altFeet=0.0
    # Ground
    if altitude == 'GND':
        altFeet = 0.0
    # F MSL
    elif re.search('F MSL', altitude, re.IGNORECASE):
        alt = re.sub(r"\D", "", altitude)
        altFeet = float(alt)
    # F GND
    elif re.search('F GND', altitude, re.IGNORECASE):
        # HACK: This is not correct, but I don't have GND elevation right now...so assuming elevation=0
        alt = re.sub(r"\D", "", altitude)
        altFeet = float(alt)
    # FL
    elif re.search('FL', altitude, re.IGNORECASE):
        fl = re.sub(r"\D", "", altitude)
        altFeet = float(fl)*100
    
    return float(altFeet)

def stringToMeter(stringAltitude):
    feet = stringTofeet(stringAltitude)
    meter = feetToMeter(feet)
    return meter
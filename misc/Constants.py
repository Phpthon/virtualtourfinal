import math
import json

MAIN_FONT = "Lucida Sans"
FONT_REGULAR = "assets/font/lsans.ttf"
FONT_BOLD = "assets/font/lsans_b.ttf"
SOFTWARE_VERSION = "v1.01"

LEVEL_MAIN_MENU = 0
LEVEL_GAME = 1

# constant arrays used for distance calculations
angles = [0, 90, 180, 270, 360]
azimuth = [0, 180, 180, 360]
direct = ["ne", "se", "sw", "nw"]
xvals = [1, 1, -1, -1]
yvals = [-1, 1, 1, -1]

# convert degrees to radians
def radians(degrees):
	return math.radians(degrees)

# convert radians to degrees
def degrees(radians):
	return math.degrees(radians)

# convert a bearing to its angle (degrees, radians, x direction, y direction, compass direction)
def bearing_conversion(bearing, velocity):
	for i in range(0, len(angles)+1):
		if bearing >= angles[i] and bearing <= angles[i+1]:
			angle = abs(bearing - azimuth[i])
			xdir = xvals[i] * velocity * math.sin(radians(angle))
			ydir = yvals[i] * velocity * math.cos(radians(angle))
			return (angle, radians(angle), xdir, ydir, direct[i])

# open the json settings and make the data available in a global variable
json_file = open("assets/settings.json")
json_settings = json.load(json_file)
json_file.close()
SERVER_URL = 'http://192.168.1.11:5000/caption'

AUDIOPLAYER = 'mpg321 -q'

#####################################
# PiCamera
####################################

# Image resolution
resolution = {'width' : 1024, 'height': 768} # Max = {'width' : 2592, 'height': 1944}

#Output directory for the audio
output_dir = "./"

# The interval between captures (in seconds).
interval = 5 # in seconds

########################################
# Camera Advanced stuff
########################################

# ISO value. 0 = auto, 60-800 for manual ISO.
# iso = 0
iso = None

# Shutter speed. 0 = auto, else value in microseconds (seconds * 1000000).
# shutter_speed = 0
shutter_speed = None

# White balance. Uncomment to use the values, else auto white balance will be selected.
# white_balance = {red_gain: 1.3, blue_gain: 1.75}
# red_gain: 1.3
# blue_gain: 1.75
white_balance = None

# Rotate the images taken by the camera. Possible value are 0, 90, 180 or 270
# rotation = 0
rotation = None
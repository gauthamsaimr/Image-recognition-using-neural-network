from flask import Flask, request, jsonify, render_template, send_file, make_response
from picamera import PiCamera
from pi_config import *
from gtts import gTTS
from tts_cache import cache_say as tts_cache
from datetime import datetime

import io, os, base64

def set_camera_options(camera):
    # Set camera resolution.
    if resolution:
        camera.resolution = (
            resolution['width'],
            resolution['height']
        )

    # Set ISO.
    if iso:
        camera.iso = iso

    # Set shutter speed.
    if shutter_speed:
        camera.shutter_speed = shutter_speed
        # Sleep to allow the shutter speed to take effect correctly.
        sleep(1)
        camera.exposure_mode = 'off'

    # Set white balance.
    if white_balance:
        camera.awb_mode = 'off'
        camera.awb_gains = (
            white_balance['red_gain'],
            white_balance['blue_gain']
        )

    # Set camera rotation
    if rotation:
        camera.rotation = rotatino

    if brightness:
        camera.brightness = brightness

    return camera


def capture_b64(camera, stream):
    camera.capture(stream, 'jpeg')
    stream.seek(0, 0)
    enc =  base64.b64encode(stream.read())
    stream.seek(0, 0)
    stream.truncate()
    return enc

def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)
    return filename


def play_audio(filename):
    """
    Create a subprocess to play the audio.
    """
    os.system(AUDIOPLAYER + ' ' + filename)

####################################################################################################

# Initialize the Flask application
app = Flask(__name__)
# CORS(app) # allow everything by default

camera = PiCamera()

set_camera_options(camera)
img_stream = io.BytesIO() # Capture Image Stream


@app.route('/')
def index():
    return render_template('index.html')

# HTTP Errors handlers
@app.errorhandler(404)
def url_error(e):
    return """
    Error resource not found. Check the URL.
    <pre>{}</pre>""".format(e), 404


@app.errorhandler(500)
def server_error(e):
    return """
    An internal server error occurred: <pre>{}</pre>
    Check the logs (if any?) for issues.
    """.format(e), 500

# Captions
@app.route('/getimage_camera', methods=['GET'])
def getimage_camera():
    """
    """
    r = make_response(capture_b64(camera, img_stream))
    r.headers.add('Access-Control-Allow-Origin', '*')
    return r

# Captions
@app.route('/tts', methods=['POST'])
def tts():
    text = request.form['text']
    cur_file = os.path.join(output_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".mp3")
    text_to_speech(text, cur_file)
    play_audio(cur_file)
    os.remove(cur_file)
    return ('', 204)

# Captions
@app.route('/tts_offline', methods=['POST'])
def tts_offline():
    text = request.form['text']
    cur_file = os.path.join(output_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".mp3")
    tts_cache(text, cur_file)
    play_audio(cur_file)
    os.remove(cur_file)
    return ('', 204)

app.run(host="0.0.0.0", port=8080, debug=False)

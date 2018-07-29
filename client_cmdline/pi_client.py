import requests
from picamera import PiCamera
from time import sleep
import os
from pi_config import *
from datetime import datetime
import io
from gtts import gTTS

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
        camera.rotation = rotation

    return camera


def post_image(img_stream):
    """ Post image and return the Caption"""
    try:
        files = {'image': img_stream.getvalue()}
        r = requests.post(SERVER_URL, files=files)

        response = r.json()
        if response['success'] == 'True':
            print('Caption returned successfully: {}'.format(response['caption']))
            return response['caption']
    except:
        print("Caption Generation failed.")


    return "Error in caption generation."

def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)
    return filename

def play_audio(filename):
    """
    Create a subprocess to play the audio.
    """
    os.system(AUDIOPLAYER + ' ' + filename)

if __name__ == '__main__':
    print("Started Pi Client for capturing frames with options:")
    print("Resolution: [width: {}, height: {}]".format(resolution['width'], resolution['height']))
    print("Output Directory : {}".format(output_dir))
    print("Interval in secs: {}".format(interval))

    print("\nISO: {}".format(iso))
    print("Shutter Speed: {}".format(shutter_speed))
    print("White Balance: {}".format(white_balance))
    print("Rotation: {}".format(rotation))

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    with PiCamera() as camera:
        set_camera_options(camera)

        current_image = 0
        stream = io.BytesIO() # Capture Image Stream

        while True:
            print('Capturing next image {} to stream'.format(current_image))

            camera.capture(stream, 'jpeg')

            stream.seek(0, 0)
            caption = post_image(stream)
            stream.seek(0, 0)
            stream.truncate()

            cur_file = os.path.join(output_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".mp3")
            text_to_speech(caption, cur_file)
            play_audio(cur_file)
            os.remove(cur_file)

            current_image += 1
            sleep(interval)

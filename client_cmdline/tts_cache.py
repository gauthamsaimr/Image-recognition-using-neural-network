#!/usr/bin/python3

import sys, os
from gtts import gTTS
from pydub import AudioSegment
import sys
import string
from tts_cache_parallel import start_cache_word
from pi_config import AUDIOPLAYER

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
table = str.maketrans('','',string.punctuation)

# sets crossfade between words, for some amount of 'smoothing'
crossfade_amount = 40
# sets fade_in/out amount, for less abruptness also
fade_amount = 30
# Show nothing (0), Show a count (1), Show each new word (2) we had to get from Google
verbose = 2

# Output File
OUTPUT_FILE = "tts.mp3"


def detect_leading_silence(sound, silence_threshold=-33.0, chunk_size=1):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def old_cache_word(word):
    if os.path.exists(str('cache/' + word + '.mp3')) and (word != ' ') and (word != ''):
        return ('cached')
    if verbose == 2: print("downloaded:" + word)

    tts = gTTS(text=str(word), lang='en')
    tts.save(str("cache/" + word + ".mp3"))
    # strip leading and trailing silences, right here, right now.
    sound = AudioSegment.from_file('cache/' + word + '.mp3', format='mp3')
    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())
    duration = len(sound)
    trimmed_sound = sound[start_trim:duration - end_trim]
    trimmed_sound.export('cache/' + word + '.mp3', format="mp3")


def remove_punctuation(text):
    return text.translate(table)


def cache_say(sentence, out=None):

    if out is None: out = OUTPUT_FILE
    
    sentence = remove_punctuation(sentence)
    sentence = sentence.split(" ")
    sentence = list(filter(None, sentence))
    for i in range(len(sentence)):
        sentence[i] = sentence[i].replace("\n", "")


    start_cache_word(sentence)

    for i in sentence:
        j = 'cache/' + i + '.mp3'
        if os.path.exists(j):
            tmp = AudioSegment.from_mp3(j)
            new = tmp
            try:
                complete = complete.append(new.fade_in(fade_amount).fade_out(fade_amount), crossfade=crossfade_amount)
            except:
                complete = new
                continue

    if os.path.exists(out): os.remove(out)
    complete.export(out, format="mp3")
    return out


### main drag
if __name__ == "__main__":
    r = sys.argv[1].split("\n")
    r = list(filter(None, r))
    for i in r:
        j = i.split(".")
        j = list(filter(None, j))
        for k in j:
            cache_say(k)

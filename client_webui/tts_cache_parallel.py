import os, sys
import multiprocessing as mp
from queue import Queue
from threading import Thread
from pydub import AudioSegment
import unicodedata
from gtts import gTTS

# quiet the endless 'insecurerequest' warning
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

verbose = 2

def worker(queue, run):
    """Process files from the queue."""
    for args in iter(queue.get, None):
        try:
            run(*args)
        except Exception as e: # catch exceptions to avoid exiting the thread prematurely
            print('{} failed: {}'.format(args, e))


def start_processes_in_parallel(queue, func, number_of_process=None):
    """
        Starts threads to run the function with processes in parallel
        :param queue: Queue of tasks i.e. files to process, also the arguments to run()
        :param number_of_process: If none is provided, the total number of CPU Cores - 1 is taken.
        :return: Nothing is returned.
    """
    if not number_of_process:
        number_of_process = mp.cpu_count() - 1

        # start threads
    threads = [Thread(target=worker, args=(queue, func)) for _ in range(number_of_process)]

    # print("Created {} threads. Running now.".format(len(threads)))
    for t in threads:
        t.daemon = True  # threads die if the program dies
        t.start()
    for _ in threads: queue.put_nowait(None)  # signal no more files
    for t in threads: t.join()  # wait for completion

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

def cache_word(word):
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

def start_cache_word(words, num_proc=None):
    q = Queue()
    for word in words:
        q.put_nowait(([word]))

    num_proc = num_proc if num_proc is not None else mp.cpu_count()
    if len(words) < num_proc:
        num_proc = len(words)

    start_processes_in_parallel(q, cache_word, num_proc)

if __name__ == '__main__':
    words = [line.rstrip() for line in open(sys.argv[1])]
    q = Queue()
    for word in words:
        q.put_nowait(([word]))

    start_processes_in_parallel(q, cache_word, mp.cpu_count())

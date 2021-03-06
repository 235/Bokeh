
import flask
import json
import os
from os.path import join
import sys
import time
import hemlib

app = flask.Flask(__name__)


import pyaudio
from numpy import zeros, linspace, short, fromstring, hstack, transpose
from scipy import fft


HOST = "localhost"
PORT = 9294


NUM_SAMPLES = 1024
SAMPLING_RATE = 44100
MAX_FREQ = SAMPLING_RATE / 8
FREQ_SAMPLES = NUM_SAMPLES / 8
SPECTROGRAM_LENGTH = 400

# Maximum time we want to spend polling the microphone for a single request
MAX_REQ_TIME = 0.05


_stream = None
def get_audio_data():
    global _stream
    if _stream is None:
        pa = pyaudio.PyAudio()
        _stream = pa.open(format=pyaudio.paInt16, channels=1, rate=SAMPLING_RATE,
                     input=True, frames_per_buffer=NUM_SAMPLES)
    try:
        audio_data  = fromstring(_stream.read(NUM_SAMPLES), dtype=short)
        normalized_data = audio_data / 32768.0
        return (abs(fft(normalized_data))[:NUM_SAMPLES/2], normalized_data)
    except:
        return None

# def onTimer(self, *args):
#     spectrum, time = get_audio_data()
#     self.spectrum_data.set_data('amplitude', spectrum)
#     self.time_data.set_data('amplitude', time)
#     spectrogram_data = self.spectrogram_plotdata.get_data('imagedata')
#     spectrogram_data = hstack((spectrogram_data[:,1:],
#                                transpose([spectrum])))

#SRCDIR = "../../static/coffee"
SRCDIR = "static/bokehjs_static/coffee"
EXAMPLE_SRCDIR = "static/coffee"
EXCLUDES = [join(SRCDIR,"demo"), join(SRCDIR,"unittest"),
            join(SRCDIR,"unittest/primitives")]

@app.route("/")
def root():
    """ Returns the spectrogram of audio data served from /data
    """
    app.debug = True
    if app.debug:
        with open("slug.json") as f:
            slug = json.load(f)
        jslibs = hemlib.slug_libs(app, slug['libs'])
        hemfiles = hemlib.coffee_assets(SRCDIR, HOST, PORT,
                                        excludes=EXCLUDES)

    else:
        jslibs = ['/static/js/demo/application.js']
        hemfiles = []
    print "soundserver hemfiles", hemfiles
    #demofiles = [os.path.join(EXAMPLE_SRCDIR,".coffee") for name in demos]
    demofiles = ["static/coffee/spectrogram.coffee"]

    for demo in demofiles:
        if not os.path.isfile(demo):
            raise RuntimeError("Cannot find demo named '%s'"%demo)

    hemfiles.extend(hemlib.make_urls(demofiles, HOST, PORT))

    return flask.render_template("spectrogram.html", jslibs = jslibs,
                                 hemfiles=hemfiles, demos="basdf")

    #return flask.render_template("spectrogram.html")

@app.route("/data")
def data():
    """ Returns the current audio data sample as a JSON list of two
    arrays of floating-point values: (fft values, audio sample values)
    """
    data = None
    starttime = time.time()
    while time.time() - starttime < MAX_REQ_TIME:
        data = get_audio_data()
        if data is not None:
            break
    if data is None:
        return json.dumps({})
    else:
        return json.dumps([data[0].tolist(), data[1].tolist()])

def main():
    """ Starts the sound server, which retains the audio data inside
    its process space, and forks out workers when web connections are
    made.
    """
    app.debug = True
    app.run()

if __name__ == "__main__":
    main()

# FFMPEG example of Blocking Mode Audio I/O

"""PyAudio Example: Play a wave file."""
import subprocess
import json
import shlex
import pprint
import os
import pyaudio
import sys
from time import sleep

CHUNK = 1024

# if len(sys.argv) < 2:
#     print("Plays an audio file.\n\nUsage: %s filename.wav" % sys.argv[0])
#     sys.exit(-1)

song = subprocess.Popen(["ffmpeg.exe", "-i", "C:\\Users\\code\\Music\\Beka Flavour - Sikinai (Official Audio).mp3", "-loglevel", "panic", "-vn", "-f", "s16le", "pipe:1"],
                        stdout=subprocess.PIPE)

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2)
stream = p.open(format=pyaudio.paInt16,
                channels=2,         # get this from the file beforehand
                rate=48000,         # get this from the file beforehand
                output=True)

# read data
data = song.stdout.read(CHUNK)

# play stream (3)
while len(data) > 0:
    # sleep(1)
    stream.write(data)
    data = song.stdout.read(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()
# close PyAudio (5)
p.terminate()
"""


def get_metadata(path):
    f, ext = os.path.splitext(path)
    result = subprocess.Popen(
        ["ffprobe.exe", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # dur = subprocess.check_output(["ffprobe.exe", "-i", path, "-show_entries",
    #                                    "format=Channels", "-v", "quiet", "-of", "csv=%s" % ("p=0")])
    cmd = "ffprobe.exe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(path)
    getout = subprocess.check_output(args).decode("utf-8")
    out = json.loads(getout)
    # pprint.pprint(out)
    # # print(dur)
    try:
        mins, secs = divmod(round(float(out["streams"][0]["duration"])), 60)
        durat = f"{mins:02}:{secs:02}"
        return durat, out["streams"][0]["channels"], out["streams"][0]["sample_rate"]
    except KeyError:

        values = []
        for x in result.stdout.readlines():

            if b"Hz" in x:
                r = x.decode("utf-8").split(",")
                x = [i for i in r if i.endswith("Hz") and i.startswith(" 4")]
                if " stereo" in r:
                    values.append(2)
                else:
                    c = r[2].strip()
                    try:
                        c = float(c)
                        values.append(c)
                    except Exception as e:
                        values.append(1)
                sample_rate = x[0].strip()[:5]
                values.append(sample_rate)
            if b"Duration" in x:
                r = x.decode("utf-8").split(",")
                d = [i for i in r if i.startswith("  Duration")]
                if int(d[0].strip()[19]) >= 5:
                    lst = int(d[0].strip()[16:18])
                    lst += 1
                    duration = f"{d[0].strip()[13:16]}{lst}"
                else:
                    duration = d[0].strip()[13:18]
                values.append(duration)
    return values


print(get_metadata(
    "C:\\Users\\code\\Music\\Tuliza Nyavu- Susumila, Kaa La Moto, Vivonce & King Kaka.mp3"))"""


from pydub import AudioSegment
from pydub.utils import make_chunks
import os
from simpleaudio import play_buffer
from time import perf_counter
ALL_FILES = [i for i in os.scandir("C:\\Users\\code\\Music") if i.is_file]


def play_file(starttime=0):
    s = perf_counter()
    # f = ALL_FILES[7].path
    # f = "C:\\Users\\code\\Videos\\(Tubidy.io)TIP TOE Remix ft Rayvanny.mp4"
    f = "C:\\Users\\code\\Music\\G Nako ft. Maua Sama - Gusanisha Official Video.mp3"
    fmt = os.path.splitext(f)[1].strip(".")
    seg = AudioSegment.from_file(f, format=fmt)[starttime * 1000:]
    print()
    # play(seg)

    playback = play_buffer(seg.raw_data,
                           num_channels=seg.channels,
                           bytes_per_sample=seg.sample_width,
                           sample_rate=seg.frame_rate)
    print(perf_counter() - s)
    # playback.wait_done()


play_file(starttime=0)

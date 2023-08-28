
from simpleaudio import play_buffer
from pydub import AudioSegment
import os


def a_play(f, starttime=0):

    fmt = os.path.splitext(f)[1].strip(".")
    seg = AudioSegment.from_file(f, format=fmt)[starttime * 1000:]
    playback = play_buffer(seg.raw_data,
                           num_channels=seg.channels,
                           bytes_per_sample=seg.sample_width,
                           sample_rate=seg.frame_rate)
    playback.wait_done()
    print(playback.is_playing())


# a_play("C:\\Users\\code\\Music\\DJ Labans Intro.mp3")


def initializer(p):
    all_files = {}
    for i in os.scandir(p):
        f = i.path
        fmt = os.path.splitext(f)[1].strip(".")
        if i.is_file:
            try:
                all_files[f] = AudioSegment.from_file(f, format=fmt)
            except Exception:
                pass
    print(all_files)


#initializer(
#    "C:\\Users\\code\\Music\\Jack U - Skrillex And Diplo Present Jack U [2015]")

from moviepy.editor import VideoFileClip


def convert(src, dst):
    """ extract audio from videos `src` to `dst` """
    with VideoFileClip(src) as video:
        video.audio.write_audiofile(dst)

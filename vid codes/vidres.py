from moviepy.editor import VideoFileClip
from os.path import abspath, dirname, splitext, join, isfile, exists

base_dir = dirname(abspath(__file__))


def res(filename: str, height: int, output=None):
    """ resize video to `height` (width is computed automatically) """
    # take care of file refs
    cwd = dirname(filename) or base_dir
    name, ext = splitext(filename)
    new_name = f"{name}_{height}P{ext}"

    if output is None:
        output = join(cwd, new_name)
    elif isfile(output) and exists(output):
        output = join(dirname(output), new_name)
        print("Warning: `output` should be a folder.")

    # get the video
    try:
        print("Output:", output)
        clip = VideoFileClip(filename)
        resized = clip.resize(height=height)
        resized.write_videofile(output)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    res(r"C:\Users\code\Downloads\LATEST POP HITS VIDEO MIX 2021 _ DJ BASHFUL [SHAWN MENDES, TAYLOR SWIFT, ED SHEERAN, KHALID].mp4", 480, output=r"C:\Users\code\Downloads\resized.mp4")

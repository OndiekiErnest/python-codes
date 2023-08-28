from moviepy.editor import VideoFileClip
import os


def convert(src, dst_folder):
    """ extract audio from video `src` to `dst_folder` """
    if os.path.isfile(dst_folder):
        dst_folder = os.path.dirname(dst_folder)
        print("Destination must be a folder, using ->", dst_folder)
    if not os.path.exists(dst_folder):
        try:
            # create folder if it does not exist
            os.mkdir(dst_folder)

        except PermissionError as e:
            print("Destination could not be created:", e)
    # do nothing if src or dst_folder file does not exist
    if os.path.exists(src) and os.path.exists(dst_folder):
        try:
            # use the same filename, change extension only
            file = f"{os.path.splitext(os.path.basename(src))[0]}.mp3"
            # make a complete file path
            output_path = os.path.join(dst_folder, file)
            with VideoFileClip(src) as video:
                video.audio.write_audiofile(output_path)

        except Exception as e:
            print(e)
    print("Source or destination not found!")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        convert(sys.argv[1], sys.argv[2])
    else:
        print("USAGE: vid2audio.py `src` `dst_folder`")

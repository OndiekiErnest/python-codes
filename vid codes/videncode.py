"""Video conversion tools"""

import os
from ffmpeg_progress_yield import (
    FfmpegProgress,
)


def remove_file(filename: str):
    """send file to trash"""
    try:
        os.remove(filename)
    except Exception:
        pass


def run_ffmpeg(cmd: list, name: str) -> bool:
    """run ffmpeg with progress"""
    ffmpeg = FfmpegProgress(cmd)
    try:
        for progress in ffmpeg.run_command_with_progress():
            to_print = f"{name}: {progress}%"
            print(to_print, end="\r")
        print(f"{name}: completed")
        return True
    except Exception as e:
        print("Error:", e)
        try:
            ffmpeg.quit_gracefully()
        except RuntimeError:
            pass
        return False


def mkv_mp4(filename: str, output_folder: str = None):
    """
    convert mkv to mp4 video
    CAUTION:
        it will lose the subtitles and other audio files if present
    """
    name = os.path.basename(filename)
    if output_folder is None:
        stem, ext = os.path.splitext(filename)
        output = f"{stem}.mp4"
    else:
        name, ext = os.path.splitext(name)
        output = os.path.join(output_folder, f"{name}.mp4")

    if not os.path.exists(output):
        cmd = [
            "ffmpeg",
            "-i", filename,
            "-c:v", "copy",
            output,
        ]
        if run_ffmpeg(cmd, name):
            remove_file(filename)
    else:
        print(f"{name}: exists")


def reencode_mkv(filename: str, vc="h264", output_folder: str = None):
    """re-encode mkv video using codec `vc`"""
    postfix = "_re-encoded"
    name = os.path.basename(filename)
    name, ext = os.path.splitext(name)

    if output_folder is None:
        stem, ext = os.path.splitext(filename)
        output = f"{stem}{postfix}{ext}"
    else:
        output = os.path.join(output_folder, f"{name}{postfix}{ext}")

    if not (os.path.exists(output) or name.endswith(postfix)):
        cmd = [
            "ffmpeg",
            "-i", filename,
            "-c:v", vc,
            output,
        ]
        if run_ffmpeg(cmd, name):
            remove_file(filename)
    else:
        print(f"{name}: exists")


if __name__ == '__main__':
    files = [
    ]
    for file in files:
        reencode_mkv(file)

    # for entry in os.scandir(r"."):
    #    reencode_mkv(entry.path)

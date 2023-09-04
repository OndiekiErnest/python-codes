from moviepy.editor import AudioFileClip, VideoFileClip
from os.path import splitext


def audio_to_mp3(filename: str):
    path, ext = splitext(filename)
    output = f"{path}.mp3"

    if ext.lower() != ".mp3":
        audio = AudioFileClip(filename)
        audio.write_audiofile(output)


def video_to_mp4(filename: str):
    path, ext = splitext(filename)
    output = f"{path}.mp4"

    if ext.lower() != ".mp4":
        video = VideoFileClip(filename)
        video.write_videofile(output, threads=2)


if __name__ == '__main__':
    audio_to_mp3(r"C:\Users\Windows 10 Pro\Music\ERNESTO\Macvoice Ft Rayvanny - Tamu (Official Video).m4a")

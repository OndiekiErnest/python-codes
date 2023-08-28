__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"


from winsound import Beep
import os
from random import choice
from subprocess import Popen


def start(path):
    # os.listdir lists all the files in the specified folder
    # necessary if you're looking for specific file extensions
    content = [file for file in os.listdir(
        path) if file.endswith(('.m4a', '.mp3'))]
    # choose a random file from the list of files in content
    file = choice(content)

    # you can get the file by index, content[number]
    # file = content[0]

    # format the song path
    song = os.path.join(path, file)
    # this beep is just for notification, not necessary
    Beep(3000, 200)

    # open the filename with the default app, probably slower
    # os.startfile(song)

    # open the filename with a specific app, probably faster
    Popen(
        ['C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe',
         '%s' % song]
    )
    # get done with one file completely, avoid repeating it
    content.remove(file)


if __name__ == '__main__':
    # replace Music with; Downloads, Documents, Videos, Desktop
    # music_folder = os.path.expanduser("~\\Music")
    # start(music_folder)

    # or just pass full path to the function like
    start("C:\\Users\\code\\Music")
